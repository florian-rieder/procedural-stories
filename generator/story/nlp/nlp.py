from typing import Optional

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from generator.utils import find_levenshtein_match, encode_entity_name

from generator.story.nlp.prompts import *


def extract_move_intent(model, previous_game_response: str, message: str, onto):
    prompt = PromptTemplate(
        template=INTENT_ANALYSIS_TEMPLATE,
        template_format='jinja2'
    )

    with onto:
        nearby_locations = onto.Player.instances()[0].INDIRECT_isLocatedAt.INDIRECT_isLinkedToLocation
        
        nearby_locations_names = []
        for l in nearby_locations:
            if l.name == "CurrentLocation":
                continue
            
            nearby_locations_names.append(l.hasName)

        #print(nearby_locations_names)

        parameters = {
            'nearby_locations_names': ", ".join(f'"{l}"' for l in nearby_locations_names),
            'previous_game_response': previous_game_response,
            'player_message': message
        }
        
        print(prompt.invoke(parameters).text)
        
        chain = prompt | model

        analysis = chain.invoke(parameters)
        print(f"Move intent output: {analysis.content}")
        
        
        result = analysis.content.strip().strip('"')
        
        
        
        if result.lower() == 'none':
            return None
        
        #print(result)
        
        entity = find_levenshtein_match(result, onto.Location.instances())
        
        return entity



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
        #print(prompt.invoke(parameters).text)

        response = chain.invoke(parameters)

        actions = response.get('actions', [])
        
    return actions



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
        #print(prompt.invoke(parameters).text)

        response = chain.invoke(parameters)

        actions = response.get('actions', [])

    return actions



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
                        if _object in subject.hasRivalryWith:
                            subject.hasRivalryWith.remove(_object)
                        if _object in subject.hasFriendshipWith:
                            subject.hasFriendshipWith.remove(_object)
                        if _object in _object.isEnemyWith:
                            _object.isEnemyWith.remove(subject)
                        if _object in _object.hasRivalryWith:
                            _object.hasRivalryWith.remove(subject)
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
