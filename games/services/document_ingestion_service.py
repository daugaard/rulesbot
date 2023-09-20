import tempfile

import requests
from pypdf import PdfReader

from games.loaders.pdf_loader_and_summarizer import load_and_split


def ingest_document(document, load_and_split_func=None):
    """
    Ingest a document by:
     - Downloading rules
     - Loading rules into the vector store.
    """
    if not load_and_split_func:
        load_and_split_func = load_and_split

    with tempfile.NamedTemporaryFile() as file:
        # Download and heck that the downloaded file is a valid PDF file
        _download_to_file(document.url, file)
        if not _valid_pdf(file.name):
            raise ValueError("Invalid PDF file")

        # Load the rules from the PDF file and split into sections
        sections = load_and_split_func(file.name, document)

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
