from functools import lru_cache

from django.conf import settings
from django.core.files.base import ContentFile
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.fake import DeterministicFakeEmbedding
from langchain.vectorstores import FAISS

EMBEDDING_LENGTH = 1536

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
            self.game.faiss_file.open()
            return FAISS.deserialize_from_bytes(
                self.game.faiss_file.read(), self.embedding
            )
        except ValueError as e:
            if "attribute has no file associated with it." in str(e):
                return None
            raise e

    def _persist_index(self):
        """
        Persist the index to storage
        """
        self.game.faiss_file.save(
            f"{self.game.slug}-{self.game.id}",
            ContentFile(self.index.serialize_to_bytes()),
        )
        self.game.save()
