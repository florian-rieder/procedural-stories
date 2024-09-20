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

from typing import Any

from langchain_core.callbacks import StdOutCallbackHandler, BaseCallbackHandler, StreamingStdOutCallbackHandler



class StreamingLLMCallbackHandler(BaseCallbackHandler):
    """Callback handler for streaming LLM responses token by token."""

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        print('t')
        print(token, end='', flush=True)
    
    async def on_chat_model_start(*args: Any, **kwards: Any):
        # Implementation of on_chat_model_start is necessary !
        # But we don't need it.
        pass



def main(args):
    
    callback = StreamingStdOutCallbackHandler()
    conversation = get_chain(callback)

    print("Welcome to Interactive fiction procedural generation command line interface !"
          " Type your message to start chatting."
          " Type 'exit' to end the conversation.")

    do_conversation(conversation)

def do_conversation(conversation_chain):
    # Run the chat loop
    while True:
        user_input = input("Player: ")
        if user_input.lower() == 'exit':
            return

        conversation_chain.invoke(user_input)
        # for chunk in conversation_chain.stream(user_input):
        #     print(chunk['response'], end='', flush=True)
        print('\n')


if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Interactive fiction's command line interface")
    parser.add_argument('-c', '--context')
    args = parser.parse_args()

    main(args)
