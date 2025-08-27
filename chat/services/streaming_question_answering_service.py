from enum import Enum, auto

from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.schema.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from chat.retrievers.rules_bot_retriever import RulesBotRetriever
from rulesbot.settings import DEFAULT_CHATGPT_MODEL

prompt_template = """Please use the following information to provide a clear and accurate answer to this question regarding the rules of the game %%GAME%%.
Explain your answer in detail using the rulebook information provided.
If the question is not a question but a greeting or a thank you, kindly respond with a greeting or a thank you.
If the question is claiming that the answer is wrong, kindly respond with an apology.
Ignore any variant or optional rules unless specifically instructed not to.

**Rulebook Context:**
{context}

"""

condense_question_for_retrieval_prompt_template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.
If the follow up question is not a question do not rephrase it.

If the question pertains to the setup of a game, rephrase it to focus on the setup process and ensure you mention "setup" and "start of game" in the question.
"""


class QueueSignals(Enum):
    job_done = auto()
    error = auto()


class QueueCallbackHandler(BaseCallbackHandler):
    def __init__(self, queue):
        self.queue = queue

    def on_llm_new_token(self, token, **kwargs) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        self.queue.put(token)

    def on_llm_end(self, response, **kwargs) -> None:
        """Run when LLM ends running."""
        self.queue.put(QueueSignals.job_done)

    def on_llm_error(self, error, **kwargs) -> None:
        """Run when LLM errors."""
        self.queue.put(QueueSignals.error)


def ask_question(question, chat_session, response_queue):
    """
    Ask a question in the chat session and add response to the chat session.
    """
    chat_session.message_set.create(message=question, message_type="human")

    result = _query_conversational_retrieval_chain(
        question, chat_session, response_queue
    )

    answer = result["answer"]
    ai_message = chat_session.message_set.create(message=answer, message_type="ai")
    for source_document in result["context"]:
        ai_message.sourcedocument_set.create(
            document_id=source_document.metadata["document_id"],
            page_number=source_document.metadata["page"] + 1,  # 0-indexed
        )

    return response_queue


def _query_conversational_retrieval_chain(question, chat_session, response_queue):
    qa_chain = _setup_conversational_retrieval_chain(chat_session, response_queue)
    return qa_chain.invoke(
        {"input": question, "chat_history": _get_chat_history(chat_session)}
    )


def _setup_conversational_retrieval_chain(chat_session, response_queue):
    personalized_prompt_template = prompt_template.replace(
        "%%GAME%%", chat_session.game.name
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", condense_question_for_retrieval_prompt_template),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        llm=ChatOpenAI(model=DEFAULT_CHATGPT_MODEL, temperature=0.1),
        retriever=RulesBotRetriever(
            index=chat_session.game.vector_store.index,
            search_kwargs={"k": 3},
        ),
        prompt=contextualize_q_prompt,
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", personalized_prompt_template),
            MessagesPlaceholder("chat_history"),
            ("user", "{input}"),
        ]
    )

    stuff_docs_chain = create_stuff_documents_chain(
        llm=ChatOpenAI(
            model=DEFAULT_CHATGPT_MODEL,
            temperature=0.1,
            streaming=True,
            callbacks=[QueueCallbackHandler(response_queue)],
        ),
        prompt=qa_prompt,
        document_variable_name="context",
    )

    retrieval_chain = create_retrieval_chain(history_aware_retriever, stuff_docs_chain)

    return retrieval_chain


def _get_chat_history(chat_session):
    chat_history = []
    latest_messages = chat_session.message_set.order_by("-created_at")[:12]
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
