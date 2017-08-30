import aiml
import webbrowser
import sys
import os
from chatbot_init import give_bot_personality

# The Kernel object is the public interface to
# the AIML interpreter.
k = aiml.Kernel()

# If there is a brain file named brain.brn, Kernel() will initialize using bootstrap() method
if os.path.isfile("brain.brn"):
    k.bootstrap(brainFile="brain.brn")
else:
    # If there is not brain file, load all AIML files and save a new brain
    k.bootstrap(learnFiles="std-startup.xml", commands="load aiml b")
    k.saveBrain("brain.brn")

give_bot_personality(kernel=k)

# Loop forever, reading user input from the command
# line and printing responses.
while True:
    input = raw_input("User: ")
    if input == "quit":
        sys.exit(0)
    response = k.respond(input)
    print 'Bot: ', response

    if response == "starting browser":
        url = 'http://docs.python.org/'
        webbrowser.open(url)

