from dotenv import load_dotenv
import requests
import os
import urllib.parse
import json

#Loading api key from environment file
# load_dotenv() # Uncomment for debugging
# print(api_key) # Uncomment for debugging

api_key = os.getenv("LIX_API_KEY")
payload={}
headers = {
  'Authorization': api_key
}

def handleException(response:requests.Response):
  if response.ok:
    return json.loads(response.text)
  else:
    print(response.text)
    error = json.loads(response.text)
    raise Exception(f"Lix Error: {error['error']['message']}")

#Used to get user information displayed on the profile page of the user. 
#Username used here is the handle LinkedIn uses to identify the user publicly
#It can be found from the link on the user profile
#i.e alfie-lambert
def getLinkedInProfile(username):
  
  url = f"https://api.lix-it.com/v1/person?profile_link=https://linkedin.com/in/{username}"

  response = requests.request("GET", url, headers=headers, data=payload)
  userInfo = handleException(response)
  return userInfo
    

#Get user Connections(Followers)
def getConnections(username, count):
  url = f"https://api.lix-it.com/v1/connections?count={count}&start=0&viewer_id={username}"
  response = requests.request("GET", url, headers=headers, data=payload)
  userConns = handleException(response)
  
  if "elements" in userConns:
    userConns = userConns["elements"]
  else:
    userConns = []
    
  return userConns

#Supposed to fetch email address but doesn't work as expected
def getEmail(username):
  url = f"https://api.lix-it.com/v1/contact/email/by-linkedin?url=https://linkedin.com/in/{username}"
  
  response = requests.request("GET", url, headers=headers, data=payload)
  userEmails = handleException(response)
  return userEmails

#Given the linked in url of a profile this function returns the public linkedin id
#i.e from https://www.linkedin.com/in/yeabesera-derese-7a9075224 returns yeabesera-derese-7a9075224
def getUsername(link):
    return link.split("/")[-1]

def getSaleNavId(salesNavLink):
  #Extracting user sales navigation link given the user information json
  salesNavLink = salesNavLink.split("lead")[1]
  
  #Sales navigation Id is used by linkedIn to identify posts made by a user
  salesNavigationID = salesNavLink.split("/")[-1].split(",")[0]
  return salesNavigationID

#Given the userInfo returned from user profile,
#this function can return the posts made by a user
def getUserPosts(userInfo):
  salesNavigationID = getSaleNavId(userInfo["salesNavLink"])
  postUrl = f'https://www.linkedin.com/search/results/content/?fromMember={salesNavigationID}&origin=SWITCH_SEARCH_VERTICAL&sid=G;z'
  postUrl = urllib.parse.quote(postUrl, safe='')
  
  url = f"https://api.lix-it.com/v1/li/linkedin/search/posts?url={postUrl}"
  
  # print(postUrl) #Uncomment this for debugging
  print(url) #Uncomment this for debugging
  
  response = requests.request("GET", url, headers=headers, data=payload)
  userPosts = handleException(response)
  
  if "posts" in userPosts:
    userPosts = userPosts["posts"]
  else: 
    userPosts = []
  
  return userPosts




