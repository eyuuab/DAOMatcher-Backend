from flask import Blueprint

from src.controllers.auth import login, confirm_email, resend_token
from src.utils.middlewares import token_required

auth = Blueprint("auth", __name__)
base_url = "/api/auth"


@auth.route(f"{base_url}/login", methods=["POST"])
def handle_login():
    response = login()
    return response, response.get("status")


@auth.route(f"{base_url}/confirm/<token>", methods=["GET"])
@token_required
def confirm(current_user: dict, token: str):
    response = confirm_email(current_user, token)
    return response, response.get("status")


@auth.route(f"{base_url}/confirm/resend", methods=["GET"])
@token_required
def resend_confirmation(current_user: dict):
    response = resend_token(current_user)
    return response, response.get("status")
