from typing import Optional

from langchain_core.prompts import PromptTemplate

from generator.utils import find_levenshtein_match

INTENT_ANALYSIS_TEMPLATE = """
Human: Please analyze the player's message and determine if they **explicitly** intend to move to a nearby location **immediately**.
Nearby locations: {{nearby_locations_names}}
Player message: "{{player_message}}"

**Please output only the *exact location name* or 'none' with ABSOLUTELY no additional explanation, notes or details. If it doesn't fit, output 'none'**
Output:
"""

def extract_move_intent(model,message: str, onto):
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
        
        print(prompt.invoke({
            'nearby_locations_names': ", ".join(f'"{l}"' for l in nearby_locations_names),
            'player_message': message
        }).text)
        
        chain = prompt | model
        
        analysis = chain.invoke({
            'nearby_locations_names': ", ".join(f'"{l}"' for l in nearby_locations_names),
            'player_message': message
        })
        #print(f"Output: {analysis.content}")
        
        
        result = analysis.content.strip().strip('"')
        
        
        
        if result.lower() == 'none':
            return None
        
        print(result)
        
        entity = find_levenshtein_match(result, onto.Location.instances())
        
        return entity
