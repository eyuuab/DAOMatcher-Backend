import bcrypt
from flask import request, jsonify

from sqlalchemy.exc import DatabaseError, IntegrityError
from src.extensions import db
from src.models import User, UserUsage
from src.utils.token import generate_and_send, generate_reset_token_send
from typing import Union


def get_user_by_id_response(user_id: str):
    user: User = get_user_by_id(user_id)
    return jsonify(
        {
            "message": "User Found",
            "data": user.serialize(),
            "error": None,
            "success": False,
            "success": True,
        }
    )


def get_user_by_id(user_id: str) -> Union[User, None]:
    user: User = User.query.filter_by(id=user_id).first()
    return user


def get_user_by_email(email: str) -> Union[User, None]:
    user: User = User.query.filter_by(email=email).first()
    return user

def request_password_reset():
    try:
        update_user = request.json
        email = update_user.get('email')
        if not email:
            return jsonify({"message": "Email is required", "success": False}), 400

        user = get_user_by_email(email)
        if not user:
            return jsonify({"message": "User not found", "success": False}), 404

       
        generate_reset_token_send(email)
        db.session.commit()


        return jsonify({"message": "Password reset email sent successfully", "success": True}), 200
    except Exception as e:
        return jsonify({"message": "Something went wrong", "error": str(e), "success": False}), 500


def add_user():
    try:
        new_user = request.json

        found_user = get_user_by_email(new_user.get("email"))
        if found_user is not None:
            return (
                jsonify(
                    {
                        "message": "User with email already exists",
                        "data": None,
                        "token": "",
                        "error": "Duplicate user error",
                        "success": False,
                    }
                ),
                409,
            )

        user: User = User(
            display_name=new_user.get("display_name"),
            api_key=new_user.get("api_key"),
            email=new_user.get("email"),
        )

        usage: UserUsage = UserUsage()
        user.user_usage = usage

        password = new_user.get("password").encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password, salt)

        user.password = hashed_password.decode("utf-8")
        user.password_salt = salt.decode("utf-8")

        db.session.add(user)
        db.session.commit()

        generate_and_send(user.email)

        return (
            jsonify(
                {
                    "message": "User added Successfully",
                    "data": user.serialize(),
                    "token": "",
                    "error": None,
                    "success": True,
                }
            ),
            201,
        )

    except IntegrityError as e:
        error_message = "Invalid data provided"
        return (
            jsonify(
                {
                    "message": error_message,
                    "data": None,
                    "error": str(e),
                    "success": False,
                }
            ),
            400,
        )
    except DatabaseError as e:
        error_message = "Something went wrong while adding data"
        return (
            jsonify(
                {
                    "message": error_message,
                    "data": None,
                    "error": str(e),
                    "success": False,
                }
            ),
            500,
        )

    except Exception as e:
        error_message = "Something went wrong"
        return (
            jsonify(
                {
                    "message": error_message,
                    "data": None,
                    "error": str(e),
                    "success": False,
                }
            ),
            500,
        )


def update_user(user_id: str):
    try:
        updatedUser = request.json
        user: User = db.one_or_404(
            db.select(User).filter_by(id=user_id), description="User not found"
        )

        user.display_name = updatedUser.get("display_name", user.display_name)
        user.api_key = updatedUser.get("api_key", user.api_key)

        db.session.commit()

        return jsonify(
            {
                "message": "User updated Successfully",
                "data": user.serialize(),
                "error": None,
                "success": False,
                "success": True,
            }
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "message": "Something went wrong",
                    "data": None,
                    "error": str(e),
                    "success": False,
                }
            ),
            500,
        )


def update_user_usage(usage_id):
    try:
        updatedUsage = request.json
        usage: UserUsage = db.one_or_404(
            db.select(UserUsage).filter_by(id=usage_id), description="Usage not found"
        )

        usage.token_count = updatedUsage.get("token_count")
        usage.search_count = updatedUsage.get("search_count")

        db.session.commit()

        return jsonify(
            {
                "message": "Usage updated Successfully",
                "data": usage.serialize(),
                "error": None,
                "success": False,
                "success": True,
            }
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "message": "Something went wrong",
                    "data": None,
                    "error": str(e),
                    "success": False,
                }
            ),
            500,
        )
