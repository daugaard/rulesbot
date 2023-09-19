from langchain import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.schema.messages import AIMessage, HumanMessage

prompt_template = """Please use the following information to provide a clear and accurate answer to this question regarding the rules of the game %%GAME%%.
If the question is not related to the rules of the specified game, kindly decline to answer.
If the question is not a question but a greeting or a thank you, kindly respond with a greeting or a thank you.
If the question is claiming that the answer is wrong, kindly respond with an apology.

**Context:**
{context}

Ignore any variant or optional rules unless specifically instructed not to.

**User's Question:** {question}

**Detailed Answer:**"""

condense_question_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language. If the follow up question is a statement and not a question pass it through.

**Conversation**:
{chat_history}
**Follow Up Question**: {question}
**Standalone Question or Statement**:
"""


def ask_question(question, chat_session):
    """
    Ask a question in the chat session and add response to the chat session.
    """
    result = _query_conversational_retrieval_chain(question, chat_session)

    chat_session.message_set.create(message=question, message_type="human")

    answer = result["answer"]
    ai_message = chat_session.message_set.create(message=answer, message_type="ai")
    for source_document in result["source_documents"]:
        ai_message.sourcedocument_set.create(
            document_id=source_document.metadata["document_id"],
            page_number=source_document.metadata["page"] + 1,  # 0-indexed
        )


def _query_conversational_retrieval_chain(question, chat_session):
    qa_chain = _setup_conversational_retrieval_chain(chat_session)
    return qa_chain(
        {"question": question, "chat_history": _get_chat_history(chat_session)}
    )


def _setup_conversational_retrieval_chain(chat_session):
    personalized_prompt_template = prompt_template.replace(
        "%%GAME%%", chat_session.game.name
    )
    question_answering_prompt = PromptTemplate(
        template=personalized_prompt_template, input_variables=["context", "question"]
    )
    condense_question_prompt = PromptTemplate(
        template=condense_question_template,
        input_variables=["chat_history", "question"],
    )

    return ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(),
        condense_question_llm=ChatOpenAI(temperature=0.1),
        condense_question_prompt=condense_question_prompt,
        retriever=chat_session.game.vector_store.index.as_retriever(
            search_kwargs={"k": 3}
        ),
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": question_answering_prompt},
        verbose=True,
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
