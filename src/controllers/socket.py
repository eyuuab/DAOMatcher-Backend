import requests

from flask import request
from flask_socketio import disconnect

from src.controllers.search_result import add_search_result
from src.extensions import socketio
from src.globals import USERS, Sessions
from src.utils.serverLogic.ScoreUsers import ScoreUsers
from src.utils.utils import (
    emitData,
    generate_random_string,
    set_user_session,
    validate_data,
)


def connect(user_id: str):
    # user_id = generate_random_string()
    USERS[user_id] = request.sid
    print("users: ", USERS)
    print("User connected with user_id: ", user_id)

    scoreUsers = ScoreUsers()
    Sessions[user_id] = scoreUsers
    emitData(socketio, "set_cookie", user_id, room=request.sid)


def get_users(user_id: str, data):
    if user_id == None:
        print(f"\033[91mUser id not found\033[0m")
        emitData(
            socketio,
            "something_went_wrong",
            {"message": "User id not found", "status": 400},
            room=request.sid,
        )
        return
    jsonRequest = data
    print(f"\033[94mReceived Data: {jsonRequest}\033[0m")
    sessionIsSet, current_user = set_user_session(user_id)
    valid = validate_data(data)
    if not sessionIsSet:
        print(f"\033[91mSession not set\033[0m")
        emitData(
            socketio, "resend_search", {"message": "Session not set"}, room=request.sid
        )
        return
    if not valid:
        if current_user:
            emitData(
                socketio,
                "something_went_wrong",
                {
                    "message": "Error data sending",
                    "status": 400,
                },
                room=current_user,
            )
        print(f"\033[91mError emitted\033[0m")
        return

    print(f"\033[94mCurrent_user:  {current_user}\033[0m")
    query = jsonRequest.get("query")
    user_list = jsonRequest.get("user_list")
    user_limit = jsonRequest.get("user_limit")
    depth = jsonRequest.get("depth")

    try:
        scoreUsers = Sessions.get(user_id)
        result = scoreUsers.scour(user_list, query, user_limit, depth)
        users = []
        for r in result:
            score, handle, userInfo = r
            users.append(
                {
                    "id": userInfo["id"],
                    "username": userInfo["username"],
                    "name": userInfo["name"],
                    "score": score,
                    "handle": handle,
                    "image": userInfo["image"],
                    "social_media": userInfo["social_media"],
                }
            )
        print(f"\033[94mTotal results: {len(users)} \033[0m")
        if users:
            data = {"result": users}
            search_result = {
                "found_users": users,
                "seed_users": user_list,
                "description": query,
            }
            response, status = add_search_result(user_id, search_result)

            # Error should be reported before sending the final result since the frontend will close the connection once the final result is sent
            if not response.json.get("success"):
                print("response: ", response.json, " status: ", status)
                emitData(
                    socketio,
                    "search_error",
                    {"message": "Couldn't save search history", "status": status},
                    room=current_user,
                )
                print(f"\033[91mError emitted\033[0m")

            if current_user:
                emitData(socketio, "search", data, room=current_user)
                disconnect()  # Disconnect the user after sending the result
                print("Disconnecting the user after sending the result")
                return
            else:
                print(f"\033[91mNo session found: {result}\033[0m")
                return

        print(f"\033[91mNo results found: {result}\033[0m")

        emitData(
            socketio,
            "search_error",
            {"message": "No search results found due to network error", "status": 500},
            room=current_user,
        )
        disconnect()  # Disconnect the user after sending the result
        return

    except requests.exceptions.RequestException as e:
        response = e.response
        if response != None:
            error = e.response.json()["error"]
            print(f"\033[91mError from RequestException: {error}\033[0m")
            emitData(
                socketio,
                "something_went_wrong",
                {"message": str(error), "status": 502},
                room=current_user,
            )
            disconnect()  # Disconnect the user after sending the result
        else:
            print(f"\033[91mError from ResponseException but no error reported\033[0m")
            emitData(
                socketio,
                "something_went_wrong",
                {"message": "The LLM server isn't responding", "status": 503},
                room=current_user,
            )
            disconnect()  # Disconnect the user after sending the result
        return

    except Exception as e:
        print(f"\033[91;1m{e}.\033[0m\n")
        emitData(
            socketio,
            "something_went_wrong",
            {"message": "Internal server error"},
            room=current_user,
        )
        disconnect()  # Disconnect the user after sending the result
        return
