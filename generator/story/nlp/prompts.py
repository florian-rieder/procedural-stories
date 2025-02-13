INTENT_ANALYSIS_TEMPLATE = """
Human: Please analyze the player's message and determine if they **explicitly** intend to move to a nearby location **immediately**.
Nearby locations: {{nearby_locations_names}}

Previous game response: "{{previous_game_response}}"
Player message: "{{player_message}}"

**Please output only the *exact location name* or 'none' with ABSOLUTELY no additional explanation, notes or details. If it doesn't fit, output 'none'**
Output:
""".strip()


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
""".strip()


CHARACTER_ACTIONS_PARSER_TEMPLATE = """
Human: Please analyze the player's message and corresponding game response to determine if the interaction changed something about the characters present in the scene

**Action Types**:.
- "start_following" if a character has started following the player.
- "stop_following" if a character has stopped following the player.
- "change_health" if a character's health has changed. Add a new description of the character's health.
- "change_description" if a character's description needs to be changed because something **important** has changed about the character. Only include information about the nature of the character, not what they are doing or where they are. Add a new description of the character. **DO NOT INCLUDE LOCATION OR INVENTORY INFORMATION, OR OTHER TEMPORARY INFORMATION. ONLY INCLUDE INFORMATION THAT IS IMPORTANT AND SHOULD BE REMEMBERED. MOST INFORMATION SHOULDN'T BE REMEMBERED.**
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
        {"action": "change_health", "subject": "John Brown", "description": "John Brown is in dire condition. He might die soon."},
        {"action": "change_description", "subject": "John Brown", "description": "... (**keep most of the original description, only add or change things that are important**) and is now wearing a red hat."}
    ]
}
```

Output:
""".strip()