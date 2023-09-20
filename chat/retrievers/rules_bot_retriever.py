from langchain import FAISS
from langchain.schema import BaseRetriever


class RulesBotRetriever(BaseRetriever):
    """
    Custom retriever for the rules bot.

    This retriever uses a FAISS index to retrieve the most similar documents.

    It also adds the setup page to the results if the question is a setup question.
    """

    index: FAISS
    search_kwargs: dict

    def get_relevant_documents(self, question):
        docs = self.index.similarity_search(question, **self.search_kwargs)

        if self._is_setup_question(question):
            setup_documents = self.index.similarity_search(
                "setup", filter={"setup_page": True}
            )
            # Remove the N last results from docs where N is the number of setup documents
            docs = docs[: -len(setup_documents)]
            docs = docs + setup_documents

        return docs

    def _is_setup_question(self, question):
        question = question.lower()
        return (
            "setup" in question
            or "set up" in question
            or "set-up" in question
            or "start with" in question
            or "starts with" in question
        )
