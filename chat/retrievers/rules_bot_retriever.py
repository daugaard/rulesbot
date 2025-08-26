from langchain.schema import BaseRetriever
from langchain_community.vectorstores import FAISS


class RulesBotRetriever(BaseRetriever):
    """
    Custom retriever for the rules bot.

    This retriever uses a FAISS index to retrieve the most similar documents.

    It also adds the setup page to the results if the question is a setup question.
    """

    index: FAISS
    search_kwargs: dict

    def get_relevant_documents(self, question):
        # TODO: Debug relevancy score and figure out if we should filter at a threshold
        docs_with_score = self.index.similarity_search_with_relevance_scores(
            question, **self.search_kwargs
        )

        docs = []
        for doc, score in docs_with_score:
            doc.metadata["relevancy_score"] = score
            docs.append(doc)

        if self._is_setup_question(question):
            # If the setup page is not already in the results, add it
            if not any(doc.metadata.get("setup_page") for doc in docs):
                setup_documents = self.index.similarity_search(
                    "setup", filter={"setup_page": True}
                )
                if len(setup_documents) > 0:
                    # Remove the N last results from docs where N is the number of setup documents and add the setup documents
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
            or "start the game" in question
            or "begin with" in question
            or "begins with" in question
            or "start of the game" in question
            or "beginning of the game" in question
        )
