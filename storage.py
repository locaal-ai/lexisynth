import json
import os
from platformdirs import user_data_dir


def store_data(file_path, document_name, data):
    # Store data into a JSON file
    # get the user data directory
    data_dir = user_data_dir("lexisynth")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # prepend the user data directory
    file_path = os.path.join(data_dir, file_path)

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                documents = json.load(f)
            except json.JSONDecodeError:
                documents = {}
    else:
        documents = {}

    if document_name in documents and isinstance(documents[document_name], dict):
        documents[document_name].update(data)
    else:
        documents[document_name] = data

    with open(file_path, "w") as f:
        json.dump(documents, f, indent=2)


def remove_data(file_path, document_name):
    # Remove data from a JSON file
    # prepend the user data directory
    file_path = os.path.join(user_data_dir("lexisynth"), file_path)

    if not os.path.exists(file_path):
        return

    with open(file_path, "r") as f:
        documents = json.load(f)

    if document_name in documents:
        del documents[document_name]

    with open(file_path, "w") as f:
        json.dump(documents, f, indent=2)


def fetch_data(file_path, document_name, default=None):
    # Fetch data from a JSON file
    # prepend the user data directory
    file_path = os.path.join(user_data_dir("lexisynth"), file_path)

    if not os.path.exists(file_path):
        return default

    with open(file_path, "r") as f:
        try:
            documents = json.load(f)
        except json.JSONDecodeError:
            return default

    if document_name in documents:
        return documents[document_name]
    else:
        return default
