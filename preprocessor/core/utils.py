# Dependencies
import re
import hashlib
import logging
from typing import Set
from collections import Counter


class Utils:
    """
    Utility functions for content validation and processing
    """
    def __init__(self, verbose: bool = False):
        """
        Initialize Utils
        
        Arguments:
        ----------
            verbose { bool } : Enable verbose logging
        """
        self.verbose                  = verbose
        self.content_hashes: Set[str] = set()
        
        # Setup logging
        logging.basicConfig(level = logging.DEBUG if verbose else logging.INFO)
        
        self.logger = logging.getLogger("Utils")
    

    def get_content_hash(self, content: str) -> str:
        """
        Generate MD5 hash for content deduplication
        
        Arguments:
        ----------
            content { str } : Content to hash
            
        Returns:
        --------
               { str }      : MD5 hash string
        """
        return hashlib.md5(content.lower().strip().encode()).hexdigest()

    
    def is_duplicate_content(self, content: str) -> bool:
        """
        Check if content is a duplicate based on hash
        
        Arguments:
        ----------
            content { str } : Content to check
            
        Returns:
        --------
               { bool }     : True if content is duplicate
        """
        content_hash = self.get_content_hash(content)
        
        if (content_hash in self.content_hashes):
            return True
        
        self.content_hashes.add(content_hash)
        
        return False

    
    def has_excessive_repetition(self, text: str, threshold: float = 0.3) -> bool:
        """
        Check if text has excessive word repetition (likely navigation/footer content)
        
        Arguments:
        ----------
            text       { str }  : Text to analyze

            threshold { float } : Repetition threshold (0.3 = 30%)
            
        Returns:
        --------
              { bool }          : True if text has excessive repetition
        """
        words = text.lower().split()
        
        if (len(words) <= 5):
            return False
        
        word_freq         = Counter(words)
        most_common_count = word_freq.most_common(1)[0][1]
        
        # Check if most common word appears more than threshold
        is_repetitive     = (most_common_count > len(words) * threshold)
        
        return is_repetitive

    
    def calculate_alpha_ratio(self, text: str) -> float:
        """
        Calculate the ratio of alphabetic characters in text
        
        Arguments:
        ----------
            text { str } : Text to analyze
            
        Returns:
        --------
            { float }    : Ratio of alphabetic characters (0.0 to 1.0)
        """
        if not text:
            return 0.0
        
        alpha_chars = len(re.findall(r'[a-zA-Z]', text))
        total_chars = len(text)
        alpha_ratio = alpha_chars / total_chars if total_chars > 0 else 0.0
        
        return alpha_ratio

    
    def is_valid_content(self, text: str, min_length: int = 50, min_alpha_ratio: float = 0.6) -> bool:
        """
        Validate if content meets quality criteria
        
        Arguments:
        ----------
            text             { str }  : Text to validate

            min_length       { int }  : Minimum content length

            min_alpha_ratio { float } : Minimum alphabetic character ratio
            
        Returns:
        --------
                  { bool }            : True if content is valid
        """
        if (not text or len(text.strip()) < min_length):
            return False
        
        # Check alphabetic ratio
        if (self.calculate_alpha_ratio(text) < min_alpha_ratio):
            return False
        
        # Check for excessive repetition
        if (self.has_excessive_repetition(text)):
            return False
        
        return True

    
    def reset_duplicate_tracking(self):
        """
        Reset the duplicate content tracking hash set
        """
        self.content_hashes.clear()
        self.logger.info("Reset duplicate content tracking")

    
    def get_stats(self) -> dict:
        """
        Get statistics about processed content
        
        Returns:
        --------
            { dict }    : Dictionary with processing statistics
        """
        stats = {"unique_content_hashes": len(self.content_hashes)}
        
        return stats 