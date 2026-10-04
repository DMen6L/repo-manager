from models import User


def greeting(name: str) -> str:
    user = User(name)
    return f"Hello, {user.name}!"
