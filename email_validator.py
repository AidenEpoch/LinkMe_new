import re

EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"[A-Za-z]{2,63}$"
)


def is_valid_email(email):
    if not isinstance(email, str):
        return False

    if len(email) > 254:
        return False

    if not EMAIL_PATTERN.fullmatch(email):
        return False

    local_part, domain = email.rsplit("@", 1)

    if len(local_part) > 64:
        return False

    if local_part.startswith(".") or local_part.endswith("."):
        return False

    if ".." in local_part:
        return False

    return True
