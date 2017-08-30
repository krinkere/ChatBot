from flask import Flask, render_template, request, jsonify
from chatbot_init import give_bot_personality
import aiml
import os

app = Flask(__name__)
global bot_kernel


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

    while True:
        if message == "quit":
            exit()
        else:
            chatbot_response = bot_kernel.respond(message)
            return jsonify({'status': 'OK', 'answer': chatbot_response})


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
