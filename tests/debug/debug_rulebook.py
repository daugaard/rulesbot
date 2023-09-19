# Script to help us debug a rulebook
# This script is not meant to be run as a test, but rather to be run manually

# This script will load a rulebook and then allow you to run queries against it
# outputing the results to the console along with the context.

# This script is meant to be run from the root of the project.

# Example usage:
#   python manage.py shell
#   from tests.debug.debug_rulebook import run_query
#   from games.models import Game
#   game = Game.objects.get(name="Forgotten Waters")
#   run_query(game, "What is the power of a 2/2 creature?")

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from chat.models import ChatSession
from chat.services import question_answering_service
from games.models import Game
from games.services.document_ingestion_service import ingest_document


def load_and_split_alternative(filename):
    print("Loading and splitting document in alternative way")
    loader = PyPDFLoader(filename)
    pages = loader.load_and_split()
    sections = RecursiveCharacterTextSplitter(
        chunk_size=2500, chunk_overlap=500
    ).split_documents(pages)
    return sections


def reingest_documents(game=Game):
    """
    Reingest all documents for a game using alternative ingestion mechanism.
    """
    # clear the vector store
    game.vector_store.clear()
    # ingest the documents
    for document in game.document_set.all():
        ingest_document(
            document,
            # load_and_split_func=load_and_split_alternative,
        )


def run_query(game=Game, query=str):
    """
    Run a query against a rulebook
    """
    chat_session = ChatSession.objects.create(game=game, ip_address="0.0.0.0")

    result = question_answering_service._query_conversational_retrieval_chain(
        query, chat_session
    )

    print("Question: " + query)
    print("Answer: " + result["answer"])
    print("=======================================")
    print("Context:")
    print("=======================================")
    for source_document in result["source_documents"]:
        print("Document: " + source_document.metadata["source"])
        print("Page: " + str(source_document.metadata["page"]))
        print("Length: " + str(len(source_document.page_content)))
        print("Context: " + source_document.page_content)
        print("=======================================")


if __name__ == "__main__":
    raise NotImplementedError(
        "This script is not meant to be run as a test, but rather to be run manually"
    )
