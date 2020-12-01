# settings.py
from dotenv import load_dotenv, find_dotenv, dotenv_values
# OR, the same with increased verbosity

def load_env():
    load_dotenv(find_dotenv(), verbose=True)
