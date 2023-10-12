"""
This script evaluates the performance of the rulesbot against a number of games with a number of known question/answer pairs.

The script is run from the command line.

Usage:
    python evaluate_rulesbot.py

The script will output a table of results to the console.

Test data is specified in the fixtures/evaluate_rulesbot/*.json files. One file for each game on the structure:
    {
        "name": "Game name",
        "document_urls": [
            "https://www.example.com/document1.pdf",
        ],
        "question_sessions": [
            {
                "description": "Session description",
                "messages": [ # optional
                    {
                        "type": "human",
                        "text": "Question text",
                    },
                    {
                        "type": "ai",
                        "text": "Answer text",
                    }
                ],
                "question": "Question text",
                "answer": "Answer text",
            }
        ]
    }
"""
import json
import os
import sys
from multiprocessing import SimpleQueue
from pathlib import Path

import django

# Load django - this has to be done before loading any models, hence the odd import order
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rulesbot.settings")
django.setup()

from colorama import Fore, Style  # noqa: E402

from chat.models import ChatSession  # noqa: E402
from chat.services import streaming_question_answering_service  # noqa: E402
from games.models import Game  # noqa: E402
from games.services import document_ingestion_service  # noqa: E402


def parse_game_json(filename: Path) -> dict:
    with open(filename, "r") as f:
        return json.load(f)


def setup_game(game: dict) -> Game:
    game_obj = Game.objects.create(name=game["name"])
    for document in game["documents"]:
        game_obj.document_set.create(
            url=document.get("url"),
            ignore_pages=document.get("ignore_pages", ""),
            setup_pages=document.get("setup_pages", ""),
        )
    return game_obj


def ingest_game(game: Game) -> None:
    for document in game.document_set.all():
        document_ingestion_service.ingest_document(document)
    game.ingested = True
    game.save()


def setup_chat_session(game: Game, question_session) -> ChatSession:
    messages = question_session.get("messages", [])

    session = ChatSession.objects.create(game=game, ip_address="")

    for message in messages:
        session.message_set.create(
            message_type=message["type"],
            message=message["text"],
        )

    return session


def clean_up_game(game: Game) -> None:
    game.chatsession_set.all().delete()
    game.document_set.all().delete()
    game.delete()


def evaluate_question(
    session: ChatSession, question: str, answer: str, description: str
) -> bool:
    # TODO: Change to use langchain evalutor eventually.
    # evaluator = load_evaluator("labeled_criteria", criteria="correctness")
    # eval_result = evaluator.evaluate_strings(
    #    input=question,
    #    prediction=bot_answer,
    #    target=answer,
    # )
    print(Fore.BLUE + f"Game: {session.game.name}" + Style.RESET_ALL)
    print(Fore.BLUE + f"Description: {description}" + Style.RESET_ALL)
    print(Fore.MAGENTA + f"Question: {question}" + Style.RESET_ALL)

    queue = (
        SimpleQueue()
    )  # Ignore the queue and just return the result by reading the message set
    streaming_question_answering_service.ask_question(question, session, queue)

    bot_answer = session.message_set.filter(message_type="ai").last().message

    print(Fore.RED + f"Reference Answer: {answer}" + Style.RESET_ALL)
    print(Fore.GREEN + f"Bot answer: {bot_answer}" + Style.RESET_ALL)

    # ask user if the bot answer is correct
    while True:
        user_input = input("Is the bot answer correct? (y/n): ")
        if user_input == "y":
            eval_result = {"score": 1}
            break
        elif user_input == "n":
            eval_result = {"score": 0}
            break
        else:
            print("Invalid input. Please enter 'y' or 'n'")

    return eval_result["score"]


def run_fixture_file(filename: Path) -> None:
    print(Fore.CYAN + f"Running fixture file: {filename}" + Style.RESET_ALL)
    fixture_object = parse_game_json(filename)
    game = setup_game(fixture_object)
    ingest_game(game)
    total_correct = 0
    total_questions = len(fixture_object["question_sessions"])

    for question_session in fixture_object["question_sessions"]:
        session = setup_chat_session(game, question_session)
        score = evaluate_question(
            session=session,
            question=question_session["question"],
            answer=question_session["answer"],
            description=question_session["description"],
        )
        total_correct += score

    print(Fore.GREEN + f"Total correct for game: {total_correct}/{total_questions}")

    clean_up_game(game)

    return total_correct, total_questions


def run_tests() -> None:
    # List all files in the fixtures/evaluate_rulesbot directory
    test_files = (
        Path(__file__).parent.joinpath("fixtures", "evaluate_rulesbot").glob("*.json")
    )

    total_correct = 0
    total_questions = 0

    for test_file in test_files:
        correct, questions = run_fixture_file(test_file)
        total_correct += correct
        total_questions += questions

    print(
        Fore.CYAN
        + Style.BRIGHT
        + f"=== Total correct: {total_correct}/{total_questions} ====="
        + Style.RESET_ALL
    )


if __name__ == "__main__":
    # get if there is an arg for a specific test file
    # if so, run that test file
    # else, run all test files
    if len(sys.argv) > 1:
        test_file = Path(sys.argv[1])
        run_fixture_file(test_file)
    else:
        run_tests()
