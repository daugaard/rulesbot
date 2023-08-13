from langchain import OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.schema.messages import AIMessage, HumanMessage


def ask_question(question, chat_session):
    """
    Ask a question in the chat session and add response to the chat session.
    """
    qc_chain = _setup_conversational_retrieval_chain(chat_session)
    answer = qc_chain.run(
        {"question": question, "chat_history": _get_chat_history(chat_session)}
    )

    chat_session.message_set.create(message=question, message_type="human")
    chat_session.message_set.create(message=answer, message_type="ai")


def _setup_conversational_retrieval_chain(chat_session):
    return ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(),
        condense_question_llm=OpenAI(),
        retriever=chat_session.game.vector_store.index.as_retriever(),
    )


def _get_chat_history(chat_session):
    chat_history = []
    latest_messages = chat_session.message_set.order_by("-created_at")[:8]
    latest_messages_in_cronological_order = reversed(latest_messages)
    for message in latest_messages_in_cronological_order:
        if message.message_type == "human":
            chat_history.append(HumanMessage(content=message.message))
        elif message.message_type == "ai":
            chat_history.append(AIMessage(content=message.message))
        elif message.message_type == "system":
            # Do nothing for system messages
            print(message.message_type)
    return chat_history if chat_history else []
