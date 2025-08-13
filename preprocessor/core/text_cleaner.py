# Dependencies
import re
import logging
from typing import List


class TextCleaner:
    """
    Handles text cleaning operations for web content
    """
    def __init__(self, skip_phrases: List[str] = None, verbose: bool = False):
        """
        Initialize TextCleaner with configurable parameters.
        
        Arguments:
        ----------
            skip_phrases { list } : List of phrases to skip during processing

            verbose      { bool } : Enable verbose logging
        """
        self.skip_phrases         = skip_phrases or []
        self.verbose              = verbose
        
        # Enhanced skip phrases for web content
        self.default_skip_phrases = ["loading", 
                                     "copyright", 
                                     "subscribe", 
                                     "follow us", 
                                     "404 error", 
                                     "newsletter", 
                                     "contact us", 
                                     "please wait", 
                                     "cookie policy", 
                                     "privacy policy", 
                                     "page not found", 
                                     "terms of service", 
                                     "all rights reserved",
                                    ]
        
        self.skip_phrases.extend(self.default_skip_phrases)
        
        # Common web noise patterns
        self.noise_patterns       = [r'\n{3,}',        # Multiple newlines
                                     r'\s{3,}',        # Multiple spaces
                                     r'\|\s*\|\s*\|',  # Multiple pipe separators
                                     r'©\s*\d{4}.*?all\s*rights\s*reserved',
                                     r'\b\d{4}\s*©\s*.*?all\s*rights\s*reserved\b',
                                    ] 
        
        # Setup logging
        logging.basicConfig(level = logging.DEBUG if verbose else logging.INFO)
        self.logger               = logging.getLogger("TextCleaner")

    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing noise patterns and normalizing formatting
        
        Arguments:
        ----------
            text { str } : Raw text to clean
            
        Returns:
        --------
             { str }     : Cleaned text
        """
        if not text or not text.strip():
            return ""
        
        # Remove noise patterns
        for pattern in self.noise_patterns:
            text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
        
        # Clean up whitespace and formatting
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\s*\|\s*\|\s*\|.*$', '', text, flags = re.MULTILINE)
        
        # Remove URLs and email addresses
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'\S+@\S+\.\S+', '', text)
        
        # Clean up extra punctuation
        text = re.sub(r'[.]{2,}', '.', text)
        text = re.sub(r'[,]{2,}', ',', text)
        
        return text.strip()
    

    def contains_skip_phrases(self, text: str) -> bool:
        """
        Check if text contains any skip phrases
        
        Arguments:
        ----------
            text  { str } : Text to check
            
        Returns:
        --------
             { bool }     : True if text contains skip phrases
        """
        text_lower = text.lower()
        flag       = any(phrase.lower() in text_lower for phrase in self.skip_phrases)
        
        return flag