import redis
from django.conf import settings
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.fake import DeterministicFakeEmbedding
from langchain.vectorstores.redis import Redis
from redis.client import Redis as RedisClient

EMBEDDING_LENGTH = 1536

DEFAULT_EMBEDDING = (
    DeterministicFakeEmbedding(size=1536) if settings.TESTING else OpenAIEmbeddings()
)


class GameVectorStore:
    """
    A vector store for a specific game.

    This vector store will have all the game documents loaded and stored along side the game record in the database.
    """

    def __init__(self, game, embedding=None):
        self.game = game

        if embedding is None:
            embedding = DEFAULT_EMBEDDING
        self.embedding = embedding
        self.index = (
            Redis.from_existing_index(
                embedding=embedding,
                redis_url=settings.REDIS_URL,
                index_name=self._game_index_name(),
            )
            if self._index_exists()
            else None
        )

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
            self.index = Redis.from_documents(
                documents=documents,
                redis_url=settings.REDIS_URL,
                index_name=self._game_index_name(),
                embedding=self.embedding,
            )

    def clear(self):
        """
        Clear the vector store
        """
        if self.index:
            self.index.drop_index(
                index_name=self._game_index_name(), delete_documents=True
            )

    def _index_exists(self):
        """
        Check if the index exists
        """
        client = RedisClient.from_url(settings.REDIS_URL)
        try:
            client.ft(self._game_index_name()).info()
        except redis.exceptions.ResponseError as e:
            message = e.args[0] if len(e.args) > 0 else ""
            if message.lower() == "unknown index name":
                client.close()
                return False
            else:
                raise e

        client.close()
        return True

    def _game_index_name(self):
        return f"game_{self.game.id}_documents"
