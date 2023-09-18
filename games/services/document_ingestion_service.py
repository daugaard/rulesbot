import tempfile

import requests
from langchain.document_loaders import PyPDFLoader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pypdf import PdfReader


def ingest_document(document, load_pages_func=None, split_pages_to_sections_func=None):
    """
    Ingest a document by:
     - Downloading rules
     - Loading rules into the vector store.
    """
    if not load_pages_func:
        load_pages_func = _load_pages
    if not split_pages_to_sections_func:
        split_pages_to_sections_func = _split_pages_to_sections

    with tempfile.NamedTemporaryFile() as file:
        # Download and heck that the downloaded file is a valid PDF file
        _download_to_file(document.url, file)
        if not _valid_pdf(file.name):
            raise ValueError("Invalid PDF file")

        # Load the rules from the PDF file and split into pages
        pages = load_pages_func(file.name)

        # Remove ignored pages
        if document.ignore_pages:
            pages = _remove_ignore_pages(pages, document.ignore_pages)

        # Combine setup pages
        if document.setup_pages:
            pages = _combine_setup_pages(pages, document.setup_pages)

        sections = split_pages_to_sections_func(pages)
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


def _load_pages(filename):
    loader = PyPDFLoader(filename)
    return loader.load_and_split()


def _split_pages_to_sections(pages):
    # At this point we have split the pdf into pages, but they can often be too large to send to the model so lets split into smaller chunks
    sections = RecursiveCharacterTextSplitter(
        chunk_size=2500, chunk_overlap=500
    ).split_documents(pages)
    return sections


def _remove_ignore_pages(pages, pages_to_ignore):
    if not pages_to_ignore:
        return pages

    ignore_page_numbers = [int(x) for x in pages_to_ignore.split(",")]
    ignore_page_numbers = [x - 1 for x in ignore_page_numbers]  # 1-indexed to 0-indexed
    return [page for page in pages if page.metadata["page"] not in ignore_page_numbers]


def _combine_setup_pages(pages, setup_pages):
    if not setup_pages:
        return pages

    setup_page_numbers = [int(x) for x in setup_pages.split(",")]
    setup_page_numbers = [x - 1 for x in setup_page_numbers]  # 1-indexed to 0-indexed
    setup_pages = [
        page for page in pages if page.metadata["page"] in setup_page_numbers
    ]

    setup_metadata = setup_pages[0].metadata
    setup_page_content = "Start / beginning of game setup instructions:\n\n"
    setup_page_content = "\n".join([page.page_content for page in setup_pages])

    # Remove setup pages
    pages = [page for page in pages if page.metadata["page"] not in setup_page_numbers]
    # Add new setup section
    pages.insert(0, Document(page_content=setup_page_content, metadata=setup_metadata))

    return pages
