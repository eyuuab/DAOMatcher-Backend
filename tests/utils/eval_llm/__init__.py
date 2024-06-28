import logging
from decouple import config
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from src.utils.serverLogic import twitter, mastodon
from urllib.parse import urlparse

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)

logger.addHandler(handler)


load_dotenv()
GOOGLE_API_KEY = config("PALM_API_KEY")
SYSTEM_PROMPT = """
    Task: Rate the accuracy and relevance of the provided RAG output in the context of the given topic and user data summary. Higher scores indicate a more accurate, relevant, and well-supported RAG output.
    Output:
        Response: After stating the accuracy, relevance and coherence, based on the provided information, give a response by saying Yes if the overall requirements have been met and the score is what it ought to be, otherwise respond by a simple No. Your last output should be marked by a delimiter 'Overall: ' 
"""


ACTIONS = [
    "Search for explicit mentions of the topic in the user data",
    "Search for indication of interest in the topic from the user data",
    "Search for topics that could belong to the same category as the given topic",
    "Pick a number from the interest levels matching the user's interest in the topic of question",
    "Compare {score} with the number you have picked and Return Yes if they are close to eachother. Otherwise Return No",
]
INSTRUCTION = """
    You are an expert tester who would be interested in a certain topic.
    Your task is to evaluate the accuracy, relevance and coherence of a topic in relation to user data provided in the following form and judge whether the score provided is in the appropriate range for the given topic vs user data:    


Use the following format:
Question: The topic the human asked you

Thought: you should always think about what to do
Action: the action to take, should be one of {actions}
Action Input: the input to the action
Observation: verbal description of what you learned after performing the above action
(... this pattern 'Thought/Action/Action Input/Observation' can be repeated N times as needed)

Analysis: your analysis of the user's interest based on Explicit mentions, Indications of interest and similar topics or field of work to the given topic
Observation: What you learned after performing the above action and what led to such conclusion

Accuracy: Your numerical evaluation of the accuracy of the RAG output. You should only output number from 1 - 100 nothing else.
Relevance: Your numerical evaluation of the relevance of the RAG output. You should only output number from 1 - 100 nothing else.
Overall: Your final evaluation of the RAG output as a Yes or No

    Input:
        Topic: {topic}
        User Data: {user_data}
        Score: {score}
"""


InterestLevels = [
    "The user's posts talks about completely different topic and show no interest in the topic given = 10-20",
    "The user's posts talks about completely different topic but those topics might have something in common with the topic in question = 20-30",
    "The user's posts talks about topics that can be under the same category and might be interested in the topic = 30-60",
    "The user's posts shows clear signs of being interested in the topic in question = 60-80",
    "The user's posts mention the topic in question and suggest a high likelihood of being interested in the topic = 80-100",
]


def is_link(string):
    try:
        parsed_url = urlparse(string)
        return parsed_url.scheme in ["http", "https"] and parsed_url.netloc != ""
    except ValueError:
        return False


def get_userdata(username, account_type, mastodon_server=None):
    if account_type == "Twitter":
        profile = twitter.getTwitterProfile(username)

        if profile:
            content = []

            if "description" in profile and profile["description"]:
                content.append(profile["description"])

            for p in twitter.getUserPosts(profile["id"], 10):
                if "text" in p and p["text"]:
                    content.append(p["text"])

            content = "\n\n------------------\n".join(content)

            return content
        return None

    elif account_type == "Linkedin":
        pass
    elif account_type == "Mastodon":
        profile = mastodon.getProfile(mastodon_server, username)
        # print(profile)
        if profile:
            content = []
            # print(id)
            if "note" in profile:
                content.append(mastodon.extractText(profile["note"]))
                # print(content[-1])
            for c in mastodon.getContent(mastodon_server, profile["id"]):
                if "content" in c and c["content"]:
                    text = mastodon.extractText(c["content"])
                    # Added filter to check if content is only link
                    if not is_link(text):
                        content.append(text)
                    # print(content[-1])
            content = "\n\n------------------\n".join(content)
            # print(f"Profile: {profile}")
            user = {
                "id": profile["id"],
                "name": profile["display_name"],
                "username": profile["username"],
                "image": profile["avatar"],
                "social_media": "mastodon",
            }
            # print(content)
            return content
        return None


def get_rag_output(score):
    if score <= 20:
        return "Different topic, Not Interested"
    elif score <= 30:
        return "Different topic, Might have something in common"
    elif score <= 60:
        return "Topics can be under the same category, Might be interested"
    elif score <= 80:
        return "Clear sign of being interested"
    elif score <= 100:
        return "High likelihood of being interested"


model = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.0,
)
