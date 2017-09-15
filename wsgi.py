# gunicorn can't find app when it is not named application
from chatbot import app as application


if __name__ == "__main__":
    application.run()
