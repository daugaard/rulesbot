"""
This is expermintal code to try and split a PDF into sections based on font size.

THIS SHOULD NOT BE USED IN PRODUCTION IT IS KNOWN TO DROP TEXT AND IS NOT RELIABLE
"""

import re
from dataclasses import dataclass

from bs4 import BeautifulSoup
from langchain.document_loaders import PDFMinerPDFasHTMLLoader
from langchain.schema import Document


@dataclass
class Snippet:
    # Class to keep track of HTML snippets
    text: str
    font_size: int


def load(filename: str) -> list[Document]:
    """
    Load a PDF file and split it into pages
    """
    html_document = _load_as_html(filename)
    snippets = _parse_html(html_document)
    for s in snippets:
        print(s.font_size)
    return _combine_snippets(snippets, html_document.metadata)


def _load_as_html(filename: str) -> Document:
    """
    Load a PDF file as HTML
    """
    loader = PDFMinerPDFasHTMLLoader(filename)
    return loader.load()[0]


def _parse_html(doc: Document) -> list[Snippet]:
    snippets = []

    soup = BeautifulSoup(doc.page_content, "html.parser")
    divs = soup.find_all("div")

    current_font_size = 0
    current_text = ""

    for div in divs:
        span = div.find("span")
        if span is None:
            continue
        style = span.get("style")
        if style is None:
            continue
        font_size_match = re.search(r"font-size:([0-9]+)px", style)
        if font_size_match is None:
            continue
        font_size = int(font_size_match.group(1))
        text = span.text
        if font_size == current_font_size:
            current_text += text
        else:
            snippets.append(Snippet(current_text, current_font_size))
            current_font_size = font_size
            current_text = text

    return snippets


def _deduplicate_snippets(snippets: list[Snippet]) -> list[Snippet]:
    """
    Remove duplicate snippets
    """
    pass


def _combine_snippets(snippets: list[Snippet], doc_metadata: dict) -> list[Document]:
    """
    Combine snippets into document sections
    """
    current_index = -1
    semantic_sections = []
    for snippet in snippets:
        if (
            len(semantic_sections) == 0
            or snippet.font_size
            >= semantic_sections[current_index].metadata["heading_font_size"]
        ):
            # if there is no semantic sections or the font is > than the previous sections heading it is a new section
            metadata = {
                "heading": snippet.text,
                "heading_font_size": snippet.font_size,
                "content_font": 0,
            }
            metadata.update(doc_metadata)
            semantic_sections.append(
                Document(page_content=snippet.text, metadata=metadata)
            )
            current_index += 1
        elif (
            semantic_sections[current_index].metadata["heading_font_size"] == 0
            or snippet.font_size
            <= semantic_sections[current_index].metadata["heading_font_size"]
        ):
            # else if the font is < than the previous sections heading it is content belonging to the previous section
            semantic_sections[current_index].page_content += "\n" + snippet.text
            semantic_sections[current_index].metadata["content_font"] = max(
                snippet.font_size,
                semantic_sections[current_index].metadata["content_font"],
            )
        else:
            # else font size is > than the previous sections content but < than the previous sections heading so it is a new section
            metadata = {
                "heading": snippet.text,
                "heading_font_size": snippet.font_size,
                "content_font": 0,
            }
            metadata.update(doc_metadata)
            semantic_sections.append(
                Document(page_content=snippet.text, metadata=metadata)
            )
            current_index += 1

    return semantic_sections
