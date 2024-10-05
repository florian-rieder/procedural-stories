STORY_GENERATION_PROMPT = """
[INST]
# Ontologie
{ontology}

# Contexte narratif
{context}

# Instructions pour la génération
Sur la base de l'ontologie et du contexte narratif ci-dessus, générez les grandes lignes d'une histoire possible avec les éléments suivants :
- Factions : Définissez au moins 2 factions qui mèneront le conflit de l'histoire.
- Lieux : Définissez les lieux clés pertinents pour le contexte et la construction du monde.
- Personnages : Inclure au moins 6 personnages avec des rôles et des factions divers et leurs relations.
- Joueur: Etablir la position du joueur dans l'histoire.
- Objectif : définir l'objectif global du joueur. Le problème à résoudre de manière créative.
- Événements : Décrire les événements importants qui alimentent la narration.
- Objets : Générer uniquement les éléments IMPORTANTS absolument nécessaires pour compléter l'histoire et qui s'inscrivent dans ce cadre.


# Format de sortie
Fournir les éléments dans un fichier json structuré selon le format suivant :
{{
    "Factions": [
        {{
            "name": "Nom de la faction 1",
            "description": "Description en une phrase de la faction"
        }},
        ...
    ],
    "Locations": [
        {{
            "name": "Nom du lieu 1",
            "description": "Description en une phrase du lieu",
            "isControlledByFaction": "Nom de la faction 1"
        }},
        ...
    ],
    "Characters": [
        {{
            "name": "Nom du personnage 1",
            "description": "description en une phrase du personnage",
            "isMemberOfFaction": "Nom de la faction 1",
            "isAtLocation": "Nom du lieu où se trouve le personnage",
            "hasRelationshipWith": "Nom du personnage 2",
            "hasPersonalityTrait": "Hâtif",
            "hasPersonalityTrait": "Aggressif",
            "hasPersonalityTrait": "Stratégique",
        }},
        {{
            "name": "Nom du personnage 2",
            "description": "description en une phrase du personnage",
            "isMemberOfFaction": "Neutre",
            "isAtLocation": "Nom du lieu où se trouve le personnage",
            "hasPersonalityTrait": "Sage",
            "hasPersonalityTrait": "Intelligent",
        }},
        ...
    ],
    "Player": {{
        "name": "Donner un nom personnage qu'incarne le joueur",
        "description": "Description en deux phrases du personnage qu'incarne le joueur",
        "isMemberOfFaction": "Nom de la faction du joueur (Peut être 'Neutre')",
        "isAtLocation": "Nom du lieu de départ de l'histoire"
    }}
    "Goal": {{
        "description": "description du problème ou de l'enjeu que le joueur doit résoudre pour 'gagner'"
        "requiresItem": "S'il un objet qui est le centre de l'histoire et doit être récupéré pour gagner, l'indiquer ici. Sinon, omettre ce champs."
    }},
    "Events": [
        {{
            "name": "Evènement 1",
            "description": "description de l'évènement",
            "condition": "description de la condition qui déclenche l'évènement (devrait être déclenché par l'action du joueur !)",
            "consequences": ["Une ou plusieurs conséquences à l'évènement", "deuxième évènement]
        }},
        ...
    ],
    "Items": [
        {{
            "name": "Nom de l'objet",
            "description": "description courte de l'objet et de sa fonction dans le récit",
            "isAtLocation": "Nom du lieu qui contient l'objet"
        }},
        ...
    ],
    "Comments": [
        "Tout commentaire que tu voudrais ajouter pour guider la génération de détails supplémentaires et pendant le jeu. Sois précis plus que général: donne des commentaires qui peuvent être exploités"
    ]
}}


[/INST]

Output:
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