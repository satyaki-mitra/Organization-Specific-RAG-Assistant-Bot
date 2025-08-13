# Dependencies
import re
import logging
from typing import Any
from typing import Set
from typing import Dict
from typing import Union
from typing import Optional
from datetime import datetime
from scrapy.spiders import Spider
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings


# Configure logging
logger = logging.getLogger(__name__)


class WebsiteScraperPipeline:
    """
    Main pipeline for processing scraped website items which performs:
    - Comprehensive data cleaning
    - Validation and normalization including text cleanup, length validation, encoding fixes, and quality scoring
    
    Attributes:
    -----------
        items_processed { int } : Counter for total items processed

        items_cleaned   { int } : Counter for items that required cleaning

        items_rejected  { int } : Counter for items rejected due to quality issues
    """
    def __init__(self) -> None:
        """
        Initialize the pipeline with logging and statistics tracking
        """
        settings             = get_project_settings()
        
        self.min_content_len = settings.getint('MIN_CONTENT_LENGTH', 10)
        self.max_content_len = settings.getint('MAX_CONTENT_LENGTH', 100000)
        self.min_heading_len = settings.getint('MIN_HEADING_LENGTH', 1)
        self.max_heading_len = settings.getint('MAX_HEADING_LENGTH', 500)
        self.min_title_len   = settings.getint('MIN_TITLE_LENGTH', 0)
        self.max_title_len   = settings.getint('MAX_TITLE_LENGTH', 200)

        self.logger          = logging.getLogger(__name__)
        self.items_processed = 0
        self.items_cleaned   = 0
        self.items_rejected  = 0

        
        self.logger.info("WebsiteScraperPipeline initialized")
    

    def _validate_item_structure(self, adapter: ItemAdapter) -> bool:
        """
        Validate that item has required fields and proper structure
        
        Arguments:
        ----------
            adapter { ItemAdapter } : The item adapter to validate
        
        Returns:
        --------
                  { bool }          : True if item structure is valid, False otherwise
        """
        try:
            required_fields = ['url', 'page_title', 'content']
            
            for field in required_fields:
                if (field not in adapter):
                    self.logger.warning(f"Missing required field: {field}")
                    return False
                
                if (not isinstance(adapter[field], str)):
                    self.logger.warning(f"Field {field} is not a string: {type(adapter[field])}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating item structure: {e}")
            return False

    
    def _process_content(self, adapter: ItemAdapter) -> bool:
        """
        Process and clean the main content field
        
        Arguments:
        ----------
            adapter { ItemAdapter } : The item adapter to process
        
        Returns:
        --------
                  { bool }          : True if content was modified, False otherwise
        """
        try:
            if ('content' not in adapter):
                return False
            
            original_content = adapter['content']
            
            if (not isinstance(original_content, str)):
                return False
            
            # Clean and normalize content
            cleaned_content = self._clean_text_content(original_content)
            
            # Validate content length
            if (len(cleaned_content) < self.min_content_len):
                self.logger.warning(f"Content too short ({len(cleaned_content)} chars) for URL: {adapter.get('url', 'unknown')}")
                cleaned_content = ""  # Will be caught by quality check

            elif (len(cleaned_content) > self.max_content_len):
                self.logger.warning(f"Content too long ({len(cleaned_content)} chars), truncating for URL: {adapter.get('url', 'unknown')}")
                cleaned_content = cleaned_content[:self.max_content_len].strip()
            
            # Update adapter
            adapter['content'] = cleaned_content
            
            # Return whether content was modified
            return (cleaned_content != original_content)
            
        except Exception as e:
            self.logger.error(f"Error processing content: {e}")
            adapter['content'] = ""
            return True


    def _process_heading(self, adapter: ItemAdapter) -> bool:
        """
        Process and clean the heading field
        
        Arguments:
        ----------
            adapter { ItemAdapter } : The item adapter to process
        
        Returns:
        --------
                  { bool }          : True if heading was modified, False otherwise
        """
        try:
            if ('heading' not in adapter):
                adapter['heading'] = ""
                return True
            
            original_heading = adapter['heading']
            
            if (not isinstance(original_heading, str)):
                adapter['heading'] = str(original_heading) if original_heading else ""
                return True
            
            # Clean heading
            cleaned_heading = self._clean_heading_text(original_heading)
            
            # Validate heading length
            if (len(cleaned_heading) > self.max_heading_len):
                self.logger.warning(f"Heading too long ({len(cleaned_heading)} chars), truncating")
                cleaned_heading = cleaned_heading[:self.max_heading_len].strip()
            
            adapter['heading'] = cleaned_heading
            
            return cleaned_heading != original_heading
            
        except Exception as e:
            self.logger.error(f"Error processing heading: {e}")
            adapter['heading'] = ""
            return True

    
    def _process_page_title(self, adapter: ItemAdapter) -> bool:
        """
        Process and clean the page title field
        
        Arguments:
        ----------
            adapter { ItemAdapter } : The item adapter to process
        
        Returns:
        --------
                 { bool }           : True if page title was modified, False otherwise
        """
        try:
            if ('page_title' not in adapter):
                adapter['page_title'] = ""
                return True
            
            original_title = adapter['page_title']
            
            if (not isinstance(original_title, str)):
                adapter['page_title'] = str(original_title) if original_title else ""
                return True
            
            # Clean title
            cleaned_title = self._clean_text_content(original_title)
            
            # Validate title length
            if (len(cleaned_title) > self.max_title_len):
                self.logger.warning(f"Title too long ({len(cleaned_title)} chars), truncating")
                cleaned_title = cleaned_title[:self.max_title_len].strip()
            
            adapter['page_title'] = cleaned_title
            
            return (cleaned_title != original_title)
            
        except Exception as e:
            self.logger.error(f"Error processing page title: {e}")
            adapter['page_title'] = ""
            return True

    
    def _validate_url(self, adapter: ItemAdapter) -> bool:
        """
        Validate the URL field
        
        Arguments:
        ----------
            adapter { ItemAdapter } : The item adapter to validate
        
        Returns:
        --------
                  { bool }          : True if URL is valid, False otherwise
        """
        try:
            url = adapter.get('url', '')
            
            if (not url or not isinstance(url, str)):
                self.logger.warning("URL is missing or not a string")
                return False
            
            if (not url.startswith(('http://', 'https://'))):
                self.logger.warning(f"Invalid URL format: {url}")
                return False
            
            # Additional URL validation could be added here
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating URL: {e}")
            return False


    def _process_meta_information(self, adapter: ItemAdapter) -> bool:
        """
        Process and clean meta information
        
        Arguments:
        ----------
            adapter { ItemAdapter } : The item adapter to process
        
        Returns:
        --------
                 { bool }           : True if meta information was modified, False otherwise
        """
        try:
            if ('meta' not in adapter):
                adapter['meta'] = dict()
                return True
            
            meta = adapter['meta']
            
            if (not isinstance(meta, dict)):
                adapter['meta'] = {}
                return True
            
            original_meta = meta.copy()
            modified      = False
            
            # Clean each meta field
            for key, value in list(meta.items()):
                if (isinstance(value, str)):
                    cleaned_value = self._clean_text_content(value)
                    
                    if (cleaned_value != value):
                        meta[key] = cleaned_value
                        modified  = True

                elif value is None:
                    meta[key] = ""
                    modified  = True

                elif (not isinstance(value, (str, int, float, bool))):
                    meta[key] = str(value)
                    modified  = True
            
            return modified
            
        except Exception as e:
            self.logger.error(f"Error processing meta information: {e}")
            adapter['meta'] = {}
            return True

    
    def _clean_text_content(self, text: str) -> str:
        """
        Apply comprehensive text cleaning operations
        
        Arguments:
        ----------
            text { str } : The text to clean
        
        Returns:
        --------
            { str }      : Cleaned text
        """
        try:
            if not text:
                return ""
            
            # Remove extra whitespace and normalize
            cleaned       = re.sub(r'\s+', ' ', text).strip()
            
            # Remove HTML entities that might have been missed
            html_entities = {'&nbsp;'  : ' ',
                             '&amp;'   : '&',
                             '&lt;'    : '<',
                             '&gt;'    : '>',
                             '&quot;'  : '"',
                             '&apos;'  : "'",
                             '&#39;'   : "'",
                             '&copy;'  : '©',
                             '&reg;'   : '®',
                             '&trade;' : '™',
                            }
            
            for entity, replacement in html_entities.items():
                cleaned = cleaned.replace(entity, replacement)
            
            # Remove excessive punctuation
            cleaned = re.sub(r'([.!?]){3,}', r'\1\1\1', cleaned)
            cleaned = re.sub(r'([,-]){2,}', r'\1', cleaned)
            
            # Fix common encoding issues
            cleaned = cleaned.replace('â€™', "'")
            cleaned = cleaned.replace('â€œ', '"')
            cleaned = cleaned.replace('â€\x9d', '"')
            
            return cleaned.strip()
            
        except Exception as e:
            self.logger.error(f"Error cleaning text: {e}")
            return text


    def _clean_heading_text(self, heading: str) -> str:
        """
        Apply heading-specific cleaning operations
        
        Arguments:
        ----------
            heading { str } : The heading text to clean
        
        Returns:
        --------
              { str }       : Cleaned heading text
        """
        try:
            cleaned            = self._clean_text_content(heading)
            
            # Remove common heading prefixes/suffixes
            prefixes_to_remove = ['home >', 'home/', 'page >', 'section >']
            
            for prefix in prefixes_to_remove:
                if (cleaned.lower().startswith(prefix)):
                    cleaned = cleaned[len(prefix):].strip()
            
            # Remove excessive capitalization
            if (cleaned.isupper() and (len(cleaned) > 10)):
                cleaned = cleaned.title()
            
            return cleaned
            
        except Exception as e:
            self.logger.error(f"Error cleaning heading: {e}")
            return heading


    def _add_processing_metadata(self, adapter: ItemAdapter) -> None:
        """
        Add processing metadata to the item
        
        Arguments:
        ----------
            adapter { ItemAdapter } : The item adapter to add metadata to
        """
        try:
            # Set default values if missing
            if ('content_type' not in adapter):
                adapter['content_type'] = 'general'
            
            if ('priority' not in adapter):
                adapter['priority'] = 0
            
            # Add processing timestamp
            adapter['processed_at']   = datetime.utcnow().isoformat()
            
            # Track which pipeline processed it
            adapter['processed_by']   = self.__class__.__name__
            
            # Add quick stats for debugging and auditing
            adapter['content_length'] = len(adapter.get('content', '') or '')
            adapter['title_length']   = len(adapter.get('page_title', '') or '')
            adapter['heading_length'] = len(adapter.get('heading', '') or '')

        except Exception as e:
            self.logger.error(f"Error adding processing metadata: {e}")


    def _final_quality_check(self, adapter: ItemAdapter) -> bool:
        """
        Perform a final quality check before accepting the item.

        Arguments:
        ----------
            adapter { ItemAdapter } : The item adapter to validate

        Returns:
        --------
                  { bool }          : True if the item passes the quality check, False otherwise
        """
        try:
            # Ensure essential fields are present and non-empty
            if (not adapter.get('url') or not adapter.get('content')):
                self.logger.debug(f"Item failed quality check - missing url or content: {adapter.asdict()}")
                return False

            if (len(adapter.get('content', '')) < self.min_content_len):
                self.logger.debug(f"Item failed quality check - content too short: {adapter.get('url')}")
                return False

            if (len(adapter.get('page_title', '')) < self.min_title_len):
                self.logger.debug(f"Item failed quality check - title too short: {adapter.get('url')}")
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error during final quality check: {e}")
            return False


    def process_item(self, item: Dict[str, Any], spider: Spider) -> Dict[str, Any]:
        """
        Process each scraped item with the following operations:
        - Data type validation
        - Content cleaning and normalization
        - Length validation and truncation
        - URL validation
        - Meta information cleaning
        - Quality scoring
        
        Arguments:
        ----------
            item  { Dict[str, Any] } : The scraped item data to process

            spider     { Spider }    : The spider instance that scraped this item

        Raises:
        -------
            DropItem                 : If the item fails quality validation and should be discarded
        
        Returns:
        --------
            { Dict[str, Any] }       : The processed and validated item
        """
        try:
            adapter               = ItemAdapter(item)
            self.items_processed += 1
            original_item_str     = str(item)[:100]  # For logging
            
            # Validate item structure
            if not self._validate_item_structure(adapter):
                self.items_rejected += 1
                raise DropItem(f"Invalid item structure: {original_item_str}")
            
            # Process and clean content
            content_modified = self._process_content(adapter)
            heading_modified = self._process_heading(adapter)
            title_modified   = self._process_page_title(adapter)
            url_valid        = self._validate_url(adapter)
            meta_modified    = self._process_meta_information(adapter)
            
            # Set processing metadata
            self._add_processing_metadata(adapter)
            
            # Track cleaning statistics
            if any([content_modified, heading_modified, title_modified, meta_modified]):
                self.items_cleaned += 1
            
            # Final quality check
            if (not self._final_quality_check(adapter)):
                self.items_rejected += 1
                raise DropItem(f"Item failed quality check: {adapter.get('url', 'unknown')}")
            
            if not url_valid:
                self.logger.warning(f"Item has invalid URL but passed quality check: {adapter.get('url')}")
            
            self.logger.debug(f"Successfully processed item: {adapter.get('url', 'unknown')}")
            return item
            
        except DropItem:
            # Re-raise DropItem exceptions
            raise
        
        except Exception as e:
            self.logger.error(f"Unexpected error processing item: {e}")
            self.items_rejected += 1
            raise DropItem(f"Processing error: {str(e)}")
