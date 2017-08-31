from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from chatbot_init import give_bot_personality
import aiml
import os
import logging
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

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

global bot_kernel


class BotChatTranscript(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(120))
    answer = db.Column(db.String(120))

    def __init__(self, question, answer):
        self.question = question
        self.answer = answer

    def __repr__(self):
        return '[Question: %r][Answer: %r]' % (self.question, self.answer)


def initialize_chatbot():
    global bot_kernel
    bot_kernel = aiml.Kernel()
    # If there is a brain file named brain.brn, Kernel() will initialize using bootstrap() method
    if os.path.isfile("brain.brn"):
        bot_kernel.bootstrap(brainFile="brain.brn")
    else:
        # If there is not brain file, load all AIML files and save a new brain
        bot_kernel.bootstrap(learnFiles=os.path.abspath("std-startup.xml"), commands="load aiml b")
        bot_kernel.saveBrain("brain.brn")

    give_bot_personality(kernel=bot_kernel)


@app.route("/")
def chatbot():
    initialize_chatbot()
    return render_template('chatbot.html')


@app.route("/ask", methods=['POST'])
def chat():
    message = str(request.form['messageText'])
    global bot_kernel

    chatbot_response = bot_kernel.respond(message)

    # Log and save to database for future analysis
    botchattranscript = BotChatTranscript(message, chatbot_response)
    logger.info(botchattranscript)
    db.session.add(botchattranscript)
    db.session.commit()

    return jsonify({'status': 'OK', 'answer': chatbot_response})


if __name__ == "__main__":
    http_server.listen(5000)
    IOLoop.instance().start()
    # app.run(host='0.0.0.0', debug=True)
