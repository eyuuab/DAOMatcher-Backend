from flask import Blueprint, jsonify

from src.controllers.auth import login
from src.controllers.user import (
    request,
    get_user_by_id_response,
    update_user,
    add_user,
    update_user_usage,
)
from src.utils.decorators import authorize, token_required

user = Blueprint("user", __name__)
base_url = "/api/user"


@user.route(f"{base_url}/<string:user_id>", methods=["GET", "PUT"])
@token_required
@authorize
def get(current_user: dict, user_id):

    if request.method == "GET":
        response = get_user_by_id_response(user_id)
        return response
    elif request.method == "PUT":
        response = update_user(user_id)
        return response


@user.route(f"{base_url}/<string:user_id>/usage/<string:usage_id>", methods=["PUT"])
@token_required
@authorize
def update_usage(current_user: dict, user_id: str, usage_id: str):
    response = update_user_usage(usage_id)
    return response
