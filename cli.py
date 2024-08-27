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
import asyncio

from langchain.chains import ConversationChain
from langchain.callbacks import StdOutCallbackHandler

from story import get_chain

loop = asyncio.get_event_loop()


def main(args):
    conversation = get_chain()

    print("Welcome to Interactive fiction procedural generation command line interface !"
          " Type your message to start chatting."
          " Type 'exit' to end the conversation.")

    # see https://stackoverflow.com/a/68372199
    loop.run_until_complete(do_conversation(conversation))

async def do_conversation(conversation_chain):
    # Run the chat loop
    while True:
        user_input = input("Player: ")
        if user_input.lower() == 'exit':
            return

        async for chunk in conversation_chain.astream(user_input):
            print(chunk['response'], end='', flush=True)
        print('\n')


if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Interactive fiction's command line interface")
    parser.add_argument('-c', '--context')
    args = parser.parse_args()

    main(args)
