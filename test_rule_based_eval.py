import pytest

from src.utils.llm.LLM import LLM
from tests.utils.eval_llm import get_rag_output, get_userdata


def load_rag_llm():
    return LLM()


def test_rag_rule_based_evaluation():
    # Define sample topics and user data variations
    topics = ["Free Speech", "Conspiracy Theories"]
    user_data = get_userdata("elonmusk", "Twitter")
    rag_llm = load_rag_llm()

    # Define expected outputs based on predefined rules
    expected_outputs = [
        get_rag_output(80),
        get_rag_output(40),
    ]

    for topic, expected_output in zip(topics, expected_outputs):
        # Simulate LLM score
        score = int(rag_llm.generate(topic, user_data).strip())

        # Assert the RAG output matches the expected_outputs based on rules
        assert get_rag_output(score) == expected_output
