from urllib.parse import quote, unquote

from Levenshtein import distance


def encode_entity_name(name: str) -> str:
    """Encode a name into a format suitable for URIs

    Args:
        name (str): the name to encode

    Returns:
        str: the encoded string
    """
    return quote(name.lower())


def decode_entity_name(encoded_name: str) -> str:
    return unquote(encoded_name)


def find_levenshtein_match(string: str, entity_list: list, threshold: int = 5):
    """Find a match amongst a list of entities from the ontology, in case the LLM made slight typos !"""
    minimum = threshold
    closest_entity = None
    for entity in entity_list:
        dist = distance(string, entity.hasName)
        if dist < minimum:
            minimum = dist
            closest_entity = entity
    #print(f'{string} -> {closest_entity.hasName}')
    return closest_entity
