from src.utils.llm.LLM import LLM

from tests.utils.eval_llm.EvalLLM import EvalLLM
from tests.utils.eval_llm import get_userdata


def load_rag_llm():
    return LLM()


def load_evaluator_llm():
    return EvalLLM()


def rag_model_graded_evaluation_linkedin_positive():
    username = "elonmusk"
    topic = "SpaceX"
    user_data = get_userdata(username, "LinkedIn")

    if not user_data:
        print(f"user with {username} does not exist!")
    else:
        rag_llm = load_rag_llm()
        evaluator_llm = load_evaluator_llm()

        score = int(rag_llm.generate(user_data, topic).strip())

        rag_output = f"User shows {score} interest in {topic}"

        evaluator_input = {
            "topic": topic,
            "user_data": user_data,
            "rag_output": rag_output,
            "score": score,
        }
        evaluation_score, _, _ = evaluator_llm.evaluate_rag_output(**evaluator_input)

        assert evaluation_score == "Yes"


def rag_model_graded_evaluation_linkedin_negative():
    linkedIn_username = "elonmusk"
    topic = "SpaceX"
    user_data = get_userdata(linkedIn_username, "LinkedIn")

    if not user_data:
        print(f"user with {linkedIn_username} does not exist!")
    else:
        rag_llm = load_rag_llm()
        evaluator_llm = load_evaluator_llm()

        score = int(rag_llm.generate(user_data, topic).strip())

        rag_output = f"User shows {score} interest in {topic}"

        evaluator_input = {
            "topic": topic,
            "user_data": user_data,
            "rag_output": rag_output,
            "score": score,
        }
        evaluation_score, _, _ = evaluator_llm.evaluate_rag_output(**evaluator_input)
        print(evaluation_score)

        assert evaluation_score == "Yes"


def test_rag_model_graded_evaluation_mastodon_negative():
    mastodon_username = "@QasimRashid"
    topic = "Art and Literature"
    user_data = get_userdata(mastodon_username, "Mastodon", "@mastodon.social")

    if not user_data:
        print(f"user with {mastodon_username} does not exist!")
    else:
        rag_llm = load_rag_llm()
        evaluator_llm = load_evaluator_llm()

        score = int(rag_llm.generate(user_data, topic).strip())

        evaluator_input = {
            "topic": topic,
            "user_data": user_data,
            "score": score,
        }
        evaluation_score, _, _ = evaluator_llm.evaluate_rag_output(**evaluator_input)

        assert evaluation_score == "No"


def test_rag_model_graded_evaluation_mastodon_positive():
    mastodon_username = "@QasimRashid"
    topic = "Human Rights"
    user_data = get_userdata(mastodon_username, "Mastodon", "@mastodon.social")

    if not user_data:
        print(f"user with {mastodon_username} does not exist!")
    else:
        rag_llm = load_rag_llm()
        evaluator_llm = load_evaluator_llm()

        score = int(rag_llm.generate(user_data, topic).strip())

        evaluator_input = {
            "topic": topic,
            "user_data": user_data,
            "score": score,
        }
        evaluation_score, accuracy, relevance = evaluator_llm.evaluate_rag_output(
            **evaluator_input
        )

        assert evaluation_score == "Yes"
        assert accuracy > 50
        assert relevance > 50


def rag_model_graded_evaluation_twitter_positive():
    username = "elonmusk"
    topic = "SpaceX"
    user_data = get_userdata(username, "Twitter")

    if not user_data:
        print(f"user with {username} does not exist!")
    else:
        rag_llm = load_rag_llm()
        evaluator_llm = load_evaluator_llm()

        score = int(rag_llm.generate(user_data, topic).strip())

        evaluator_input = {
            "topic": topic,
            "user_data": user_data,
            "score": score,
        }
        evaluation_score, accuracy, relevance = evaluator_llm.evaluate_rag_output(
            **evaluator_input
        )

        assert evaluation_score == "Yes"
        assert accuracy > 50
        assert relevance > 50


def rag_model_graded_evaluation_twitter_negative():
    username = "elonmusk"
    topic = "partisan politics"
    user_data = get_userdata(username, "Twitter")

    if not user_data:
        print(f"user with {username} does not exist!")
    else:
        rag_llm = load_rag_llm()
        evaluator_llm = load_evaluator_llm()

        score = int(rag_llm.generate(user_data, topic).strip())

        evaluator_input = {
            "topic": topic,
            "user_data": user_data,
            "score": score,
        }
        evaluation_score, _, _ = evaluator_llm.evaluate_rag_output(**evaluator_input)

        assert evaluation_score == "No"
