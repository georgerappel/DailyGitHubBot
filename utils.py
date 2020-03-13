import re


def is_username_valid(username):
    username = username.lower()
    return re.fullmatch(r"^[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}", username) is not None