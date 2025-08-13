# Dependencies
import re
import spacy
import logging
from typing import List


class NamedEntityRecognizer:
    """
    Handles named entity recognition using spaCy
    """
    def __init__(self, model_name: str = "en_core_web_sm", verbose: bool = False):
        """
        Initialize NamedEntityRecognizer
        
        Arguments:
        ----------
            model_name { str }  : spaCy model name to use

            verbose    { bool } : Enable verbose logging
        """ 
        self.model_name = model_name
        self.verbose    = verbose
        
        # Load spaCy model
        try:
            self.ner_model = spacy.load(model_name)

        except (ImportError, OSError) as e:
            logging.error(f"Failed to load spaCy model {model_name}: {e}")
            raise
        
        # Setup logging
        logging.basicConfig(level = logging.DEBUG if verbose else logging.INFO)
        self.logger = logging.getLogger("NamedEntityRecognizer")

    
    def extract_named_entities(self, text: str) -> List[str]:
        """
        Extract named entities from text with filtering
        
        Arguments:
        ----------
            text { str } : Text to extract entities from
            
        Returns:
        --------
             { list }    : List of extracted entity strings
        """
        if (not text or len(text.strip()) < 10):
            return []
        
        try:
            # Limit text length for efficiency
            document         = self.ner_model(text[:5000])
            entities         = list()
            entity_list      = ["ORG", "PERSON", "GPE", "PRODUCT"]
            entity_text_list = ['usa', 'app', 'web', 'mobile', 'business']
            
            for entity in document.ents:
                if entity.label_ in entity_list:
                    # Filter out common web noise entities
                    entity_text = entity.text.strip()
                    
                    if ((len(entity_text) > 2) and (entity_text.lower() not in entity_text_list) and (not re.match(r'^\d+$', entity_text))):
                        entities.append(entity_text)
            
            # Remove duplicates while preserving order
            seen            = set()
            unique_entities = list()

            for entity in entities:
                if entity not in seen:
                    seen.add(entity)
                    unique_entities.append(entity)
            
            self.logger.debug(f"Extracted {len(unique_entities)} entities")
            
            return unique_entities
            
        except Exception as e:
            self.logger.warning(f"NER extraction failed: {e}")
            return []
    

    def get_entities_by_label(self, text: str, label: str) -> List[str]:
        """
        Extract entities of a specific label type
        
        Arguments:
        ----------
            text  { str } : Text to extract entities from

            label { str } : Entity label to filter by (e.g., "ORG", "PERSON")
            
        Returns:
        --------
             { list }     : List of entities with the specified label
        """
        if (not text or len(text.strip()) < 10):
            return []
        
        try:
            document        = self.ner_model(text[:5000])
            entities        = [entity.text.strip() for entity in document.ents if entity.label_ == label]
            
            # Remove duplicates
            entity_labels   = list(set(entities))
            
            return entity_labels
            
        except Exception as e:
            self.logger.warning(f"Label-specific NER extraction failed: {e}")
            return []