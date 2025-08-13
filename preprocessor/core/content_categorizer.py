# Dependencies
import logging
from typing import List


class ContentCategorizer:
    """
    Handles automatic content categorization based on text and URL patterns
    """
    def __init__(self, verbose: bool = False):
        """
        Initialize ContentCategorizer
        
        Arguments:
        ----------
            verbose { bool } : Enable verbose logging
        """
        self.verbose          = verbose
        
        # URL-based categorization patterns
        self.url_patterns     = {"Services"   : ['/services/', '/service/'],
                                 "Industries" : ['/industries/', '/industry/'],
                                 "Company"    : ['/about/', '/company/', '/home/'],
                                 "Content"    : ['/blog/', '/news/'],
                                 "Products"   : ['/products/', '/product/'],
                                }
                        
        # Content-based categorization keywords
        self.content_keywords = {"Services"   : ['services', 'solutions', 'development', 'consulting', 'design'],
                                 "Industries" : ['healthcare', 'fintech', 'retail', 'manufacturing', 'hospitality', 'IT'],
                                }
        
        # Setup logging
        logging.basicConfig(level = logging.DEBUG if verbose else logging.INFO)

        self.logger = logging.getLogger("ContentCategorizer")
    

    def categorize_by_url(self, url: str) -> str:
        """
        Categorize content based on URL patterns
        
        Arguments:
        -----------
            url { str } : URL to analyze
            
        Returns:
        --------
            { str }     : Category name or None if no match
        """
        if not url:
            return None
        
        url_lower = url.lower()
        
        for category, patterns in self.url_patterns.items():
            if (any(pattern in url_lower for pattern in patterns)):
                self.logger.debug(f"URL categorized as: {category}")
        
                return category
        
        return None
    

    def categorize_by_content(self, text: str) -> str:
        """
        Categorize content based on text analysis
        
        Arguments:
        ----------
            text { str } : Text content to analyze
            
        Returns:
        --------
             { str }     : Category name or None if no match
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        for category, keywords in self.content_keywords.items():
            if (any(keyword in text_lower for keyword in keywords)):
                self.logger.debug(f"Content categorized as: {category}")
                
                return category
        
        return None
    

    def categorize_content(self, text: str, url: str = "") -> str:
        """
        Automatically categorize content using both URL and text analysis
        
        Arguments:
        ----------
            text { str } : Text content to analyze

            url  { str } : URL to analyze
            
        Returns:
        --------
             { str }     : Category name
        """
        # Try URL-based categorization first (more reliable)
        url_category = self.categorize_by_url(url)
        
        if url_category:
            return url_category
        
        # Fall back to content-based categorization
        content_category = self.categorize_by_content(text)
        
        if content_category:
            return content_category
        
        # Default category
        return "General"

    
    def add_url_patterns(self, category: str, patterns: List[str]):
        """
        Add custom URL patterns for a category
        
        Arguments:
        ----------
            category { str }  : Category name

            patterns { list } : List of URL patterns to match
        """
        if category in self.url_patterns:
            self.url_patterns[category].extend(patterns)

        else:
            self.url_patterns[category] = patterns
        
        self.logger.info(f"Added {len(patterns)} URL patterns for category: {category}")
    

    def add_content_keywords(self, category: str, keywords: List[str]):
        """
        Add custom content keywords for a category
        
        Arguments:
        ----------
            category { str }  : Category name

            keywords { list } : List of keywords to match
        """
        if (category in self.content_keywords):
            self.content_keywords[category].extend(keywords)

        else:
            self.content_keywords[category] = keywords
        
        self.logger.info(f"Added {len(keywords)} keywords for category: {category}")
    

    def get_all_categories(self) -> List[str]:
        """
        Get list of all available categories
        
        Returns:
        --------
            { list }    : List of category names
        """
        url_categories     = set(self.url_patterns.keys())
        content_categories = set(self.content_keywords.keys())
        all_categories     = sorted(list(url_categories.union(content_categories)) + ["General"])
        
        return all_categories