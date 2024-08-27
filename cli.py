"""
This module provides a command line interface for the chat application

Usage
-----
>>> python cli.py

Example
-------
>>> python cli.py -s "Médiéval réaliste (9ème siècle), Normandie actuelle"
 
To end the conversation, type 'exit'.
"""

import argparse

from langchain.chains import ConversationChain
from langchain.callbacks import StdOutCallbackHandler

from story import get_chain


if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Interactive fiction's command line interface")
    parser.add_argument('-c', '--context')
    args = parser.parse_args()

    stream_handler = StdOutCallbackHandler()
    conversation = get_chain(stream_handler)

    print("Welcome to Interactive fiction procedural generation command line interface !"
          " Type your message to start chatting."
          " Type 'exit' to end the conversation.")

    # Run the chat loop
    while True:
        user_input = input("Player: ")
        if user_input.lower() == 'exit':
            break
        response = conversation.predict(input=user_input, context=args.context)
        print("Interactive fiction: " + response)
