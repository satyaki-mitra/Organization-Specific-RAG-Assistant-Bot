# Dependencies
import logging
from urllib.parse import urlparse
from nltk.tokenize import sent_tokenize


class TopicExtractor:
    """
    Handles topic extraction from content, titles, and URLs
    """
    def __init__(self, verbose: bool = False):
        """
        Initialize TopicExtractor
        
        Arguments:
        ----------
            verbose { bool } : Enable verbose logging
        """
        self.verbose = verbose
        
        # Setup logging
        logging.basicConfig(level = logging.DEBUG if verbose else logging.INFO)

        self.logger  = logging.getLogger("TopicExtractor")


    def extract_from_title(self, title: str) -> str:
        """
        Extract topic from page title
        
        Arguments:
        ----------
            title { str } : Page title
            
        Returns:
        --------
             { str }      : Cleaned title if meaningful, None otherwise
        """
        if(title and len(title.strip()) > 5):
            cleaned_title = title.strip()

            self.logger.debug(f"Extracted topic from title: {cleaned_title}")
            
            return cleaned_title
        
        return None
    

    def extract_from_url(self, url: str) -> str:
        """
        Extract topic from URL path components
        
        Arguments:
        ----------
            url { str } : URL to extract topic from
            
        Returns:
        --------
             { str }    : Topic extracted from URL, None if unsuccessful
        """
        if not url:
            return None
        
        try:
            path_parts = urlparse(url).path.strip('/').split('/')
            
            if len(path_parts) > 1:
                # Use last 2 path components for topic
                topic_parts = path_parts[-2:]
                topic       = ' '.join(topic_parts).replace('-', ' ').replace('_', ' ').title()
                
                if (len(topic) > 5):
                    self.logger.debug(f"Extracted topic from URL: {topic}")
                    
                    return topic
        
        except Exception as e:
            self.logger.warning(f"URL topic extraction failed: {e}")
        
        return None
    

    def extract_from_content(self, text: str) -> str:
        """
        Extract topic from the first meaningful sentence of content
        
        Arguments:
        ----------
            text { str } : Text content to analyze
            
        Returns:
        --------
             { str }     : First meaningful sentence as topic, None if unsuccessful
        """
        if not text:
            return None
        
        try:
            sentences = sent_tokenize(text)
            
            # Check first 3 sentences for a good topic
            for sentence in sentences[:3]:
                
                # Look for sentences with reasonable length
                if (10 < len(sentence) < 100):
                    cleaned_sentence = sentence.strip()
                    
                    self.logger.debug(f"Extracted topic from content: {cleaned_sentence}")
                    
                    return cleaned_sentence
        
        except Exception as e:
            self.logger.warning(f"Content topic extraction failed: {e}")
        
        return None
    

    def extract_topic(self, text: str, title: str = "", url: str = "") -> str:
        """
        Extract or generate topic from content using multiple strategies
        
        Arguments:
        ----------
            text  { str } : Text content

            title { str } : Page title
            
            url   { str } : URL of the content
            
        Returns:
        --------
             { str }      : Best available topic
        """
        # Priority 1: Use title if available and meaningful
        title_topic = self.extract_from_title(title)
        
        if title_topic:
            return title_topic
        
        # Priority 2: Extract from URL
        url_topic = self.extract_from_url(url)
        
        if url_topic:
            return url_topic
        
        # Priority 3: Extract from content
        content_topic = self.extract_from_content(text)
        
        if content_topic:
            return content_topic
        
        # Default fallback
        return "General Content"

    
    def extract_keywords_from_topic(self, topic: str, max_keywords: int = 5) -> list:
        """
        Extract keywords from a topic string
        
        Arguments:
        ----------
            topic        { str } : Topic string to extract keywords from

            max_keywords { int } : Maximum number of keywords to return
            
        Returns:
        --------
                { list }         : List of keywords
        """
        if not topic:
            return []
        
        # Simple keyword extraction - split and clean
        words          = topic.lower().split()
        
        # Filter out common stop words and short words
        stop_words     = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        keywords       = [word for word in words if len(word) > 2 and word not in stop_words]
        topic_keywords = keywords[:max_keywords]
        
        return topic_keywords