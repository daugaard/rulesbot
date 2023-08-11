from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

EMBEDDING_LENGTH = 1536

class GameVectorStore():
    """
    A vector store for a specific game. 

    This vector store will have all the game documents loaded and stored along side the game record in the database. 
    """
    def __init__(self, game, embedding=None):
        self.game = game
    
        if embedding is None:
            embedding = OpenAIEmbeddings()
        self.embedding = embedding
        self.index = self._try_load_game_index()
        

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

        if self.index:
            self.index.add_documents(documents)
        else:
            self.index = FAISS.from_documents(documents, self.embedding)

        # Commit these changes to the game object
        self.persist_to_game()

    def persist_to_game(self):
        """
        Persist the index to the database
        """
        self.game.vector_store_binary = self.index.serialize_to_bytes()
        self.game.save()
        

    def _try_load_game_index(self):
        """
        Try to load the game table from the database
        """
        if self.game.vector_store_binary is not None:
            return FAISS.deserialize_from_bytes(self.game.vector_store_binary, self.embedding)
        else:
            return None

    def _game_index_name(self):
        return f"game_{self.game.id}_documents"
