"""Small Firestore REST API wrapper used by the SMTP and POP3 servers."""

import requests


PROJECT_ID = "email-proxy-simulator"
BASE_URL = (
    f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}"
    "/databases/(default)/documents"
)
EMAILS_URL = f"{BASE_URL}/emails"
REQUEST_TIMEOUT = 10


def add_email(sender, receiver, subject, message):
    data = {
        "fields": {
            "sender": {"stringValue": sender},
            "receiver": {"stringValue": receiver},
            "subject": {"stringValue": subject},
            "message": {"stringValue": message},
            "status": {"stringValue": "unread"},
        }
    }

    try:
        response = requests.post(
            EMAILS_URL, json=data, timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"Could not store email: {error}")
        return False

    print("Email stored successfully!")
    return response.json()


def get_emails(receiver):
    try:
        response = requests.get(EMAILS_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"Could not read emails: {error}")
        return []

    documents = response.json().get("documents", [])
    return [
        document
        for document in documents
        if document.get("fields", {}).get("receiver", {}).get("stringValue")
        == receiver
    ]


def delete_email(document):
    document_name = document.get("name")
    if not document_name:
        return False

    try:
        response = requests.delete(
            f"https://firestore.googleapis.com/v1/{document_name}",
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"Could not delete email: {error}")
        return False

    return True
