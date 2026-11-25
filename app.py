"""Run the chatbot locally with: flask --app app run --debug"""
from dotenv import load_dotenv

load_dotenv()

from api.chat import app
from flask import send_from_directory


@app.get("/")
def home():
    return send_from_directory("public", "index.html")
