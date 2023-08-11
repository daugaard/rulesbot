from functools import cache
import lancedb
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import LanceDB

VECTOR_STORE_LOCATION = "vector_store.db"


@cache
def get_vector_store():
    embeddings = OpenAIEmbeddings()

    db = lancedb.connect(VECTOR_STORE_LOCATION)
    table = _game_document_table()

    return LanceDB.VectorStore(table, embeddings)


def _game_document_table(self):
    """
    Ensure the document table exists and return it
    """
    if not "game_document" in self.db.table_names():
        # Seed the table with an example document to help lance derive the schema
        self.db.create_table("game_document", data=[
            "vector"=self.embeddings.embed("This is an example document"),
            "id"=0,
            "text"="This is an example document",
            "game_id"=0,
            "document_id"=0,
            "page"=0,
        ]
        
    return db.open_table("game_document")
