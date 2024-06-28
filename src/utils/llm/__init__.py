# import os

from decouple import config
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# from langchain_google_vertexai import ChatVertexAI

load_dotenv()
GOOGLE_API_KEY = config("PALM_API_KEY")
# os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

LOCAL_LLM_PORT = config("LLM_PORT", "5001")
LOCAL_LLM_URL = f"http://127.0.0.1:{LOCAL_LLM_PORT}"
LLM_URL = None

ACTIONS = [
    "Search for explicit mentions of the topic in the posts",
    "Search for indication of interest in the topic from the posts",
    "Search for topics that could belong to the same category as the given topic",
    "Pick a number from the interest levels matching the user's interest in the topic of question",
]

InterestLevels = [
    "The user's posts talks about completely different topic and show no interest in the topic given = 10-20",
    "The user's posts talks about completely different topic but those topics might have something in common with the topic in question = 20-30",
    "The user's posts talks about topics that can be under the same category and might be interested in the topic = 30-60",
    "The user's posts shows clear signs of being interested in the topic in question = 60-80",
    "The user's posts mention the topic in question and suggest a high likelihood of being interested in the topic = 80-100",
]

DEFAULT_SYSTEM_PROMPT = """
You are expert user recommender that would be interested in a certain topic. Your task is to provide a number of a user's likely hood of being interested on a given topic on the scale of 1-100 by analyzing the posts they made. You should carefully look for interest indicating words, explicit mention of the topic, posts that might belong to the same category as the topic given, other similar interest of the user and any other thing you need to do to make the recommendation efficient. Your final response should contain only one number that signifies the likelihood of the user's interest on the topic. Output a number in the interval of 5 between 0 and 100. You shouldn't use any type of formatting except the one provided.
Topic: {query}
Posts: {content}
"""
INSTRUCTION = """Given the topic and the Posts above.

Use the following format:
Question: The topic the human asked you

Thought: you should always think about what to do
Action: the action to take, should be one of {actions}
Action Input: the input to the action
Observation: verbal description of what you learned after performing the above action
(... this pattern 'Thought/Action/Action Input/Observation' can be repeated N times as needed)

Analysis: your analysis of the user's interest based on Explicit mentions, Indications of interest and similar topics or field of work to the given topic
Observation: What you learned after performing the above action and what led to such conclusion

Final Thought: you now know what the final response should be.
Response: Choose a single number from 1-100 using the following intervals as guide {intervals}
"""

B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"

SYSTEM_PROMPT = DEFAULT_SYSTEM_PROMPT

# Selecting the first and only text generation model available in palm
model = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.2,
)

# model = ChatVertexAI(model="gemini-pro")
