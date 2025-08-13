# Dependencies
import logging
from typing import List
from typing import Dict
from urllib.parse import urlparse


class TagExtractor:
    """
    Handles tag extraction from content and URLs
    """
    def __init__(self, verbose: bool = False):
        """
        Initialize TagExtractor
        
        Arguments:
        ----------
            verbose { bool } : Enable verbose logging
        """
        self.verbose       = verbose
        
        # Technology and business keywords mapping
        self.tech_keywords = {'web'                     : ['Web Development'], 
                              'mobile'                  : ['Mobile Development'], 
                              'app'                     : ['App Development'],
                              'blockchain'              : ['Blockchain'], 
                              'fintech'                 : ['Fintech'], 
                              'healthcare'              : ['Healthcare'],
                              'ecommerce'               : ['E-commerce'], 
                              'saas'                    : ['SaaS'], 
                              'api'                     : ['API Development'],
                              'ui'                      : ['UI Design'], 
                              'ux'                      : ['UX Design'], 
                              'development'             : ['Development'],
                              'digital'                 : ['Digital Transformation'], 
                              'cloud'                   : ['Cloud Services'],
                              'artificial intelligence' : ['AI'], 
                              'machine learning'        : ['ML'],
                              'payment'                 : ['Payment Solutions'], 
                              'booking'                 : ['Booking System'],
                              'inventory'               : ['Inventory Management'], 
                              'crm'                     : ['CRM'],
                             }
        
        # Setup logging
        logging.basicConfig(level = logging.DEBUG if verbose else logging.INFO)
        self.logger        = logging.getLogger("TagExtractor")

    
    def extract_tags_from_url(self, url: str) -> List[str]:
        """
        Extract tags from URL path components
        
        Arguments:
        ----------
            url { str } : URL to extract tags from
            
        Returns:
        --------
            { list }    : List of extracted tags
        """
        if not url:
            return []
        
        tags = list()

        try:
            path_parts = urlparse(url).path.strip('/').split('/')
            
            for part in path_parts:
                if (part and len(part) > 2):
                    # Clean up path part and convert to title case
                    tag = part.replace('-', ' ').replace('_', ' ').title()
                    tags.append(tag)
            
            self.logger.debug(f"Extracted {len(tags)} tags from URL")
            
            return tags
            
        except Exception as e:
            self.logger.warning(f"URL tag extraction failed: {e}")
            return []
    

    def extract_tags_from_content(self, text: str) -> List[str]:
        """
        Extract technology and business tags from text content
        
        Arguments:
        ----------
            text { str } : Text content to analyze
            
        Returns:
        --------
            { list }     : List of relevant tags
        """
        if not text:
            return []
        
        tags       = list()
        text_lower = text.lower()
        
        for keyword, tag_list in self.tech_keywords.items():
            if (keyword in text_lower):
                tags.extend(tag_list)
        
        # Remove duplicates while preserving order
        unique_tags = list()
        seen        = set()

        for tag in tags:
            if (tag not in seen):
                seen.add(tag)
                unique_tags.append(tag)
        
        self.logger.debug(f"Extracted {len(unique_tags)} content tags")
        
        return unique_tags

    
    def extract_tags_from_content_and_url(self, text: str, url: str = "") -> List[str]:
        """
        Extract tags from both content and URL
        
        Arguments:
        ----------
            text { str } : Text content to analyze

            url  { str } : URL to extract tags from
            
        Returns:
        --------
            { list }     : Combined list of unique tags
        """
        url_tags     = self.extract_tags_from_url(url)
        content_tags = self.extract_tags_from_content(text)
        
        # Combine and deduplicate
        all_tags     = url_tags + content_tags
        unique_tags  = list()
        seen         = set()
        
        for tag in all_tags:
            if (tag not in seen):
                seen.add(tag)
                unique_tags.append(tag)
        
        return unique_tags

    
    def add_custom_keywords(self, custom_keywords: Dict[str, List[str]]):
        """
        Add custom keyword mappings to the extractor
        
        Arguments:
        ----------
            custom_keywords { dict } : Dictionary mapping keywords to tag lists
        """
        self.tech_keywords.update(custom_keywords)

        self.logger.info(f"Added {len(custom_keywords)} custom keyword mappings")
