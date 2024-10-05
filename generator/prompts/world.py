ABOX_GENERATION_PROMPT = """
[INST]
# Ontology T-Box Definitions
{tbox}

# Narrative Context
{context}

# Generation Instructions
Based on the above ontology and narrative context, generate an A-Box with the following:
- Characters: Include at least 5 characters with diverse roles and relationships.
- Locations: Define key locations relevant to Viking Normandy.
- Items: Generate items that fit within this setting.
- Events: Outline significant events that drive the narrative.
- Relationships: Establish connections between characters and other entities.

# Output Format
Provide the A-Box in a structured JSON format adhering to the ontology classes and properties.
[/INST]

Output:
"""

LOCATION_GENERATION_PROMPT = """[INST]
A partir d'un cadre, génère 5 lieux uniques avec un nom, une brève description et les relations qu'ils peuvent avoir entre eux.
Considère les lieux naturels et artificiels comme les villes, les forêts ou les forteresses, sans t'y limiter. Ajoute des lieux de transition reliant les lieux majeurs.
Utilise toujours le même nom pour référer au même lieu.

Commence par réfléchir à voix haute au monde et à sa cohérence, aux relations entre les lieux et leur importance relative, afin de créer un monde cohérent et narrativement intéressant.

Ensuite, définis la liste des lieux. Le résultat doit être une liste d'éléments structurés comme suit (TOUJOURS omettre les `` et les <>) :
`- **<nom du lieu>** [<relation au joueur (ami, neutre, hostile)>]: <brève description d'une phrase> (<autre_lieu_connecté_à>, <autre_lieu_si_nécessaire>) `


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