from langchain.document_loaders import PDFPlumberLoader
from langchain.schema import Document


def load(filename: str) -> list[Document]:
    """
    Load a PDF file and split it into pages
    """
    loader = PDFPlumberLoader(filename)
    return loader.load()
