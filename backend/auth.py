users = {
    "admin": "sample_password"
}


def authenticate(username, password) -> str:
    if password != "" and users.get(username, "") == password:
        return username
