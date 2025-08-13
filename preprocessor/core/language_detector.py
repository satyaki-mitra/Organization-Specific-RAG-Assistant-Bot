# Dependencies
import logging
from langdetect import detect


class LanguageDetector:
    """
    Handles language detection for text content
    """
    def __init__(self, default_language: str = "en", verbose: bool = False):
        """
        Initialize LanguageDetector
        
        Arguments:
        ----------
            default_languag { str }  : Default language code to return on detection failure

            verbose         { bool } : Enable verbose logging
        """
        self.default_language = default_language
        self.verbose          = verbose
        
        # Setup logging
        logging.basicConfig(level = logging.DEBUG if verbose else logging.INFO)

        self.logger           = logging.getLogger("LanguageDetector")
    

    def detect_language(self, text: str) -> str:
        """
        Detect the language of the input text with error handling
        
        Arguments:
        ----------
            text { str } : Text to analyze for language detection
            
        Returns:
        --------
             { str }     : Language code (e.g., 'en', 'es', 'fr')
        """
        try:
            # Skip language detection for very short texts
            if (len(text.strip()) < 20):
                return self.default_language
            
            detected_lang = detect(text)
            self.logger.debug(f"Detected language: {detected_lang}")
            
            return detected_lang
            
        except Exception as e:
            self.logger.warning(f"Language detection failed: {e}")
            return self.default_language
    

    def is_target_language(self, text: str, target_language: str = None) -> bool:
        """
        Check if text is in the target language
        
        Arguments:
        ----------
            text            { str } : Text to check

            target_language { str } : Target language code (defaults to default_language)
            
        Returns:
        --------
                  { bool }          : True if text is in target language
        """
        if target_language is None:
            target_language = self.default_language
            
        detected           = self.detect_language(text)
        is_target_language = (detected == target_language)

        return is_target_language