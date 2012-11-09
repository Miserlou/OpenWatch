import re

def validate_email(potential_email):
    if re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", potential_email):
        return True
    else:
        return False
