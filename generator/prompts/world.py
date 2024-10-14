OUTLINE_GENERATION_PROMPT = """
[INST]
# Ontologie
{ontology}

# Contexte narratif
{context}

# Instructions pour la génération
Sur la base de l'ontologie et du contexte narratif ci-dessus, générez les grandes lignes d'une histoire possible avec les éléments suivants :
- Lieux : Définissez les lieux clés pertinents pour le contexte et la construction du monde.
- Personnages : Inclure au moins 6 personnages avec des rôles et des factions divers et leurs relations.
- Joueur: Etablir la position du joueur dans l'histoire.
- Objectif : définir l'objectif global du joueur. Le problème à résoudre de manière créative.
- Événements : Décrire les événements importants qui alimentent l'histoire.
- Objets : Générer uniquement les éléments IMPORTANTS absolument nécessaires pour compléter l'histoire et qui s'inscrivent dans ce cadre.


# Format de sortie
D'abord, raisonner sur le contexte narratif donné et son importance pour la cohérence du monde et de l'histoire.
Fournir les éléments dans un fichier json structuré selon le format suivant (entre triple backticks "```"):
{{
    "Locations": [
        {{
            "name": "Nom du lieu 1",
            "description": "Description en une phrase du lieu"
        }},
        ...
    ],
    "Characters": [
        {{
            "name": "Nom propre du personnage 1",
            "description": "description en une phrase du personnage",
            "isAtLocation": "Nom du lieu où se trouve le personnage",
            "hasPersonalityTrait": "Un trait de personnalité",
            "hasPersonalityTrait": "Un autre trait de personnalité",
        }},
        {{
            "name": "Nom propre du personnage 2",
            "description": "description en une phrase du personnage",
            "hasStanceTowardsPlayer": "Description de l'attitude du personnage par rapport au joueur"
            "isAtLocation": "Nom du lieu où se trouve le personnage",
            "hasPersonalityTrait": "Un trait de personnalité",
        }},
        ...
    ],
    "Player": {{
        "name": "Donner un nom personnage qu'incarne le joueur",
        "description": "Description en deux phrases du personnage qu'incarne le joueur",
        "isAtLocation": "Nom du lieu de départ de l'histoire"
    }}
    "Goal": {{
        "description": "description du problème ou de l'enjeu qui motive le joueur"
        "requiresItem": "(FACULTATIF) S'il un objet qui est le centre de l'histoire et doit être récupéré pour gagner, l'indiquer ici. Sinon, omettre ce champs."
    }},
    "Events": [
        {{
            "name": "Evènement 1",
            "description": "description de l'évènement",
            "condition": "description de la condition qui déclenche l'évènement (devrait être déclenché par l'action du joueur !)",
            "consequences": ["Une ou plusieurs conséquences à l'évènement", "deuxième conséquence possible"]
        }},
        ...
    ],
    "Items": [
        {{
            "name": "Nom de l'objet",
            "description": "description courte de l'objet et de sa fonction dans le récit",
            "isAtLocation": "(OBLIGATOIRE) Nom du lieu qui contient l'objet"
        }},
        ...
    ],
    "Comments": [
        "Tout commentaire que tu voudrais ajouter pour guider la génération de détails supplémentaires et pendant le jeu. Sois précis plus que général: donne des commentaires qui peuvent être exploités. Des éléments importants de l'histoire"
    ]
}}


[/INST]

Output:
"""

INTERMEDIATE_LOCATIONS_GENERATION_PROMPT = """
Contexte de l'histoire:

{{ setting }}

Voici une liste de lieux importants dans le monde de l'histoire :

{%- for location in locations %}
    - "{{ location.name }}": {{ location.description }}
{%- endfor %}

Je voudrais que vous génériez trois à cinq lieux intermédiaires qui pourraient exister entre ces lieux majeurs. Ces lieux intermédiaires doivent avoir une fonction pratique ou narrative, comme des endroits que le joueur pourrait visiter au cours de son voyage, des repères naturels, des zones dangereuses ou des petits villages. Chaque lieu doit être relié à au moins un autre lieu, et ces relations doivent être indiquées dans la propriété `isLinkedToLocation`.

Veuillez fournir les résultats au format JSON, où chaque lieu est une entrée avec les propriétés suivantes :

    name : Le nom du lieu.
    description : Une courte description du lieu.
    isLinkedToLocation : Une liste des noms d'autres lieux liés à ce lieu.

Le résultat doit être en français et chaque lieu doit s'intégrer logiquement dans ce monde.
Exemple de sortie JSON :

```json
[
  {
    "name": "nom propre du lieu",
    "description": "Description en une phrase du lieu",
    "isLinkedToLocation": ["Nom du lieu lié 1", "Nom du lieu lié 2"]
  },
  ...
]
```

Lieux majeurs :
{%- for location in locations %}
    - "{{ location.name }}"
{%- endfor %}

"""

LOCATION_GENERATION_PROMPT = """[INST]
A partir d'un cadre, génère 5 lieux uniques avec un nom, une brève description et les relations qu'ils peuvent avoir entre eux.
Considère les lieux naturels et artificiels comme les villes, les forêts ou les forteresses, sans t'y limiter. Ajoute des lieux de transition reliant les lieux majeurs.
Utilise toujours le même nom pour référer au même lieu. Veille à ce qu'en général, une seule route mène de A à B, surtout si tu ajoutes un lieu de transition entre les deux.

Commence par réfléchir à voix haute au monde et à sa cohérence, aux relations entre les lieux et leur importance relative, afin de créer un monde cohérent et narrativement intéressant.

Ensuite, définis la liste des lieux. Le résultat doit être une liste d'éléments structurés comme suit (TOUJOURS omettre les `` et les <>) :
`- **<nom du lieu>** [<relation au joueur (ami, neutre, hostile)>]: <brève description d'une phrase> (<autre_lieu_connecté>, <autre_lieu_si_nécessaire>) `


# Cadre de l'histoire
{setting}
[/INST]

Sortie :
"""

CHARACTERS_GENERATION_PROMPT = """[INST]
Génère entre 0 et 4 personnages ou entités qui se trouvent dans le lieu suivant:

# Cadre de l'histoire:
{setting}

# Lieu contenant les personnages:
{location}
[/INST]

Sortie:
"""


ENTITY_EXTRACTION_PROMPT = """
### CONTEXT ###
The following information defines the context of the game world:

- You are currently located at: "{{ current_location }}"
- Nearby locations you are aware of: 
{%- for location in nearby_locations %}
    - "{{ location.name }}": {{ location.description }}
{%- endfor %}

### PREVIOUS GAME RESPONSE ###
"{{ previous_game_response }}"

### USER MESSAGE ###
"{{ user_message }}"

### TASK ###
Based on the provided context, previous game response, and the current user message, identify the entity names referred to in the user's message by its name in the context. The entity name to extract should be one of the names in quotes from the context. Return a short reasoning (one paragraph) and a JSON object with the following format:
```
{
    "user_intent": "<describe the player's action: move, pick up, talk>",
    "resolved_entities": [
        {
            "type": "<entity type: e.g., location, character, item>",
            "name": "<resolved entity name: e.g. Paris>"
        }
    ]
}
```
"""