import tempfile

import requests
from langchain.schema import Document
from langchain.text_splitter import TokenTextSplitter
from pypdf import PdfReader

from games.services.loaders.py_pdf_loader import load as py_pdf_loader


def ingest_document(document, load_and_split_func=None):
    """
    Ingest a document by:
     - Downloading rules
     - Loading rules into the vector store.
    """
    if load_and_split_func is None:
        load_and_split_func = _load_and_split

    with tempfile.NamedTemporaryFile() as file:
        # Download and heck that the downloaded file is a valid PDF file
        _download_to_file(document.url, file)
        if not _valid_pdf(file.name):
            raise ValueError("Invalid PDF file")

        # Load the rules from the PDF file and split into pages
        # TODO: Find a better way of splitting the PDF, this is problematic for sections that span multiple pages
        sections = load_and_split_func(file.name, py_pdf_loader)

        # Add to vector store
        document.game.vector_store.add_documents(sections, document.id)

    document.ingested = True
    document.save()


def _download_to_file(url: str, file: tempfile.NamedTemporaryFile) -> None:
    # Pretend to be a recent chrome
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }
    r = requests.get(url, headers=headers)
    file.write(r.content)
    file.flush()
    file.seek(0)


def _valid_pdf(filename: str):
    """
    Check that the file is a valid PDF file
    """
    try:
        PdfReader(filename)
        return True
    except:
        return False


def _load_and_split(filename: str, loader: callable) -> list[Document]:
    pages = loader(filename)
    # At this point we have split the pdf into pages, but they can often be too large to send to the model so lets split into smaller chunks
    sections = TokenTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(
        pages
    )
    return sections
