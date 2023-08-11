import tempfile
from urllib import request

from pypdf import PdfReader
from langchain.document_loaders import PyPDFLoader

from games.services.vector_store_service import get_vector_store

def ingest_document(document):
    """
    Ingest a document by:
     - Downloading rules
     - Loading rules into the vector store.
    """

    with tempfile.NamedTemporaryFile() as file:
        # Download and heck that the downloaded file is a valid PDF file
        _download_to_file(document.url, file)
        if not _valid_pdf(file.name):
            raise ValueError("Invalid PDF file")

        # Load the rules from the PDF file and split into pages
        # TODO: Find a better way of splitting the PDF, this is problematic for sections that span multiple pages
        sections = _load_and_split(file.name)

        # Add game_id and document_id to each section
        for section in sections:
            section.metadata["game_id"] = document.game.id
            section.metadata["document_id"] = document.id

        # Add to vector store
        get_vector_store().add_documents(sections)


def _download_to_file(url, file):
    r = request.get(url)
    file.write(r.content)
    file.flush()
    file.seek(0)


def _valid_pdf(filename):
    """
    Check that the file is a valid PDF file
    """
    try:
        pdf = PdfReader(filename)
        return True
    except:
        return False
    

def _load_and_split(filename):
    loader = PyPDFLoader(filename)
    return loader.load_and_split()
