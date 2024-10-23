OUTLINE_GENERATION_PROMPT = """
# Instructions pour la génération
Sur la base du contexte narratif ci-dessous, générez les grandes lignes d'une histoire possible en tenant compte des éléments suivants :

    Lieux : Définissez au moins 4 à 5 lieux clés pertinents pour le contexte et la construction du monde. Incluez une description succincte de chaque lieu, en indiquant son atmosphère, son importance dans l'histoire et tout élément notable qui pourrait influencer les événements ou les personnages.
    Joueur : Établir la position et le rôle du joueur dans l'histoire, en précisant leur identité, leurs motivations et leur lien avec les personnages principaux. Décrire le point de départ du joueur et son rôle dans le récit global.
    Personnages: Etablir une liste d'au moins 4 à 6 personnages principaux de l'histoire, sans rentrer dans les détails. Décrire le rôle et la fonction narrative du personnage, sa relation aux autres personnages, etc, sans rentrer dans trop de détails.
    Objectif : Définir l'objectif global du joueur, en précisant le problème principal à résoudre ou l’enjeu narratif qui motive l’action.
    Événements : Décrire au moins 3 à 5 événements clés qui alimentent l'histoire et doivent être déclenchés par l'action du joueur.
    Objets : Générer uniquement les éléments essentiels nécessaires pour compléter l'histoire (objets de quête), en incluant : Un nom et une description de chaque objet, avec sa fonction dans le récit. Indiquer le lieu où se trouve chaque objet, en s'assurant qu'il s'intègre logiquement dans le contexte de l'histoire.
    Commentaires : Inclure tout commentaire supplémentaire qui pourrait guider la génération de détails supplémentaires ou éclaircir des éléments importants de l'histoire.

# Format de sortie
D'abord, raisonner sur le contexte narratif donné et son importance pour la cohérence du monde et de l'histoire, l'intrigue principale (qui doit être de nature ouverte), et les relations des personnages.
Fournir les éléments dans un fichier json structuré selon le format suivant:
{
    "Locations": [
        {
            "name": "Nom du lieu 1",
            "description": "Description en une phrase du lieu"
        },
        ...
    ],
    "Player": {
        "name": "Donner le nom du personnage qu'incarne le joueur",
        "description": "Description en quelques phrases du personnage qu'incarne le joueur",
        "location": "Nom du lieu de départ de l'histoire"
    },
    "Characters": [
        {
            "name": "Nom propre du personnage 1",
            "description": "description en une phrase du personnage",
        },
        ...
    ],
    "Goal": {
        "description": "description du problème ou de l'enjeu qui motive le joueur"
        "requiresItem": "(FACULTATIF) S'il un objet qui est le centre de l'histoire et doit être récupéré pour gagner, l'indiquer ici. Sinon, omettre ce champs."
    },
    "Events": [
        {
            "name": "Evènement 1",
            "description": "description de l'évènement",
            "condition": "description de la condition qui déclenche l'évènement (devrait être déclenché par l'action du joueur !)",
            "consequences": ["Une ou plusieurs conséquences à l'évènement", "deuxième conséquence possible"]
        },
        ...
    ],
    "Items": [
        {
            "name": "Nom de l'objet",
            "description": "description courte de l'objet et de sa fonction dans le récit",
            "isAtLocation": "(OBLIGATOIRE) Nom du lieu qui contient l'objet"
        },
        ...
    ],
    "Comments": [
        "Tout commentaire que tu voudrais ajouter pour guider la génération de détails supplémentaires et pendant le jeu. Sois précis plus que général: donne des commentaires qui peuvent être exploités. Des éléments importants de l'histoire"
    ]
}

# Contexte narratif
{{ setting }}

# Résultat
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



LOCATION_EXPANSION_PROMPT = """
Contexte de l'histoire:
{{ setting }}

Nous avons le lieu suivant :
    Nom du lieu : {{ location.name }}
    Description actuelle : {{ location.description }}
    Personnages principaux présents dans ce lieu :
    {%- if characters %}
        {%- for character in characters %}
            - "{{ character.name }}": {{ character.description }}
        {%- endfor %}
    {%- else %}
        Aucun
    {%- endif %}
    Objets de quête spécifiques :
    {%- if items %}
        {%- for item in items %}
            - "{{ item.name }}": {{ item.description }}
        {%- endfor %}
    {%- else %}
        Aucun
    {%- endif %}

Ce lieu et les événements qui s'y déroulent doivent refléter fidèlement la période et l'environnement de l'histoire, tels que définis dans le "Contexte de l'histoire". Les objets, personnages, et événements doivent respecter les limites technologiques, culturelles, et sociales de cette époque. Aucun élément ne doit provenir d'une époque postérieure, sauf si justifié par l'histoire.


Objectif: Ne fournir que les détails strictement nécessaires pour enrichir ce lieu, en ajoutant des éléments nouveaux uniquement si pertinents. Évitez de répéter les personnages, objets de quête ou éléments déjà définis dans l'intrigue principale.

Personnages secondaires: Ajouter un ou deux personnages secondaires au maximum, uniquement s'ils sont essentiels pour l'ambiance ou l'action du lieu. Ces personnages doivent être directement liés à des événements ou objets spécifiques présents dans ce lieu, avec des relations explicites.

Objets secondaires: Introduire un ou deux objets secondaires (argent, armes, nourriture, outils) uniquement si cela est nécessaire pour une interaction contextuelle dans la scène. Pour l'argent, inclure la propriété optionnelle quantity pour spécifier combien de la monnaie est présente.

Événements: Ajouter un ou deux événements maximum, en lien avec l'environnement immédiat et le lieu. Chaque événement doit être déclenché par une action spécifique du joueur ou par des indices dans l’environnement.

    Les conditions de déclenchement doivent être liées aux interactions du joueur avec les éléments du lieu (ex. : parler à un personnage, explorer un coin spécifique, examiner un objet).
    Évitez les événements "universels" ; concentrez-vous sur ceux qui enrichissent ce lieu en particulier.

Description finale: La description doit comporter deux phrases, détaillant l'atmosphère, la fonction narrative, et les objets ou événements qui pourraient s'y dérouler.

Fournissez la réponse au format JSON avec les propriétés suivantes :

    name: Le nom du lieu.
    description: Une description développée en deux phrases qui ajoute des détails nouveaux, sans répéter les éléments déjà définis.
    characters: Une liste de nouveaux personnages secondaires s'ils sont pertinents pour ce lieu, avec une courte description.
    items: Une liste de nouveaux objets trouvés dans ce lieu (hors objets de quête), comme de l'argent, des armes, de la nourriture, ou des outils, avec une description de leur utilité dans la scène".
    events: Une liste d'évènements pertinents qui peuvent se produire dans ce lieu, chaque évènement ayant la structure suivante :
        name: Le nom de l'évènement.
        description: Une brève description de ce qui se passe durant l'évènement.
        condition: La condition qui déclenche cet évènement, en lien avec une action du joueur.
        consequences: Une liste des conséquences possibles de cet évènement.

Exemple de sortie JSON :

json

{
  "name": "[Nom du lieu]",
  "description": "[Deux phrases développant davantage le lieu avec des éléments nouveaux sur l'atmosphère, les personnages, ou les objets présents.]",
  "characters": [
    {
      "name": "[Nom d'un personnage secondaire]",
      "description": "[Description du personnage, incluant son rôle potentiel dans le lieu ou la scène.]"
    }
  ],
  "items": [
    {
      "name": "[Nom d'une arme, d'un outil, ou d'un autre objet pertinent]",
      "description": "[Description détaillant l'utilisation potentielle de cet objet dans la scène.]",
      "quantity": "[Si il y a plus qu'un de cet objet, particulièrement si c'est de l'argent, préciser la quantité ici. Si la quantité est 1, ne pas le préciser.]"
    }
  ],
  "events": [
    {
      "name": "[Nom de l'évènement]",
      "description": "[Courte description de ce qui se passe dans cet évènement.]",
      "condition": "[Condition spécifique déclenchée par une action du joueur.]",
      "consequences": [
        "[Première conséquence possible]",
        "[Deuxième conséquence possible]"
      ]
    }
  ]
}

Lieu :
    Nom : {{ location.name }}
    Description actuelle : {{ location.description }}
    Personnages principaux présents :
    {%- if characters %}
        {%- for character in characters %}
            - "{{ character.name }}": {{ character.description }}
        {%- endfor %}
    {%- else %}
        Aucun
    {%- endif %}
    Objets de quête spécifiques :
    {%- if items %}
        {%- for item in items %}
            - "{{ item.name }}": {{ item.description }}
        {%- endfor %}
    {%- else %}
        Aucun
    {%- endif %}
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