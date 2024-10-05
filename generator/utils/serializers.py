
import json

def natural2pascal(text: str) -> str:
    """Converts a string in natural language to Pascal case"""
    sanitized = ''.join(e for e in text if e.isalnum() or e == ' ') # Remove special characters
    capitalized = sanitized.title()
    spaces_removed = "".join(capitalized.split(' '))
    return spaces_removed

def pascal2natural(text: str) -> str:
    natural_text = []
    
    for i, char in enumerate(text):
        # Check if the character is uppercase and not the first character
        if char.isupper() and i > 0 and (text[i-1].islower() or text[i-1].isdigit()):
            natural_text.append(' ')  # Add a space before the uppercase letter
        natural_text.append(char.lower())  # Append the lowercase version of the character

    return ''.join(natural_text)


def json2llmready(json_text: str):
    cleaned_data = []
    
    jsonld_data = json.loads(json_text)

    for item in jsonld_data:
        cleaned_item = {}

        # Extract the @id as the identifier
        identifier = item.get('@id', 'Unknown ID').split('#')[-1]
        cleaned_item['ID'] = identifier

        # Extract @type (e.g., class or property type)
        if '@type' in item:
            cleaned_item['Type'] = [t.split('#')[-1] for t in item['@type']]

        # Extract domain and range if available
        if 'http://www.w3.org/2000/01/rdf-schema#domain' in item:
            domain = item['http://www.w3.org/2000/01/rdf-schema#domain'][0]['@id'].split('#')[-1]
            cleaned_item['Domain'] = domain

        if 'http://www.w3.org/2000/01/rdf-schema#range' in item:
            range_ = item['http://www.w3.org/2000/01/rdf-schema#range'][0]['@id'].split('#')[-1]
            cleaned_item['Range'] = range_

        # Extract inverseOf relationship
        if 'http://www.w3.org/2002/07/owl#inverseOf' in item:
            inverse_of = item['http://www.w3.org/2002/07/owl#inverseOf'][0]['@id'].split('#')[-1]
            cleaned_item['InverseOf'] = inverse_of

        # Extract labels or comments if present
        if 'http://www.w3.org/2000/01/rdf-schema#label' in item:
            label = item['http://www.w3.org/2000/01/rdf-schema#label'][0]['@value']
            cleaned_item['Label'] = label

        if 'http://www.w3.org/2000/01/rdf-schema#comment' in item:
            comment = item['http://www.w3.org/2000/01/rdf-schema#comment'][0]['@value']
            cleaned_item['Comment'] = comment

        cleaned_data.append(cleaned_item)

    return cleaned_data



if __name__ == "__main__":
    print(natural2pascal("Raven's rest"))
    print(pascal2natural("RavensThorpe"))
    
    
    # Example usage
    with open('../story.json', "r") as f:
        jsonld_data = f.read()
    readable_data = json2llmready(jsonld_data)
    print(json.dumps(readable_data, indent=2, ensure_ascii=False))
