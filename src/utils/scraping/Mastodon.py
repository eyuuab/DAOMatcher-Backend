import requests
from bs4 import BeautifulSoup
from src.utils.scraping import MASTEDON_BASE_URL, TIMEOUT


class Mastodon:
    def extractText(self, html):
        soup = BeautifulSoup(html, features="html.parser")
        return soup.getText()

    # These function specific to Mastodon Scraping

    def getProfile(self, server, acc, webfinger=False, searchServer="mastodon.social"):
        # Change the searching server if webfinger is enabled
        BASE_URL = MASTEDON_BASE_URL.format(
            server=searchServer if webfinger else server
        )
        try:
            # Setting the search param based on the type of search
            # When webfinger is True, mastodon will search for the user's server from the current server itself. If not it will just try to find the user itself from the server
            acc = "@" + "@".join([acc, server]) if webfinger else acc
            # print(f"\033[92;1m{BASE_URL}/lookup?acct={acc}.\033[0m\n")
            response = requests.get(f"{BASE_URL}/lookup?acct={acc}", timeout=TIMEOUT)
            response.raise_for_status()
            # print(f"\033[93;1mUser Profile found.\033[0m\n")
            return response.json()

        except requests.exceptions.Timeout as errt:
            print(f"\033[91;1mRequest timed out after {TIMEOUT} seconds.\033[0m\n")
            return False

        except requests.exceptions.RequestException as errh:
            print(f"\033[91;1m{errh}.\033[0m\n")
            print(f"\033[94;1mRetrying with a different Server...\033[0m\n")
            if (
                (errh.response != None)
                and (errh.response.status_code == 404)
                and (not webfinger)
            ):
                return self.getProfile(
                    server=server,
                    acc=acc,
                    webfinger=True,
                )
            return False
        except Exception as e:
            print(f"\033[91;1m{e}.\033[0m\n")
            return False

    def getFollowers(self, server, id, webfinger=False, searchServer="mastodon.social"):
        BASE_URL = MASTEDON_BASE_URL.format(
            server=searchServer if webfinger else server
        )

        try:
            # print(f"\033[92;1m{BASE_URL}/{id}/following\033[0m\n")
            response2 = requests.get(f"{BASE_URL}/{id}/following", timeout=TIMEOUT)
            response2.raise_for_status()
            # print(f"\033[93;1mUser Followers found.\033[0m\n")
            # print(len(response2.json()))
            return response2.json()

        except requests.exceptions.Timeout as errt:
            print(f"\033[91;1mRequest timed out after {TIMEOUT} seconds.\033[0m\n")
            return {}

        except requests.exceptions.RequestException as errh:
            print(f"\033[91;1m{errh}.\033[0m\n")
            print(f"\033[94;1mRetrying with a different Server...\033[0m\n")
            if (
                (errh.response != None)
                and (errh.response.status_code == 404)
                and (not webfinger)
            ):
                return self.getFollowers(
                    server=server,
                    id=id,
                    webfinger=True,
                )
            return {}
        except Exception as e:
            print(f"\033[91;1m{e}.\033[0m\n")
            return {}

    def getContent(self, server, id, webfinger=False, searchServer="mastodon.social"):
        BASE_URL = MASTEDON_BASE_URL.format(
            server=searchServer if webfinger else server
        )
        try:
            # print(f"\033[92;1m{BASE_URL}/{id}/statuses?exclude_replies=true\033[0m\n")
            response = requests.get(
                f"{BASE_URL}/{id}/statuses?exclude_replies=true", timeout=TIMEOUT
            )
            response.raise_for_status()

            # print(f"\033[93;1mUser Content found.\033[0m\n")
            return response.json()

        except requests.exceptions.Timeout as errt:
            print(f"\033[91;1mRequest timed out after {TIMEOUT} seconds.\033[0m\n")
            return {}

        except requests.exceptions.RequestException as errh:
            print(f"\033[91;1m{errh}.\033[0m\n")
            print(f"\033[94;1mRetrying with a different Server...\033[0m\n")
            if (
                (errh.response != None)
                and (errh.response.status_code == 404)
                and (not webfinger)
            ):
                return self.getFollowers(
                    server=server,
                    id=id,
                    webfinger=True,
                )
            return {}
        except Exception as e:
            print(f"\033[91;1m{e}.\033[0m\n")
            return {}
