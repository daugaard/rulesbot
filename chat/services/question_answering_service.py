from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI


def ask_question(question, chat_session):
    """
    Ask a question in the chat session and add response to the chat session.
    """

    chat_session.message_set.create(message=question, message_type="human")

    qc_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(),
        chain_type="stuff",
        retriever=chat_session.game.vector_store.index.as_retriever(),
    )
    answer = qc_chain.run(question)
    chat_session.message_set.create(message=answer, message_type="ai")
