import requests
import time
from heapq import *
from collections import *
from urllib.parse import urlparse
from src.extensions import socketio
from src.utils.serverLogic import (
    mastodon,
    linkedIn,
    twitter,
    llm_server,
    LINKEDIN_PREFIX,
    TWITTER_PREFIX,
)
from src.utils.utils import emitData


class ScoreUsers:
    def __init__(self) -> None:
        self.cancel = False
        self.user_session = None

    def __store_items(self, item, limit, user_heap):
        if len(user_heap) == limit:
            heappushpop(user_heap, item)
        else:
            heappush(user_heap, item)

    def __is_link(self, string):
        try:
            parsed_url = urlparse(string)
            return parsed_url.scheme in ["http", "https"] and parsed_url.netloc != ""
        except ValueError:
            return False

    # Returns Mastodon user content and user in a dictionary of keys id, name, username
    def __get_mastodon_user(self, acc, server):
        profile = mastodon.getProfile(server, acc)
        if profile:
            content = []
            # print(id)
            if "note" in profile:
                content.append(mastodon.extractText(profile["note"]))
                # print(content[-1])
            for c in mastodon.getContent(server, profile["id"]):
                if "content" in c and c["content"]:
                    text = mastodon.extractText(c["content"])
                    # Added filter to check if content is only link
                    if not self.__is_link(text):
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
            return content, user
        return None, None

    # Returns LinkedIn user content and user in a dictionary of keys id, name, username
    def __get_linkedIn_user(self, username):
        profile = linkedIn.getLinkedInProfile(username)

        if profile:
            content = []

            if "aboutSummaryText" in profile and profile["aboutSummaryText"]:
                content.append(profile["aboutSummaryText"])

            for p in linkedIn.getUserPosts(profile):
                if "text" in p and p["text"]:
                    content.append(p["text"])

            content = "\n\n------------------\n".join(content)
            saleNavId = linkedIn.getSaleNavId(profile["salesNavLink"])
            username = linkedIn.getUsername(profile["link"])

            print("linkedIn found profile: ", profile)
            # TODO: Make sure to check whether the image's url is correct or not when you get the api key
            user = {
                "id": saleNavId,
                "name": profile["name"],
                "username": username,
                "image": profile.get("imageUrl", None),
                "social_media": "linkedIn",
            }

            return content, user
        return None, None

    def __get_twitter_user(self, username):
        profile = twitter.getTwitterProfile(username)

        if profile:
            content = []

            if "description" in profile and profile["description"]:
                content.append(profile["description"])

            for p in twitter.getUserPosts(profile["id"], 10):
                if "text" in p and p["text"]:
                    content.append(p["text"])

            content = "\n\n------------------\n".join(content)
            user = {
                "id": profile["id"],
                "name": profile["name"],
                "username": username,
                "image": profile["profile_image_url"],
                "social_media": "twitter",
            }

            return content, user
        return None, None

    def scour(self, starting_users, query, user_limit, depth):
        user_heap = []

        accounts = deque(starting_users)

        visited = set()
        count = 0
        self.cancel = False
        print(f"\033[92mUser from scour: {self.user_session}\033[0m")

        while (not self.cancel) and accounts and (count < depth):
            account = accounts.popleft()
            user = None

            # Organized logging for debugging purposes
            print(
                "\033[93;1m{:<15} {:<25} {:<8} {:<10}\033[0m".format(
                    "Processing: ", account, " From: ", len(account)
                )
            )
            try:
                username = None
                if (
                    "@" in account
                ):  # If it contains @ it is mastodon otherwise it is LinkedIn URL
                    _, acc, server = account.split("@")
                    content, user = self.__get_mastodon_user(acc, server)
                    # If there is no user found, no point in executing the rest of the code
                    if not user:
                        continue

                    # Get mastodon followers
                    for follower in mastodon.getFollowers(server, user["id"]):
                        username = follower["acct"]
                        if "@" in username:
                            username = "@" + username
                        else:
                            username = "@" + username + "@" + server

                        if username and username not in visited:
                            accounts.append(username)
                            visited.add(username)
                elif (
                    LINKEDIN_PREFIX in account
                ):  # If the username input contains a "li+" it is from linkedIn. This is a prefix used to identify which is which.
                    # It is going to be set from frontend for the starting users and here in the backend for the new users found
                    _, account = account.split(LINKEDIN_PREFIX)
                    content, user = self.__get_linkedIn_user(account)
                    time.sleep(4)

                    # If there is no user found, no point in executing the rest of the code
                    if not user:
                        continue

                    # Get followers for linkedIn
                    for follower in linkedIn.getConnections(account, 10):
                        username = follower["publicIdentifier"]
                        username = LINKEDIN_PREFIX + username

                        if username and username not in visited:
                            accounts.append(username)
                            visited.add(username)
                elif (
                    TWITTER_PREFIX in account
                ):  # If the username input contains a "tw+" it is from twitter. This is a prefix used to identify which is which.
                    # It is going to be set from frontend for the starting users and here in the backend for the new users found
                    _, account = account.split(TWITTER_PREFIX)
                    content, user = self.__get_twitter_user(account)

                    # If there is no user found, no point in executing the rest of the code
                    if not user:
                        continue

                    # Get followers for twitter
                    for follower in twitter.getFollowers(account, 1000):
                        username = follower["username"]
                        username = TWITTER_PREFIX + username

                        if username and username not in visited:
                            accounts.append(username)
                            visited.add(username)

            except Exception as e:
                print(f"\033[91;1m{e} In scour.\033[0m\n")
                emitData(socketio, f"update", {"error": str(e)}, room=self.user_session)

            if user:
                try:
                    if query and content:
                        score = llm_server.generate_search(query, content)["response"]
                        self.__store_items(
                            ((int(score), account, user)), user_limit, user_heap
                        )
                        # print(count)
                        count += 1
                        emitData(
                            socketio,
                            f"update",
                            {"progress": count, "curr_user": account},
                            room=self.user_session,
                        )
                        print(f"\033[94mEmitting to: {self.user_session}\033[0m")
                    else:
                        continue

                except requests.exceptions.RequestException as e:
                    emitData(
                        socketio, f"update", {"error": str(e)}, room=self.user_session
                    )
                except Exception as e:
                    emitData(
                        socketio, f"update", {"error": str(e)}, room=self.user_session
                    )
                    # raise Exception("Error encountered on storing the scores")
        self.user_session = None
        return user_heap
