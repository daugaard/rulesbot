from enum import Enum, auto

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from chat.retrievers.rules_bot_retriever import RulesBotRetriever
from rulesbot.settings import DEFAULT_CHATGPT_MODEL

prompt_template = """Please use the available tools to provide a clear and accurate answer to questions regarding the rules of %%GAME%%.
Always use the rulebook search tool before answering rule questions.
Explain your answer in detail using the rulebook information you found.
If the question is not a question but a greeting or a thank you, kindly respond with a greeting or a thank you.
If the question is claiming that the answer is wrong, kindly respond with an apology.
Ignore any variant or optional rules unless specifically instructed not to.
"""


class QueueSignals(Enum):
    job_done = auto()
    error = auto()


def ask_question(question, chat_session, response_queue):
    """
    Ask a question in the chat session and add response to the chat session.
    """
    chat_session.message_set.create(message=question, message_type="human")

    try:
        result = _query_agentic_stream(question, chat_session, response_queue)
    except Exception:
        response_queue.put(QueueSignals.error)
        raise

    answer = result["answer"]
    ai_message = chat_session.message_set.create(message=answer, message_type="ai")
    for source_document in result["context"]:
        ai_message.sourcedocument_set.create(
            document_id=source_document.metadata["document_id"],
            page_number=source_document.metadata["page"] + 1,  # 0-indexed
        )

    response_queue.put(QueueSignals.job_done)
    return response_queue


def _query_agentic_stream(question, chat_session, response_queue):
    retrieved_documents = []
    rulebook_search_tool = _build_rulebook_search_tool(
        chat_session, retrieved_documents
    )
    agent = _build_question_answering_agent(chat_session, [rulebook_search_tool])

    answer = _stream_agent_answer(
        agent=agent,
        question=question,
        chat_session=chat_session,
        response_queue=response_queue,
    )

    return {
        "answer": answer,
        "context": _deduplicate_documents(retrieved_documents),
    }


def _build_question_answering_agent(chat_session, tools):
    personalized_prompt_template = prompt_template.replace(
        "%%GAME%%", chat_session.game.name
    )

    model = ChatOpenAI(
        model=DEFAULT_CHATGPT_MODEL,
        temperature=0.1,
        streaming=True,
    )

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=personalized_prompt_template,
        name="rulesbot_question_answering_agent",
    )


def _build_rulebook_search_tool(chat_session, retrieved_documents):
    retriever = RulesBotRetriever(
        index=chat_session.game.vector_store.index,
        search_kwargs={"k": 3},
    )

    @tool("rulebook_search")
    def rulebook_search(query: str) -> str:
        """Search the current game's rulebook and return relevant passages with page references."""
        docs = retriever.invoke(query)
        retrieved_documents.extend(docs)
        return _format_rulebook_context(docs)

    return rulebook_search


def _format_rulebook_context(documents):
    if len(documents) == 0:
        return "No relevant rulebook passages were found."

    passages = []
    for i, document in enumerate(documents, start=1):
        page_number = document.metadata.get("page")
        page_display = page_number + 1 if isinstance(page_number, int) else "unknown"
        document_id = document.metadata.get("document_id", "unknown")
        relevancy_score = document.metadata.get("relevancy_score")
        relevancy_text = (
            f"{relevancy_score:.3f}"
            if isinstance(relevancy_score, float)
            else "unknown"
        )
        passages.append(
            "\n".join(
                [
                    f"Passage {i}",
                    f"Document ID: {document_id}",
                    f"Page: {page_display}",
                    f"Relevancy: {relevancy_text}",
                    document.page_content,
                ]
            )
        )

    return "\n\n".join(passages)


def _stream_agent_answer(agent, question, chat_session, response_queue):
    answer_chunks = []
    answer = None

    chat_history = _get_chat_history(chat_session)
    if (
        not chat_history
        or not isinstance(chat_history[-1], HumanMessage)
        or chat_history[-1].content != question
    ):
        chat_history.append(HumanMessage(content=question))

    agent_input = {"messages": chat_history}

    for chunk in agent.stream(
        agent_input,
        stream_mode=["messages", "updates"],
        version="v2",
    ):
        if chunk.get("type") == "messages":
            token, _metadata = chunk["data"]
            if isinstance(token, AIMessageChunk) and token.text:
                response_queue.put(token.text)
                answer_chunks.append(token.text)

        if chunk.get("type") == "updates":
            for source, update in chunk["data"].items():
                if source != "model":
                    continue
                if not isinstance(update, dict):
                    continue

                messages = update.get("messages", [])
                if not messages:
                    continue

                latest_message = messages[-1]
                if isinstance(latest_message, AIMessage) and latest_message.text:
                    answer = latest_message.text

    if answer is None:
        answer = "".join(answer_chunks)

    return answer


def _deduplicate_documents(documents):
    unique_documents = []
    seen = set()
    for document in documents:
        key = (document.metadata.get("document_id"), document.metadata.get("page"))
        if key in seen:
            continue
        seen.add(key)
        unique_documents.append(document)

    return unique_documents


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
            continue
    return chat_history if chat_history else []
