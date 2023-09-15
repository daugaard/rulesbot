from langchain.document_loaders import PyPDFLoader
from langchain.schema import Document


def load(filename: str) -> list[Document]:
    """
    Load a PDF file and split it into pages
    """
    loader = PyPDFLoader(filename)
    return loader.load_and_split()
