from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyMuPDFLoader
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


def load_and_split(filename, document):
    """
    Loads the filename and splits it into sections to index.

    :param filename: The filename to load.
    :param document: The document to index.
    :return: A list of sections to index.
    """
    pages = _load_pages(filename)

    # Remove ignored pages
    if document.ignore_pages:
        pages = _remove_ignore_pages(pages, document.ignore_pages)

    # Clean up the pages
    # TODO: Add guard to only do this if we have the checkbox enabled
    # for page in pages:
    #    page.page_content = _clean_up_page(page.page_content)

    sections = _split_pages_to_sections(pages)

    # Combine setup pages
    if document.setup_pages:
        setup_document = _extract_setup_instructions(pages, document.setup_pages)
        sections.append(setup_document)

    return sections


def _load_pages(filename):
    loader = PyMuPDFLoader(filename)
    return loader.load()


def _split_pages_to_sections(pages):
    # At this point we have split the pdf into pages, but they can often be too large to send to the model so lets split into smaller chunks
    sections = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=100
    ).split_documents(pages)
    return sections


def _remove_ignore_pages(pages, pages_to_ignore):
    ignore_page_numbers = [int(x) for x in pages_to_ignore.split(",")]
    ignore_page_numbers = [x - 1 for x in ignore_page_numbers]  # 1-indexed to 0-indexed
    return [page for page in pages if page.metadata["page"] not in ignore_page_numbers]


def _extract_setup_instructions(pages, setup_pages):
    setup_page_numbers = [int(x) for x in setup_pages.split(",")]
    setup_page_numbers = [x - 1 for x in setup_page_numbers]  # 1-indexed to 0-indexed
    setup_pages = [
        page for page in pages if page.metadata["page"] in setup_page_numbers
    ]

    setup_metadata = setup_pages[0].metadata.copy()
    setup_metadata["setup_page"] = True
    setup_page_content = "Start of game setup instructions:\n\n"
    setup_page_content += "\n".join([page.page_content for page in setup_pages])

    # TODO: Add guard to only do this if we have the checkbox enabled
    # summarized_page_content = _summarize_setup_instructions(setup_page_content)
    summarized_page_content = setup_page_content

    return Document(page_content=summarized_page_content, metadata=setup_metadata)


def _summarize_setup_instructions(setup_page_content):
    """
    Use ChatGPT to summarize the setup instructions.
    """
    llm = ChatOpenAI(temperature=0.1)
    prompt = f"Provided setup instructions for a board game. Please clean them up and summarize them into an easy-to-read and understand format. \n\n{setup_page_content}\n\nSummary:"
    return llm.predict(prompt)


def _clean_up_page(page_content):
    """
    Use ChatGPT to clean up the content.
    """
    print("Cleaning up page ... ")
    llm = ChatOpenAI(temperature=0.1)
    prompt = f"Please clean up the following page of rules to make it easier to read and understand. \n\n{page_content}\n\nCleaned up rules:"
    print(f"Input: {page_content}")
    cleaned_up_page_content = llm.predict(prompt)
    print(f"Output: {cleaned_up_page_content}")
    return cleaned_up_page_content
