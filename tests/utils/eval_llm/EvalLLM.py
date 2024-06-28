from tests.utils.eval_llm import model
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from tests.utils.eval_llm import (
    SYSTEM_PROMPT,
    INSTRUCTION,
    ACTIONS,
    InterestLevels,
    logger,
)
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
        # print("\033[31m" + response + "\033[0m")

        try:
            score = self.extract_score(response)
            accuracy = self.extract_integer(response, "Accuracy:")
            relevance = self.extract_integer(response, "Relevance:")
            logger.info(
                f"\033[1m\033[32m\nAccuracy parameters:\n"
                f"    Accuracy: {accuracy}\n"
                f"    Relevance: {relevance}\n"
                f"    Score: {score}\n\033[0m"
            )
            # print("Logger is called here")

        except (ValueError, AttributeError):
            # Handle cases where score extraction fails (e.g., missing "Overall:")
            score = None

        return (score, accuracy, relevance)

    def extract_score(self, response):
        response = response.split("Overall: ")[1]
        return response

    def extract_integer(self, output, start_string):
        try:
            start_index = output.index(start_string)
        except ValueError:
            return None

        end_of_line_index = output.index("\n", start_index)
        line = output[start_index:end_of_line_index]

        try:
            return int(line.split(":")[1].strip())
        except (IndexError, ValueError):
            return None
