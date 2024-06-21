from datetime import datetime, timezone, timedelta
import jwt
import bcrypt

from decouple import config
from flask import jsonify, make_response, request

from src.controllers.user import get_user_by_email
from src.extensions import db
from src.models.user import User

from src.utils.token import confirm_token, generate_and_send
from src.utils.utils import generate_access_token, generate_refresh_token


def login(body: dict = None):
    try:
        data = request.json if not body else body
        if not data:
            return (
                jsonify(
                    {
                        "message": "Please provide user details",
                        "data": None,
                        "error": "Bad request",
                        "success": False,
                    }
                ),
                400,
            )

        is_validated, user = False, None
        error = None

        try:
            is_validated, user = validate_credentials(
                data.get("email"), data.get("password")
            )
        except Exception as e:
            error = str(e)

        if not is_validated:
            return (
                jsonify(
                    {
                        "message": "Invalid credentials",
                        "data": None,
                        "error": error,
                        "success": False,
                    }
                ),
                401,
            )

        if user:

            try:
                access_token = generate_access_token(user.id)
                print("Token on login   ", access_token)

                refresh_token = generate_refresh_token(user.id)
                response = make_response(
                    jsonify(
                        {
                            "message": "Login successful",
                            "data": {"user": user.serialize(), "token": access_token},
                            "error": None,
                            "success": True,
                        },
                    )
                )

                expiry_day = int(config("REFRESH_TOKEN_EXPIRY_IN_DAYS", 1))
                expiry_date = datetime.now() + timedelta(days=expiry_day)

                response.set_cookie(
                    "refresh_token",
                    refresh_token,
                    secure=True,
                    httponly=True,
                    expires=expiry_date,
                    samesite='None'
                )

                return response, 200

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
        return (
            jsonify(
                {
                    "message": "Unauthorized",
                    "data": None,
                    "error": "Error fetching auth token!, invalid email or password",
                    "success": False,
                }
            ),
            401,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "message": "Something went wrong!",
                    "error": str(e),
                    "data": None,
                    "success": False,
                }
            ),
            500,
        )


def handle_google_signin(data):
    try:
        email = data.get("email")
        display_name = data.get("name")

        if not email or not display_name:
            return (
                jsonify(
                    {
                        "message": "Email and name are required",
                        "data": None,
                        "error": "Bad request",
                        "success": False,
                    }
                ),
                400,
            )

        # Check if the user exists
        found_user = get_user_by_email(email)
        if found_user:
            found_user.verified = True  # Mark user as verified
            db.session.commit()
            return login_with_google(found_user)

        # Create a new user since it does not exist
        user = User(
            display_name=display_name,
            email=email,
            api_key=None,
            password=None,  # No password since using Google for authentication
            password_salt=None,
            verified=True,  # Mark new user as verified
        )

        db.session.add(user)
        db.session.commit()

        return login_with_google(user)

    except Exception as e:
        # print("Error from sign up google: ", e)
        return (
            jsonify(
                {
                    "message": "Something went wrong!",
                    "error": str(e),
                    "data": None,
                    "success": False,
                }
            ),
            500,
        )


def login_with_google(user):
    try:
        access_token = generate_access_token(user.id)
        refresh_token = generate_refresh_token(user.id)
        response = make_response(
            jsonify(
                {
                    "message": "Login successful",
                    "data": {"user": user.serialize(), "token": access_token},
                    "error": None,
                    "success": True,
                },
            )
        )

        response.set_cookie("refresh_token", refresh_token, secure=True, httponly=True)

        return response, 200

    except Exception as e:
        # print("Error from google login: ", e)
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


def validate_credentials(email: str, password: str):
    if not email or not password:
        raise Exception("Invalid email or password")

    user = get_user_by_email(email)
    if not user:
        raise Exception("User not found")

    hashed_password = user.password.encode("utf-8")
    salt = user.password_salt.encode("utf-8")
    password = password.encode("utf-8")

    hashed_password_with_salt = bcrypt.hashpw(password, salt)

    valid_credential = hashed_password_with_salt == hashed_password

    return valid_credential, user


def confirm_email(current_user: dict, token: str):
    try:
        if current_user.get("verified", False):
            return (
                jsonify(
                    {
                        "message": "Email already verified",
                        "data": None,
                        "error": None,
                        "success": False,
                    }
                ),
                400,
            )

        email = confirm_token(token)
        user = get_user_by_email(current_user.get("email"))

        if user and user.email == email:
            user.verified = True
            db.session.add(user)
            db.session.commit()
            return jsonify(
                {
                    "message": "Email verified",
                    "data": None,
                    "error": None,
                    "success": True,
                }
            )
        else:
            return (
                jsonify(
                    {
                        "message": "Invalid token",
                        "data": None,
                        "error": "Unauthorized",
                        "success": False,
                    }
                ),
                401,
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

def resend_token(current_user: dict):
    if current_user.get("verified", False):
        return (
            jsonify(
                {
                    "message": "Email already verified",
                    "data": None,
                    "error": None,
                    "success": False,
                }
            ),
            400,
        )

    generate_and_send(current_user.get("email"))
    return jsonify(
        {
            "message": "Confirmation email sent",
            "data": None,
            "error": None,
            "success": True,
        }
    )


def refresh_token():
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        return (
            jsonify(
                {
                    "message": "Refresh token not found",
                    "data": None,
                    "error": None,
                    "success": False,
                }
            ),
            401,
        )

    try:
        payload = jwt.decode(refresh_token, config("SECRET_KEY"), algorithms=["HS256"])
        user_id = payload["sub"]
    except jwt.ExpiredSignatureError:
        return (
            jsonify(
                {
                    "message": "Refresh token expired",
                    "data": None,
                    "error": None,
                    "success": False,
                }
            ),
            401,
        )
    except jwt.InvalidTokenError:
        return (
            jsonify(
                {
                    "message": "Invalid token",
                    "data": None,
                    "error": None,
                    "success": False,
                }
            ),
            401,
        )

    user = db.session.query(User).filter_by(id=user_id).first()

    if not user:
        return (
            jsonify(
                {
                    "message": "User not found",
                    "data": None,
                    "error": None,
                    "success": False,
                }
            ),
            404,
        )

    access_token = generate_access_token(user.id)

    print("Token on refresh ", access_token)

    return jsonify(
        {
            "message": "Token refreshed",
            "data": {"token": access_token},
            "error": None,
            "success": True,
        }
    )
