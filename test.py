import requests

def get_definition(word):
    """Get definition from Free Dictionary API"""
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word.lower()}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract definitions
            definitions = []
            for entry in data:
                for meaning in entry.get('meanings', []):
                    part_of_speech = meaning.get('partOfSpeech', '')
                    for definition in meaning.get('definitions', []):
                        def_text = definition.get('definition', '')
                        example = definition.get('example', '')
                        
                        definitions.append({
                            'pos': part_of_speech,
                            'definition': def_text,
                            'example': example
                        })
            
            return definitions
        else:
            return None
    
    except Exception as e:
        print(f"Error fetching definition: {e}")
        return None
    
print(get_definition("by the way"))