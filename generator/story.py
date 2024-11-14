# https://python.langchain.com/v0.2/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html
import logging
import os
from typing import List, Optional

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import (
    ConfigurableFieldSpec,
    RunnableLambda,
    RunnablePassthrough,
)
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from pydantic import BaseModel, Field
from owlready2 import *


from generator.nlp import extract_move_intent

from generator.utils import find_levenshtein_match, encode_entity_name

logger = logging.getLogger(__name__)

CHAT_SYSTEM_PROMPT = """
You are an LLM designed to act as the engine for a text adventure game set in "{{setting}}".

Keep in mind that more things can and should be revealed later, after interaction with the player, so feel free to keep some information to yourself for later.
Keep in mind that not everything that is in a location is necessarily immediately visible or known to the player. Things can be hidden within a location, and a location can be quite large. You should discreetly tell the player they can go there, without being too explicit.
If the player has spent a long time in a location, you can push them a little more explicitly to move to different locations.
The game is played by interactions between the game (you) and the player. The player will type in natural language whatever they want to do, etc.
Do not reveal everything all at once: let the player discover things. Only output natural text, as one would read in a book they actually were the hero of.
Do not reveal character names unless the player knows them.

Your messages should be short. Please do not produce lengthy messages. Your messages should be one to two sentences long. The player can always ask for more details ! For dialogues, you will output only one line of dialogue, and let the player respond.

Use the game elements provided:

# Game state
The player's current location is "{{location.hasName}}". {{location.hasName}} is described as "{{location.hasDescription}}".

The locations accessible from where the player is are {{nearby_locations_names}}. You should discreetly tell the player they can go there, without being too explicit.

The player's character is named "{{player.hasName}}" and is described as "{{player.hasDescription}}".
The player's goal is "{{player.hasGoal[0].hasDescription}}"

{%- if characters_nearby %}
Characters present in {{location.hasName}}:
{%- for character in characters_nearby %}
    - {{ character.hasName }}: {{character.hasDescription}} (narrative importance {{character.hasImportance}})
{%- endfor %}
{%- else %}
    There are no other characters present in {{location.hasName}}.
{%- endif %}

{%- if items_nearby %}
Items present in {{location.hasName}}:
{%- for item in items_nearby %}
    - {{ item.hasName }}: {{item.hasDescription}} (narrative importance {{item.hasImportance}})
{%- endfor %}
{%- else %}
    There are no items present in {{location.hasName}}.
{%- endif %}

{%- if player.INDIRECT_ownsItem %}
Items in the player's inventory:
{%- for item in player.INDIRECT_ownsItem %}
    - {{ item.hasName }}: {{item.hasDescription}} (narrative importance {{item.hasImportance}})
{%- endfor %}
{%- else %}
    The player has no items in their inventory.
{%- endif %}

{%- if move_intent_location %}
The parser has detected that the player intends to move to {{move_intent_location.hasName}}.
    {{move_intent_location.hasName}} is described as "{{move_intent_location.hasDescription}}".
    {%- if move_intent_location.INDIRECT_containsCharacter %}
        Characters present in {{move_intent_location.hasName}}:
        {%- for character in move_intent_location.INDIRECT_containsCharacter %}
            - {{ character.hasName }}: {{character.hasDescription}} (narrative importance {{character.hasImportance}})
        {%- endfor %}
    {%- endif %}
    {%- if move_intent_location.INDIRECT_containsItem %}
        Items present in {{move_intent_location.hasName}}:
        {%- for item in move_intent_location.INDIRECT_containsItem %}
            - {{ item.hasName }}: {{item.hasDescription}} (narrative importance {{item.hasImportance}})
        {%- endfor %}
    {%- endif %}

If you confirm the move, add the token "<CONFIRM_MOVE>" to your response.
**Keep in mind that the player will read your response before typing theirs, and only the token will be removed from your response.**
{%- endif %}

Always answer in {{language}}
"""


# https://python.langchain.com/v0.2/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html
class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""

    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []


# Here we use a global variable to store the chat message history.
# This will make it easier to inspect it to see the underlying results.
store = {}

def get_by_session_id(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryHistory()
    return store[session_id]



def get_chain(model, predictable_model, first_message: str, setting: str, language: str, user_name: str, config: dict):
    # Load the ontology
    logger.info(f'Loading ontology for user {user_name}')
    onto = get_ontology('file://story_poptest70b.rdf').load()

    # with onto:
    #     sync_reasoner()

    logger.info(f'Ontology loaded for user {user_name}')
    # Define the chat prompt

    # Initialize the history
    history = InMemoryHistory()

    # Add the first messages to the history
    history.add_messages([('ai', first_message)])

    # Define the function that will be called to generate the next message
    
    
    async def converse(message: str):
            # 1. Extract move intent
        move_intent_location = extract_move_intent(predictable_model, message, onto)

        # 2. Retrieve relevant information from the KG
        # 2.1 If the player intends to move, add the new location information to the chat prompt
        if move_intent_location:
            print(f'Move intent: {move_intent_location}')


        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", CHAT_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{{message}}"),
        ], template_format='jinja2')

        chain = chat_prompt | model

        chain_with_history = RunnableWithMessageHistory(
            chain,
            get_by_session_id,
            input_messages_key="message",
            history_messages_key="history",
        )


        # Retrieve relevant information from the KG
        with onto:
            player = list(onto.Player.instances())[0]
            current_location = player.INDIRECT_isLocatedAt
            characters_nearby = current_location.INDIRECT_containsCharacter
            locations_nearby = current_location.INDIRECT_isLinkedToLocation
            nearby_locations_names = [l.hasName for l in locations_nearby]
            items_nearby = current_location.INDIRECT_containsItem


            response = await chain_with_history.ainvoke(
                {"setting": setting, 
                "language": language,
                "location": current_location,
                "move_intent_location": move_intent_location,
                'characters_nearby': characters_nearby,
                'items_nearby': items_nearby,
                'player': player,
                'nearby_locations_names': nearby_locations_names,
                "message": message},
                config=config
            )

            text_response = response.content

            # Find if the LLM accepted the move, and filter out the <CONFIRM_MOVE> token
            if '<CONFIRM_MOVE>' in text_response:
                print('Move confirmed by the LLM')
                text_response = text_response.replace('<CONFIRM_MOVE>', '').strip()

                # If the LLM accepted the move, update the KG
                with onto:
                    for follower in player.INDIRECT_hasFollower:
                        follower.isLocatedAt = move_intent_location
                    player.isLocatedAt = move_intent_location

            inventory_actions = extract_inventory_actions(predictable_model, message, text_response, onto)
            character_actions = extract_character_actions(predictable_model, message, text_response, onto)
            apply_inventory_actions(inventory_actions.get('actions', []), onto)
            apply_character_actions(character_actions.get('actions', []), onto)

        return text_response

    return converse


INVENTORY_ACTIONS_PARSER_TEMPLATE = """
Human: Please analyze the player's message and determine if they intend to interact with an item.

# Action Types
- "create" if you need to create a new item that doesn't exist yet.
- "destroy" if an item should be removed from the game.
- "claim" if the player has taken or picked up an unowned item.
- "give" if the player has given an item they own to another character. In this case, you will provide the name of the character the player gives the item to. **If the character doesn't exist, ignore the action.**
- "drop" if the player has dropped an item they own in the current location.
- "alter" if the player's actions have changed the state of an item. In this case, you will provide an updated description of the item.

{%- if player.INDIRECT_ownsItem %}
# Possible items whose state to change
**Owned items**:
{%- for item in player.INDIRECT_ownsItem %}
- {{item.hasName}}: {{item.hasDescription}}
{%- endfor %}
{%- else %}
There are no items in the player's inventory.
{%- endif %}

{%- if nearby_items %}
**Unowned items in the current location**:
{%- for item in nearby_items %}
{%- if not item.INDIRECT_isOwnedBy %}
- {{item.hasName}}: {{item.hasDescription}}
{%- endif %}
{%- endfor %}
{%- else %}
There are no unowned items in the current location.
{%- endif %}

{%- if nearby_characters %}
**Names of the characters present in the current location**:
{%- for character in nearby_characters %}
    {%- if character.hasName != player.hasName %}
- "{{character.hasName}}"
    {%- endif %}
{%- endfor %}
{%- else %}
There are no other characters present in the current location.
{%- endif %}

# Last message from the player and game response
Player message: "{{player_message}}"
Game response: "{{game_response}}"

**Please output a list of actions that the game system needs to perform to update the game state, in the following JSON format:**
If none of these fit, output an empty list.

```json
{
    "actions": [
        {"action": "create", "item": "map", "description": "A map of the area."},
        {"action": "claim", "item": "map"},
        {"action": "give", "item": "coin", "target": "John Brown"},
        {"action": "drop", "item": "bucket"},
        {"action": "destroy", "item": "apple"},
        {"action": "alter", "item": "sword", "description": "The sword is now covered in rust."}
    ]
}
```

Output:
"""



def extract_inventory_actions(model, message: str, game_response: str, onto):
    prompt = PromptTemplate(
        template=INVENTORY_ACTIONS_PARSER_TEMPLATE,
        template_format='jinja2'
    )

    parser = JsonOutputParser()

    chain = prompt | model | parser

    
    with onto:
        player = onto.Player.instances()[0]
        current_location = player.INDIRECT_isLocatedAt

        parameters = {
            "player_message": message, 
            "game_response": game_response, 
            "player": player,
            "onto": onto,
            "nearby_characters": current_location.INDIRECT_containsCharacter,
            "nearby_items": current_location.INDIRECT_containsItem
        }

        # Print the prompt to inspect it
        print(prompt.invoke(parameters).text)

        response = chain.invoke(parameters)
        
    return response



def apply_inventory_actions(actions: list, onto):
    with onto:
        player = onto.Player.instances()[0]
        for action in actions:
            try:
                if action['action'] == 'create':
                    item_name = action['item']
                    item = onto.Item(encode_entity_name(item_name))
                    item.hasDescription = action['description']
                    player.ownsItem.append(item)
                elif action['action'] == 'destroy':
                    item = find_levenshtein_match(action['item'], onto.Item.instances())
                    if item:
                        player.ownsItem.remove(item)
                        destroy_entity(item)
                elif action['action'] == 'claim':
                    item = find_levenshtein_match(action['item'], onto.Item.instances())
                    if item:
                        player.ownsItem.append(item)
                        item.itemIsLocatedAt = None
                elif action['action'] == 'give':
                    item = find_levenshtein_match(action['item'], onto.Item.instances())
                    target = find_levenshtein_match(action['target'], onto.Character.instances())
                    if item and target:
                        if item in player.ownsItem:
                            player.ownsItem.remove(item)
                            target.ownsItem.append(item)
                elif action['action'] == 'drop':
                    item = find_levenshtein_match(action['item'], onto.Item.instances())
                    if item:
                        player.ownsItem.remove(item)
                        item.itemIsLocatedAt = current_location
                elif action['action'] == 'alter':
                    item = find_levenshtein_match(action['item'], onto.Item.instances())
                    if item:
                        item.hasDescription = action['description']
            except ValueError as e:
                print(f'Error applying inventory action: {e}')



CHARACTER_ACTIONS_PARSER_TEMPLATE = """
Human: Please analyze the player's message and corresponding game response to determine if the interaction changed something about the characters present in the scene

**Action Types**:.
- "start_following" if a character has started following the player.
- "stop_following" if a character has stopped following the player.
- "change_health" if a character's health has changed. Add a new description of the character's health.
- "change_description" if a character's description needs to be changed. Add a new description of the character.
- "become_enemies" if two characters have become enemies. (symmetrical)
- "become_friends" if two characters have become friends. (symmetrical)
- "become_rivals" if two characters have become rivals. (symmetrical)
- "become_neutral" if two characters have become neutral. (symmetrical)
- "give_allegiance" if a character has given allegiance to another character. (asymmetrical)
- "now_knows" if a character now knows about another character's existence. (asymmetrical)
- "fall_in_love" if a character has fallen in love with another character. (asymmetrical)

Most relationships are symmetrical, but some are not, like loves. If love is reciprocal, output two actions, one for each character.

The player is named "{{player.hasName}}" and is described as "{{player.hasDescription}}".

**Characters present**:
{%- for character in characters_present %}
- {{character.hasName}}: {{character.hasDescription}}
    {% if character.INDIRECT_knows %}knows: {%- for known_character in character.INDIRECT_knows %} "{{known_character.hasName}}" {%- endfor %}{%- endif %}
    {% if character.INDIRECT_isEnemyWith %}is enemy with: {%- for enemy in character.INDIRECT_isEnemyWith %} "{{enemy.hasName}}" {%- endfor %}{%- endif %}
    {% if character.INDIRECT_hasFriendshipWith %}is friend with: {%- for friend in character.INDIRECT_hasFriendshipWith %} "{{friend.hasName}}" {%- endfor %}{%- endif %}
    {% if character.INDIRECT_isRivalWith %}is rival with: {%- for rival in character.INDIRECT_isRivalWith %} "{{rival.hasName}}" {%- endfor %}{%- endif %}
    {% if character.INDIRECT_loves %}is in love with: {%- for love in character.INDIRECT_loves %} "{{love.hasName}}" {%- endfor %}{%- endif %}
    {% if character.INDIRECT_hasAllegiance %}has allegiance to: {{character.INDIRECT_hasAllegiance.hasName}}{%- endif %}
{%- endfor %}

Player message: "{{player_message}}"
Game response: "{{game_response}}"

**Please output a list of actions that the game system needs to perform to update the game state, in the following JSON format:**
If none of these fit, output an empty list.

```json
{
    "actions": [
        {"action": "become_enemies", "subject": "John Brown", "object": "Jane Doe"},
        {"action": "become_friends", "subject": "John Brown", "object": "Jane Doe"},
        {"action": "become_neutral", "subject": "John Brown", "object": "Jane Doe"},
        {"action": "fall_in_love", "subject": "John Brown", "object": "Jane Doe"},
        {"action": "give_allegiance", "subject": "John Brown", "object": "Jane Doe"},
        {"action": "now_knows", "subject": "John Brown", "object": "Jane Doe"},
        {"action": "start_following", "subject": "John Brown", "object": "Jane Doe"},
        {"action": "stop_following", "subject": "John Brown", "object": "Jane Doe"},
        {"action": "change_health", "subject": "John Brown", "description": "John Brown is now in dire condition. He might die soon."},
        {"action": "change_description", "subject": "John Brown", "description": "John Brown is blablabla (keep parts of the original description) and is now wearing a red hat."}
    ]
}
```

Output:
"""

def extract_character_actions(model, message: str, game_response: str, onto):
    prompt = PromptTemplate(
        template=CHARACTER_ACTIONS_PARSER_TEMPLATE,
        template_format='jinja2'
    )

    parser = JsonOutputParser()

    chain = prompt | model | parser

    with onto:
        player = onto.Player.instances()[0]
        current_location = player.INDIRECT_isLocatedAt

        parameters = {
            "player_message": message, 
            "game_response": game_response, 
            "player": player,
            "onto": onto,
            "characters_present": current_location.INDIRECT_containsCharacter
        }

        # Print the prompt to inspect it
        print(prompt.invoke(parameters).text)

        response = chain.invoke(parameters)
        
    return response



def apply_character_actions(actions: list, onto):
    with onto:
        player = onto.Player.instances()[0]
        for action in actions:
            try:
                if action['action'] == 'start_following':
                    subject = find_levenshtein_match(action['subject'], onto.Character.instances())
                    if subject:
                        player.hasFollower.append(subject)
                elif action['action'] == 'stop_following':
                    subject = find_levenshtein_match(action['subject'], onto.Character.instances())
                    if subject:
                        if subject in player.hasFollower:
                            player.hasFollower.remove(subject)
                elif action['action'] == 'change_health':
                    subject = find_levenshtein_match(action['subject'], onto.Character.instances())
                    if subject:
                        subject.hasHealth = action['description']
                elif action['action'] == 'change_description':
                    subject = find_levenshtein_match(action['subject'], onto.Character.instances())
                    if subject:
                        subject.hasDescription = action['description']
                elif action['action'] == 'become_enemies':
                    subject = find_levenshtein_match(action['subject'], onto.Character.instances())
                    _object = find_levenshtein_match(action['object'], onto.Character.instances())
                    if subject and _object:
                        subject.isEnemyWith.append(_object)
                        _object.isEnemyWith.append(subject)
                elif action['action'] == 'become_friends':
                    subject = find_levenshtein_match(action['subject'], onto.Character.instances())
                    _object = find_levenshtein_match(action['object'], onto.Character.instances())
                    if subject and _object:
                        subject.hasFriendshipWith.append(_object)
                        _object.hasFriendshipWith.append(subject)
                elif action['action'] == 'become_neutral':
                    subject = find_levenshtein_match(action['subject'], onto.Character.instances())
                    _object = find_levenshtein_match(action['object'], onto.Character.instances())
                    if subject and _object:
                        if _object in subject.isEnemyWith:
                            subject.isEnemyWith.remove(_object)
                        if _object in subject.isRivalWith:
                            subject.isRivalWith.remove(_object)
                        if _object in subject.hasFriendshipWith:
                            subject.hasFriendshipWith.remove(_object)
                        if _object in _object.isEnemyWith:
                            _object.isEnemyWith.remove(subject)
                        if _object in _object.isRivalWith:
                            _object.isRivalWith.remove(subject)
                        if _object in _object.hasFriendshipWith:
                            _object.hasFriendshipWith.remove(subject)
                elif action['action'] == 'fall_in_love':
                    subject = find_levenshtein_match(action['subject'], onto.Character.instances())
                    _object = find_levenshtein_match(action['object'], onto.Character.instances())
                    if subject and _object:
                        # Love is sometimes reciprocal, sometimes not
                        subject.loves.append(_object)
                elif action['action'] == 'give_allegiance':
                    subject = find_levenshtein_match(action['subject'], onto.Character.instances())
                    _object = find_levenshtein_match(action['object'], onto.Character.instances())
                    if subject and _object:
                        subject.hasAllegiance = _object
                elif action['action'] == 'rescind_allegiance':
                    subject = find_levenshtein_match(action['subject'], onto.Character.instances())
                    if subject:
                        subject.hasAllegiance = None
                elif action['action'] == 'now_knows':
                    subject = find_levenshtein_match(action['subject'], onto.Character.instances())
                    _object = find_levenshtein_match(action['object'], onto.Character.instances())
                    if subject and _object:
                        subject.knows.append(_object)
            except ValueError as e:
                print(f'Error applying character action: {e}')
