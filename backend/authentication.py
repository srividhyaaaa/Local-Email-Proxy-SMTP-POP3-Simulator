"""User registration and login using the Firestore REST API."""

import hashlib
from urllib.parse import quote

import requests


PROJECT_ID = "email-proxy-simulator"
USERS_URL = (
    f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}"
    "/databases/(default)/documents/users"
)
REQUEST_TIMEOUT = 10


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _user_url(username):
    return f"{USERS_URL}/{quote(username, safe='')}"


def register_user(username, password, email):
    try:
        existing = requests.get(_user_url(username), timeout=REQUEST_TIMEOUT)
        if existing.status_code == 200:
            print("Username already exists.")
            return False
        if existing.status_code != 404:
            existing.raise_for_status()

        data = {
            "fields": {
                "username": {"stringValue": username},
                "password": {"stringValue": hash_password(password)},
                "email": {"stringValue": email},
            }
        }
        response = requests.patch(
            _user_url(username), json=data, timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"Registration failed: {error}")
        return False

    print("User registered successfully!")
    return True


def login_user(username, password):
    try:
        response = requests.get(_user_url(username), timeout=REQUEST_TIMEOUT)
        if response.status_code == 404:
            print("User not found.")
            return False
        response.raise_for_status()
        stored_password = (
            response.json().get("fields", {}).get("password", {}).get("stringValue")
        )
    except (requests.RequestException, ValueError) as error:
        print(f"Login failed: {error}")
        return False

    if stored_password == hash_password(password):
        print("Login successful!")
        return True

    print("Invalid password.")
    return False
