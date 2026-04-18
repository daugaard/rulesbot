import importlib
import sys
from functools import lru_cache

from django.conf import settings
from django.core.files.base import ContentFile
from langchain_community.embeddings.fake import DeterministicFakeEmbedding
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings

EMBEDDING_LENGTH = 1536

LEGACY_LANGCHAIN_MODULE_ALIASES = [
    # Compatibility aliases for FAISS blobs serialized before the LangChain 1.x migration.
    # Once all persisted indexes have been rebuilt on 1.x, this alias map can be removed.
    ("langchain.docstore", "langchain_classic.docstore"),
    ("langchain.docstore.base", "langchain_classic.docstore.base"),
    ("langchain.docstore.document", "langchain_classic.docstore.document"),
    ("langchain.docstore.in_memory", "langchain_classic.docstore.in_memory"),
    ("langchain.schema", "langchain_classic.schema"),
    ("langchain.schema.document", "langchain_classic.schema.document"),
]

DEFAULT_EMBEDDING = (
    DeterministicFakeEmbedding(size=1536) if settings.TESTING else OpenAIEmbeddings()
)


class GameVectorStore:
    """
    A vector store for a specific game.

    This vector store will have all the game documents loaded and stored along side the game record in the database.
    """

    @lru_cache(maxsize=5)  # TODO: Understand memory implications of doing this
    def __init__(self, game, embedding=None):
        self.game = game

        if embedding is None:
            embedding = DEFAULT_EMBEDDING
        self.embedding = embedding
        self.game = game
        self.index = self._try_load_index()

    def add_documents(self, documents, document_id):
        """
        Add documents to the vector store

        Note:
            Document is a an overloaded terms here. Documents represents the sections of a document as a langchain Document.
            document_id referes to the document_id of the game document the sections belong to.
        """
        for document in documents:
            document.metadata["game_id"] = self.game.id
            document.metadata["document_id"] = document_id

        if self.index is not None:
            self.index.add_documents(documents)
        else:
            self.index = FAISS.from_documents(
                documents=documents,
                embedding=self.embedding,
            )
        self._persist_index()

    def clear(self):
        """
        Clear the vector store
        """
        if self.game.faiss_file is not None:
            self.game.faiss_file.delete()
        self.index = None

    def _try_load_index(self):
        """
        If the index exists, load it. Otherwise return None
        """
        try:
            self.game.faiss_file.open("rb")
            try:
                data = self.game.faiss_file.read()
            finally:
                self.game.faiss_file.close()

            self._register_legacy_langchain_module_aliases()

            try:
                return FAISS.deserialize_from_bytes(
                    data,
                    self.embedding,
                    allow_dangerous_deserialization=True,
                )
            except ModuleNotFoundError as e:
                if self._register_legacy_langchain_module_alias(e.name):
                    return FAISS.deserialize_from_bytes(
                        data,
                        self.embedding,
                        allow_dangerous_deserialization=True,
                    )
                raise
        except ValueError as e:
            if "attribute has no file associated with it." in str(e):
                return None
            raise e

    @classmethod
    def _register_legacy_langchain_module_aliases(cls):
        for module_name, target_module in LEGACY_LANGCHAIN_MODULE_ALIASES:
            cls._register_legacy_langchain_module_alias(
                module_name, preferred_target=target_module
            )

    @staticmethod
    def _register_legacy_langchain_module_alias(module_name, preferred_target=None):
        if not module_name or not module_name.startswith("langchain."):
            return False

        candidates = []

        if preferred_target is not None:
            candidates.append(preferred_target)

        if module_name.startswith("langchain.docstore"):
            candidates.append(
                module_name.replace(
                    "langchain.docstore", "langchain_classic.docstore", 1
                )
            )
            candidates.append(
                module_name.replace(
                    "langchain.docstore", "langchain_community.docstore", 1
                )
            )

        if module_name.startswith("langchain.schema"):
            candidates.append(
                module_name.replace("langchain.schema", "langchain_classic.schema", 1)
            )

        candidates.append(module_name.replace("langchain.", "langchain_classic.", 1))

        for candidate in candidates:
            try:
                sys.modules[module_name] = importlib.import_module(candidate)
                return True
            except ModuleNotFoundError:
                continue

        return False

    def _persist_index(self):
        """
        Persist the index to storage
        """
        self.game.faiss_file.save(
            f"{self.game.slug}-{self.game.id}",
            ContentFile(self.index.serialize_to_bytes()),
        )
        self.game.save()
