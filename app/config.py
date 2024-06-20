import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
