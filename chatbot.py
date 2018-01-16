from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from chatbot_init import give_bot_personality
import aiml
import os
import logging
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///botchat_transcript.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

http_server = HTTPServer(WSGIContainer(app))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create a file handler
handler = logging.FileHandler('chatter.log')
handler.setLevel(logging.DEBUG)
# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(handler)


class BotChatTranscript(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(120))
    answer = db.Column(db.String(120))
    is_known = db.Column(db.Boolean)
    chat_date = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self, question, answer, is_known=True):
        self.question = question
        self.answer = answer
        self.is_known = is_known
        self.chat_date = datetime.datetime.now()

    def __repr__(self):
        return '[Question: %r][Answer: %r] asked on %r' % (self.question, self.answer, self.chat_date)


def initialize_chatbot():
    bot_kernel = aiml.Kernel()
    # If there is a brain file named brain.brn, Kernel() will initialize using bootstrap() method
    if os.path.isfile("brain.brn"):
        bot_kernel.bootstrap(brainFile="brain.brn")
    else:
        # If there is not brain file, load all AIML files and save a new brain
        bot_kernel.bootstrap(learnFiles=os.path.abspath("std-startup.xml"), commands="load aiml b")
        bot_kernel.saveBrain("brain.brn")

    give_bot_personality(kernel=bot_kernel)
    return bot_kernel


@app.route("/")
def chatbot():
    initialize_chatbot()
    return render_template('chatbot.html')

bot_kernel = initialize_chatbot()


@app.route("/ask", methods=['POST'])
def chat():
    message = str(request.form['messageText'])

    chatbot_response = bot_kernel.respond(message)

    is_known = True
    if chatbot_response == "Does not compute... Please refer to MPEP or ask your SPE!":
        logger.warn("Unknown question: '" + message + "'")
        is_known = False

    # Log and save to database for future analysis
    botchattranscript = BotChatTranscript(message.decode("utf-8"), chatbot_response.decode("utf-8"), is_known)
    logger.info(botchattranscript)
    db.session.add(botchattranscript)
    db.session.commit()

    return jsonify({'status': 'OK', 'answer': chatbot_response})


if __name__ == "__main__":
    # Run this for development
    http_server.listen(5000)
    IOLoop.instance().start()
    # Run this on production to get gunicorn going. Make sure to displace debug, it would cache stuff?
    # app.run(host='0.0.0.0', debug=False)
