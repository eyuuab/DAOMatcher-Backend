from tests.utils.eval_llm import model
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from tests.utils.eval_llm import SYSTEM_PROMPT, INSTRUCTION, ACTIONS, InterestLevels

from langchain_core.output_parsers import StrOutputParser


class EvalLLM:
    def __init__(self, temperature=0.1, max_tokens=512):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        template = SYSTEM_PROMPT + INSTRUCTION
        self.prompt = PromptTemplate(
            template=template,
            input_variables=["topic", "user_data", "score"],
        ).partial(actions=str(ACTIONS), intervals=str(InterestLevels))
        self.chain = self.prompt | self.model | StrOutputParser()

    def evaluate_rag_output(self, topic, score, user_data):
        response = self.chain.invoke(
            {
                "topic": topic,
                "user_data": user_data,
                "score": score,
            }
        )
        print("\n" + response + "\n")

        try:
            score = self.extract_score(response)
        except (ValueError, AttributeError):
            # Handle cases where score extraction fails (e.g., missing "Overall:")
            score = None

        return score

    def extract_score(self, response):
        response = response.split("Overall: ")[1]
        return response
