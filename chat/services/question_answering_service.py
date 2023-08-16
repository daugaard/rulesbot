from langchain import OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.schema.messages import AIMessage, HumanMessage


def ask_question(question, chat_session):
    """
    Ask a question in the chat session and add response to the chat session.
    """
    qa_chain = _setup_conversational_retrieval_chain(chat_session)
    result = qa_chain(
        {"question": question, "chat_history": _get_chat_history(chat_session)}
    )

    chat_session.message_set.create(message=question, message_type="human")

    answer = result["answer"]
    ai_message = chat_session.message_set.create(message=answer, message_type="ai")
    for source_document in result["source_documents"]:
        ai_message.sourcedocument_set.create(
            document_id=source_document.metadata["document_id"],
            page_number=source_document.metadata["page"] + 1,  # 0-indexed
        )


def _setup_conversational_retrieval_chain(chat_session):
    return ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(),
        condense_question_llm=OpenAI(),
        retriever=chat_session.game.vector_store.index.as_retriever(k=3),
        return_source_documents=True,
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
