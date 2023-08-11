import tempfile
import requests

from pypdf import PdfReader
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


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

        # Add to vector store
        document.game.vector_store.add_documents(sections, document.id)

    document.ingested = True
    document.save()


def _download_to_file(url, file):
    # Pretend to be a recent chrome
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }
    r = requests.get(url, headers=headers)
    file.write(r.content)
    file.flush()
    file.seek(0)


def _valid_pdf(filename):
    """
    Check that the file is a valid PDF file
    """
    try:
        PdfReader(filename)
        return True
    except:
        return False


def _load_and_split(filename):
    loader = PyPDFLoader(filename)
    pages = loader.load_and_split()
    # At this point we have split the pdf into pages, but they can often be too large to send to the model so lets split into smaller chunks
    sections = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=100
    ).split_documents(pages)
    return sections
