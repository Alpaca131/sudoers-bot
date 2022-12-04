import os

from dotenv import load_dotenv

if os.path.isfile('.env'):
    load_dotenv()

TOKEN = os.environ['TOKEN']
