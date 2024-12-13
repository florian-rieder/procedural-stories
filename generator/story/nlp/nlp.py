from generator.utils import find_levenshtein_match, encode_entity_name

from generator.story.nlp.prompts import (
    INTENT_ANALYSIS_TEMPLATE,
    INVENTORY_ACTIONS_PARSER_TEMPLATE,
    CHARACTER_ACTIONS_PARSER_TEMPLATE,
)

from tracet import Chain, chainable, JsonRepairParser

from owlready2 import destroy_entity


@chainable(input_keys=["onto"], output_key="nearby_locations_names")
def get_nearby_locations(onto):
    with onto:
        player = onto.Player.instances()[0]
        current_location = player.INDIRECT_isLocatedAt
        nearby_locations = current_location.INDIRECT_isLinkedToLocation

        nearby_locations_names = []
        for location in nearby_locations:
            if location.name == "CurrentLocation":
                continue

            nearby_locations_names.append(location.hasName)

        nearby_locations = ", ".join(f'"{name}"' for name in nearby_locations_names)

        return nearby_locations


@chainable(
    input_keys=["move_intent_response", "onto"], output_key="move_intent_location"
)
def find_location(move_intent_response: str, onto):
    result = move_intent_response.strip().strip('"')
    if result.lower() == "none":
        return None
    else:
        entity = find_levenshtein_match(result, onto.Location.instances())
        return entity


def get_move_intent_extraction_chain(model):
    extract_move_intent_chain = Chain(
        get_nearby_locations,
        INTENT_ANALYSIS_TEMPLATE,
        model.using(
            output_key="move_intent_response",
            temperature=0.0,
        ),
        find_location,
        verbose=True,
        debug=True,
    )

    return extract_move_intent_chain


@chainable(input_keys=["onto"], output_key="current_location")
def get_current_location(onto):
    with onto:
        player = onto.Player.instances()[0]
        current_location = player.INDIRECT_isLocatedAt

    return current_location


@chainable(input_keys=["onto"], output_key="player")
def get_player(onto):
    with onto:
        return onto.Player.instances()[0]


def get_inventory_actions_extraction_chain(model):
    chain = Chain(
        get_current_location,
        get_player,
        INVENTORY_ACTIONS_PARSER_TEMPLATE,
        model,
        JsonRepairParser(output_key="inventory_actions"),
        verbose=True,
        debug=True,
    )

    return chain


@chainable(input_keys=["inventory_actions", "onto"], output_key=None)
def apply_inventory_actions(inventory_actions: list, onto):
    if not inventory_actions:
        print("No inventory actions to apply.")
        return
    actions = inventory_actions.get("actions", [])
    with onto:
        player = onto.Player.instances()[0]
        for action in actions:
            try:
                if action["action"] == "create":
                    item_name = action["item"]
                    item = onto.Item(encode_entity_name(item_name))
                    item.hasDescription = action["description"]
                    player.ownsItem.append(item)
                elif action["action"] == "destroy":
                    item = find_levenshtein_match(action["item"], onto.Item.instances())
                    if item:
                        player.ownsItem.remove(item)
                        destroy_entity(item)
                    else:
                        print(f"Item not found: {action['item']}")
                elif action["action"] == "claim":
                    item = find_levenshtein_match(action["item"], onto.Item.instances())
                    if item:
                        player.ownsItem.append(item)
                        item.itemIsLocatedAt = None
                    else:
                        print(f"Item not found: {action['item']}")
                elif action["action"] == "give":
                    item = find_levenshtein_match(action["item"], onto.Item.instances())
                    target = find_levenshtein_match(
                        action["target"], onto.Character.instances()
                    )
                    if item and target:
                        if item in player.ownsItem:
                            player.ownsItem.remove(item)
                            target.ownsItem.append(item)
                    else:
                        if not item:
                            print(f"Item not found: {action['item']}")
                        if not target:
                            print(f"Target not found: {action['target']}")
                elif action["action"] == "drop":
                    item = find_levenshtein_match(action["item"], onto.Item.instances())
                    if item:
                        player.ownsItem.remove(item)
                        current_location = get_current_location(onto)
                        item.itemIsLocatedAt = current_location
                    else:
                        print(f"Item not found: {action['item']}")
                elif action["action"] == "alter":
                    item = find_levenshtein_match(action["item"], onto.Item.instances())
                    if item:
                        description = action.get("description", "")
                        if description:
                            item.hasDescription = description
                        else:
                            print(f"No description provided for item: {action['item']}")
                    else:
                        print(f"Item not found: {action['item']}")
            except Exception as e:
                print(f"Error applying inventory action: {e}")


def get_character_actions_extraction_chain(model):
    chain = Chain(
        get_current_location,
        get_player,
        CHARACTER_ACTIONS_PARSER_TEMPLATE,
        model.using(
            output_key="character_actions_response",
            temperature=0.0,
        ),
        JsonRepairParser(
            input_key="character_actions_response", output_key="character_actions"
        ),
        verbose=True,
        debug=True,
    )

    return chain


@chainable(input_keys=["character_actions", "onto"], output_key=None)
def apply_character_actions(character_actions: list, onto):
    if not character_actions:
        print("No character actions to apply")
        return
    actions = character_actions.get("actions", [])
    with onto:
        player = onto.Player.instances()[0]
        for action in actions:
            try:
                if action["action"] == "start_following":
                    subject = find_levenshtein_match(
                        action["subject"], onto.Character.instances()
                    )
                    if subject:
                        player.hasFollower.append(subject)
                elif action["action"] == "stop_following":
                    subject = find_levenshtein_match(
                        action["subject"], onto.Character.instances()
                    )
                    if subject:
                        if subject in player.hasFollower:
                            player.hasFollower.remove(subject)
                    else:
                        print(f"Subject not found: {action['subject']}")
                elif action["action"] == "change_health":
                    subject = find_levenshtein_match(
                        action["subject"], onto.Character.instances()
                    )
                    if subject:
                        subject.hasHealth = action["description"]
                    else:
                        print(f"Subject not found: {action['subject']}")
                elif action["action"] == "change_description":
                    subject = find_levenshtein_match(
                        action["subject"], onto.Character.instances()
                    )
                    if subject:
                        subject.hasDescription = action["description"]
                    else:
                        print(f"Subject not found: {action['subject']}")
                elif action["action"] == "become_enemies":
                    subject = find_levenshtein_match(
                        action["subject"], onto.Character.instances()
                    )
                    _object = find_levenshtein_match(
                        action["object"], onto.Character.instances()
                    )
                    if subject and _object:
                        subject.isEnemyWith.append(_object)
                        _object.isEnemyWith.append(subject)
                    else:
                        if not subject:
                            print(f"Subject not found: {action['subject']}")
                        if not _object:
                            print(f"Object not found: {action['object']}")
                elif action["action"] == "become_friends":
                    subject = find_levenshtein_match(
                        action["subject"], onto.Character.instances()
                    )
                    _object = find_levenshtein_match(
                        action["object"], onto.Character.instances()
                    )
                    if subject and _object:
                        subject.hasFriendshipWith.append(_object)
                        _object.hasFriendshipWith.append(subject)
                    else:
                        if not subject:
                            print(f"Subject not found: {action['subject']}")
                        if not _object:
                            print(f"Object not found: {action['object']}")
                elif action["action"] == "become_neutral":
                    subject = find_levenshtein_match(
                        action["subject"], onto.Character.instances()
                    )
                    _object = find_levenshtein_match(
                        action["object"], onto.Character.instances()
                    )
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
                elif action["action"] == "fall_in_love":
                    subject = find_levenshtein_match(
                        action["subject"], onto.Character.instances()
                    )
                    _object = find_levenshtein_match(
                        action["object"], onto.Character.instances()
                    )
                    if subject and _object:
                        # Love is sometimes reciprocal, sometimes not
                        subject.loves.append(_object)
                    else:
                        if not subject:
                            print(f"Subject not found: {action['subject']}")
                        if not _object:
                            print(f"Object not found: {action['object']}")
                elif action["action"] == "give_allegiance":
                    subject = find_levenshtein_match(
                        action["subject"], onto.Character.instances()
                    )
                    _object = find_levenshtein_match(
                        action["object"], onto.Character.instances()
                    )
                    if subject and _object:
                        subject.hasAllegiance = _object
                    else:
                        if not subject:
                            print(f"Subject not found: {action['subject']}")
                        if not _object:
                            print(f"Object not found: {action['object']}")
                elif action["action"] == "rescind_allegiance":
                    subject = find_levenshtein_match(
                        action["subject"], onto.Character.instances()
                    )
                    if subject:
                        subject.hasAllegiance = None
                    else:
                        print(f"Subject not found: {action['subject']}")
                elif action["action"] == "now_knows":
                    subject = find_levenshtein_match(
                        action["subject"], onto.Character.instances()
                    )
                    _object = find_levenshtein_match(
                        action["object"], onto.Character.instances()
                    )
                    if subject and _object:
                        subject.knows.append(_object)
                    else:
                        if not subject:
                            print(f"Subject not found: {action['subject']}")
                        if not _object:
                            print(f"Object not found: {action['object']}")
            except Exception as e:
                print(f"Error applying character action: {e}")
