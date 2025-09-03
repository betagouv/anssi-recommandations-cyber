import os

ALBERT_API_KEY = os.getenv("ALBERT_API_KEY")
assert ALBERT_API_KEY, "ALBERT_API_KEY doit être définie"
