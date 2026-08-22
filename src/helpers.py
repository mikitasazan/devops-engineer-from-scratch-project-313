import os


def generate_short_link(short_name: str = None) -> str:
    return f"{os.environ['BASE_URL']}/r/{short_name}"


def push_error(errors, target: list[str], msg: str):
    errors.append(
        {
            "loc": target,
            "msg": msg,
        }
    )
