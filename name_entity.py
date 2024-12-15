import spacy

class EntityExtractor:
    def __init__(self, model='en_core_web_sm'):
        """
        Initialize the Named Entity Extractor
        
        :param model: SpaCy NER model to use (default: en_core_web_sm)
        """
        try:
            self.nlp = spacy.load(model)
        except OSError:
            print(f"Model {model} not found. Downloading...")
            spacy.cli.download(model)
            self.nlp = spacy.load(model)

    def extract_entities(self, text):
        """
        Extract named entities from text, limited to PERSON and ORG
        
        :param text: Input text to extract entities from
        :return: List of extracted entities
        """
        # Define allowed labels
        interesting_labels = ['PERSON', 'ORG']

        doc = self.nlp(text)
        entities = [
            {
                'text': ent.text, 
                'label': ent.label_
            } 
            for ent in doc.ents 
            if ent.label_ == 'PERSON' or ent.label_ == 'ORG'
        ]
        return entities