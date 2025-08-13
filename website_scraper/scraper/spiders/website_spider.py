# Dependencies
import re
import logging
from typing import Set
from typing import Any
from typing import Dict
from typing import List 
from typing import Union
from typing import Optional
from typing import Generator
from scrapy.http import Request
from scrapy.http import Response
from .base_spider import BaseSpider
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings


# Configure logging
logger = logging.getLogger(__name__)


class WebsiteSpider(BaseSpider):
    """
    Spider for extracting structured content from websites such as:
    
    - Intelligent content extraction, 
    - Creating separate entries for each heading found on pages while maintaining content-heading relationships
    - It outputs data in JSONL format suitable for analysis and processing
    
    Attributes:
    -----------
        name              { str }        : Spider identifier

        max_depth      { Optional[int] } : Maximum crawling depth

        follow_all_links  { bool }       : Whether to follow all discovered links
    """
    name: str = 'website'

    def __init__(self, start_url: Optional[str] = None, allowed_domains: Optional[Union[str, List[str]]] = None, max_depth: Optional[int] = None, 
                 follow_all_links: bool = True, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the website spider with content extraction configuration
        
        Arguments:
        ----------
            start_url                 { Optional[str] }        : The initial URL to start scraping from

            allowed_domains { Optional[Union[str, List[str]]]} : Domain(s) allowed for scraping

            max_depth                 { Optional[int] }        : Maximum depth to crawl. None means unlimited

            follow_all_links              { bool }             : Whether to follow all discovered links

            *args                                              : Variable length argument list passed to parent class

            **kwargs                                           : Arbitrary keyword arguments passed to parent class
        """
        try:
            super(WebsiteSpider, self).__init__(start_url, allowed_domains, *args, **kwargs)

            settings = get_project_settings()
        
            self.min_content_len = settings.getint('MIN_CONTENT_LENGTH')
            self.max_content_len = settings.getint('MAX_CONTENT_LENGTH')
            self.min_heading_len = settings.getint('MIN_HEADING_LENGTH')
            self.max_heading_len = settings.getint('MAX_HEADING_LENGTH')
            
            # Validate and set depth limit
            if max_depth is not None:
                
                if (not isinstance(max_depth, int) or (max_depth < 0)):
                    raise ValueError("max_depth must be a non-negative integer or None")
            
            self.max_depth        = max_depth
            
            # Set link following behavior
            self.follow_all_links = bool(follow_all_links)
            
            logger.info(f"WebsiteSpider initialized - max_depth: {max_depth}, follow_links: {follow_all_links}")
                       
        except Exception as e:
            logger.error(f"Failed to initialize WebsiteSpider: {e}")
            raise


    def clean_text(self, text_list: List[str]) -> str:
        """
        Processes a list of text fragments by joining them, removing extra whitespace, normalizing line breaks, and applying content quality filters
        
        Arguments:
        ----------
            text_list { List[str] } : List of text fragments to clean and join
        
        Returns:
        --------
                { str }             : Cleaned and normalized text content
        """
        try:
            if not text_list or not isinstance(text_list, (list, tuple)):
                return ""
            
            # Filter out None and empty strings
            valid_texts   = [text for text in text_list if text and isinstance(text, str)]
            
            if not valid_texts:
                return ""
            
            # Join all text fragments
            combined_text = ' '.join(valid_texts)
            
            # Remove extra whitespace and normalize
            cleaned_text  = re.sub(r'\s+', ' ', combined_text).strip()
            
            # Remove common HTML artifacts that might have been missed
            cleaned_text  = re.sub(r'&nbsp;', ' ', cleaned_text)
            cleaned_text  = re.sub(r'&amp;', '&', cleaned_text)
            cleaned_text  = re.sub(r'&lt;', '<', cleaned_text)
            cleaned_text  = re.sub(r'&gt;', '>', cleaned_text)
            cleaned_text  = re.sub(r'&quot;', '"', cleaned_text)
            
            # Final cleanup
            cleaned_text  = cleaned_text.strip()
            
            logger.debug(f"Cleaned text: {len(text_list)} fragments -> {len(cleaned_text)} characters")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error cleaning text: {e}")
            return ""


    def extract_meta_info(self, response: Response) -> Dict[str, str]:
        """
        Extracts various metadata including title, description, Open Graph tags, and other SEO-related information from the page head section
        
        Arguments:
        ----------
            response { Response } : The Scrapy response object to extract metadata from
        
        Returns:
        --------
            { Dict[str, str] }    : Dictionary containing extracted metadata with the following keys:
                                    - title          : HTML title tag content
                                    - description    : Meta description content
                                    - og_url         : Open Graph URL
                                    - og_type        : Open Graph type
                                    - og_title       : Open Graph title
                                    - og_description : Open Graph description
                                    - og_site_name   : Open Graph site name
                                    - keywords       : Meta keywords (if present)
                                    - author         : Meta author (if present)
        """
        try:
            meta: Dict[str, str]   = dict()
            
            # Basic meta tags
            meta['title']          = self._safe_extract_text(response.css('title::text').get(), 'title')
            meta['description']    = self._safe_extract_attr(response.css('meta[name="description"]::attr(content)').get(), 'description')
            
            # Open Graph tags
            meta['og_url']         = self._safe_extract_attr(response.css('meta[property="og:url"]::attr(content)').get(), 'og_url')
            meta['og_type']        = self._safe_extract_attr(response.css('meta[property="og:type"]::attr(content)').get(), 'og_type')
            meta['og_title']       = self._safe_extract_attr(response.css('meta[property="og:title"]::attr(content)').get(), 'og_title')
            meta['og_description'] = self._safe_extract_attr(response.css('meta[property="og:description"]::attr(content)').get(), 'og_description')
            meta['og_site_name']   = self._safe_extract_attr(response.css('meta[property="og:site_name"]::attr(content)').get(), 'og_site_name')
            
            # Additional meta information
            meta['keywords']       = self._safe_extract_attr(response.css('meta[name="keywords"]::attr(content)').get(), 'keywords')
            meta['author']         = self._safe_extract_attr(response.css('meta[name="author"]::attr(content)').get(), 'author')
            
            # Count non-empty meta fields
            filled_fields          = sum(1 for value in meta.values() if value.strip())

            logger.debug(f"Extracted {filled_fields}/{len(meta)} meta fields from {response.url}")
            
            return meta
            
        except Exception as e:
            logger.error(f"Error extracting meta info from {response.url}: {e}")
            # Return empty meta dict with all expected keys
            return {'title'          : '', 
                    'description'    : '', 
                    'og_url'         : '', 
                    'og_type'        : '',
                    'og_title'       : '', 
                    'og_description' : '', 
                    'og_site_name'   : '',
                    'keywords'       : '', 
                    'author'         : '',
                   }


    def _safe_extract_text(self, text: Optional[str], field_name: str) -> str:
        """
        Safely extract and clean text content with validation
        
        Arguments:
        ----------
            text   { Optional[str] } : The text to clean and validate

            field_name { str }       : Name of the field for logging purposes
        
        Returns:
        --------
                    { str }          : Cleaned text or empty string if invalid
        """
        try:
            if not text or not isinstance(text, str):
                return ""
            
            cleaned = text.strip()
            
            # Validate length: reasonable limit for meta fields
            if (len(cleaned) > 5000):  
                logger.warning(f"Truncating long {field_name}: {len(cleaned)} chars")
                cleaned = cleaned[:5000].strip()
            
            return cleaned
            
        except Exception as e:
            logger.warning(f"Error processing {field_name}: {e}")
            return ""


    def _safe_extract_attr(self, attr: Optional[str], field_name: str) -> str:
        """
        Safely extract and clean attribute content
        
        Arguments:
        ----------
            attr  { Optional[str] } : The attribute value to clean

            field_name { str }      : Name of the field for logging purposes
        
        Returns:
        --------
                   { str }          : Cleaned attribute value or empty string if invalid
        """
        return self._safe_extract_text(attr, field_name)


    def extract_content_sections(self, response: Response) -> Dict[str, str]:
        """
        Extract different types of content from the HTML response
        
        Arguments:
        ----------
            response { Response } : The Scrapy response object to extract content from
        
        Returns:
        --------
            { Dict[str, str] }    : Dictionary with different content types:
                                    - headings   : Combined heading text (H1-H6)
                                    - paragraphs : All paragraph text
                                    - articles   : Article section text
                                    - sections   : Generic section text
                                    - divs       : Div element text
                                    - lists      : List item text
                                    - combined   : All content combined
        """
        try:
            content: Dict[str, str] = dict()
            
            # Extract different content types
            content['headings']     = self.clean_text([*response.css('h1::text, h2::text, h3::text, h4::text, h5::text, h6::text').getall()])
            content['paragraphs']   = self.clean_text(response.css('p::text').getall())
            content['articles']     = self.clean_text(response.css('article *::text').getall())
            content['sections']     = self.clean_text(response.css('section *::text').getall())
            content['divs']         = self.clean_text(response.css('div::text').getall())
            content['lists']        = self.clean_text(response.css('li::text').getall())
            
            # Combine all content types
            all_parts               = [content['paragraphs'], content['articles'], content['sections'], content['divs'], content['lists']]
            content['combined']     = self.clean_text(all_parts)
            
            # Log content extraction stats
            total_chars             = sum(len(text) for text in content.values())

            logger.debug(f"Extracted {total_chars} characters of content from {response.url}")
            
            return content
            
        except Exception as e:
            logger.error(f"Error extracting content from {response.url}: {e}")
            return {'headings'   : '', 
                    'paragraphs' : '', 
                    'articles'   : '', 
                    'sections'   : '',
                    'divs'       : '', 
                    'lists'      : '', 
                    'combined'   : '',
                   }


    def extract_individual_headings(self, response: Response) -> List[Dict[str, str]]:
        """
        Extract individual headings with their levels and text content
        
        Arguments:
        ----------
            response  { Response }   : The Scrapy response object to extract headings from
        
        Returns:
        --------
            { List[Dict[str, str]] } : List of dictionaries containing heading information:
                                        - level : Heading level (h1, h2, etc.)
                                        - text  : Heading text content
                                        - order : Order of appearance on page
        """
        try:
            headings: List[Dict[str, str]] = list()
            
            # Extract headings by level: H1 to H6
            for level in range(1, 7):  
                heading_texts = response.css(f'h{level}::text').getall()
                
                for order, heading_text in enumerate(heading_texts):
                    if (heading_text and heading_text.strip()):
                        cleaned_heading = self._validate_heading(heading_text.strip())
                        
                        if cleaned_heading:
                            headings.append({'level' : f'h{level}',
                                             'text'  : cleaned_heading,
                                             'order' : len(headings),
                                           })
            
            logger.debug(f"Extracted {len(headings)} individual headings from {response.url}")

            return headings
            
        except Exception as e:
            logger.error(f"Error extracting individual headings from {response.url}: {e}")
            return []


    def _validate_heading(self, heading: str) -> str:
        """
        Validate and clean heading text
        
        Arguments:
        ----------
            heading { str } : Raw heading text to validate
        
        Returns:
        --------
               { str }      : Validated heading text or empty string if invalid
        """
        try:
            if not heading or len(heading) < self.min_heading_len:
                return ""
            
            if (len(heading) > self.max_heading_len):
                logger.warning(f"Truncating long heading: {len(heading)} chars")
                heading = heading[:self.max_heading_len].strip()
            
            # Remove excessive punctuation
            heading = re.sub(r'[^\w\s\-.,!?()[\]{}:;]', '', heading)
            heading = re.sub(r'\s+', ' ', heading).strip()
            
            return heading
            
        except Exception as e:
            logger.warning(f"Error validating heading: {e}")
            return ""


    def _validate_content(self, content: str) -> str:
        """
        Validate content length and quality
        
        Arguments:
        ---------
            content { str } : Content to validate
        
        Returns:
        --------
              { str }       : Validated content or empty string if invalid
        """
        try:
            if (not content or (len(content) < self.min_content_len)):
                return ""
            
            if (len(content) > self.max_content_len):
                logger.warning(f"Truncating long content: {len(content)} chars")
                content = content[:self.max_content_len].strip()
            
            return content
            
        except Exception as e:
            logger.warning(f"Error validating content: {e}")
            return ""


    def parse(self, response: Response, depth: int = 0, **kwargs: Any) -> Generator[Union[Dict[str, Any], Request], None, None]:
        """
        Parse response and extracts content and metadata from web pages, creating individual entries for each heading
        found while maintaining content relationships
        
        Arguments:
        ----------
            response { Response }                                     : The Scrapy response object to parse
            
            depth       { int }                                       : Current crawling depth for this response

            **kwargs                                                  : Additional keyword arguments
        
        Yields:
        -------
            { Generator[Union[Dict[str, Any], Request], None, None] } : Dictionaries containing extracted data or Request objects for following links
        """
        try:
            logger.info(f"Parsing {response.url} at depth {depth}")
            
            # Validate response
            if (response.status != 200):
                logger.warning(f"Non-200 status {response.status} for {response.url}")
                return
            
            # Extract basic page information
            page_title       = self._safe_extract_text(response.css('title::text').get(),
                                                       field_name = 'page_title',
                                                      )
            
            # Extract metadata
            meta_info        = self.extract_meta_info(response)
            
            # Extract content sections
            content_sections = self.extract_content_sections(response)
            combined_content = self._validate_content(content_sections['combined'])
            
            if (not combined_content):
                logger.warning(f"No valid content found on {response.url}")
                return
            
            # Extract individual headings
            headings         = self.extract_individual_headings(response)
            
            # Create entries for each heading
            entries_created  = 0
            
            if headings:
                for heading_info in headings:
                    try:
                        entry = {"url"          : response.url,
                                 "page_title"   : page_title,
                                 "heading"      : heading_info['text'],
                                 "content"      : combined_content,
                                 "content_type" : "general",
                                 "priority"     : 0,
                                 "meta"         : meta_info,
                                }
                        
                        entries_created += 1

                        yield entry
                        
                    except Exception as e:
                        logger.error(f"Error creating entry for heading '{heading_info.get('text', 'unknown')}': {e}")
                        continue
            
            else:
                # No headings found, create a general entry
                try:
                    entry = {"url"          : response.url,
                             "page_title"   : page_title,
                             "heading"      : "Main Content",
                             "content"      : combined_content,
                             "content_type" : "general",
                             "priority"     : 0,
                             "meta"         : meta_info,
                            }
                    
                    entries_created += 1

                    yield entry
                    
                except Exception as e:
                    logger.error(f"Error creating general entry for {response.url}: {e}")
            
            logger.info(f"Created {entries_created} entries for {response.url}")
            
            # Follow links if enabled and within depth limit
            if (self.follow_all_links and (self.max_depth is None or depth < self.max_depth)):
                try:
                    links_followed = 0
                    
                    for link_request in self.follow_links(response):
                        # Add depth information to request meta
                        link_request.meta['depth'] = depth + 1
                        
                        # Use a lambda with default argument to capture current depth
                        link_request                = link_request.replace(callback = lambda r, d = depth + 1: self.parse(r, depth = d))
                        
                        links_followed             += 1

                        yield link_request
                    
                    logger.debug(f"Following {links_followed} links from {response.url}")
                    
                except Exception as e:
                    logger.error(f"Error following links from {response.url}: {e}")
            
        except Exception as e:
            logger.error(f"Critical error parsing {response.url}: {e}")
            
            # Yield error entry for debugging
            try:
                yield {"url"          : response.url,
                       "page_title"   : "ERROR",
                       "heading"      : "Parse Error",
                       "content"      : f"Error parsing page: {str(e)}",
                       "content_type" : "error",
                       "priority"     : -1,
                       "meta"         : {"error": str(e)},
                      }

            except Exception as yield_error:
                logger.error(f"Failed to yield error entry: {yield_error}")


    def closed(self, reason: str) -> None:
        """
        Called when the spider is closed with enhanced logging
        
        Arguments:
        ----------
            reason { str } : The reason why the spider was closed
        """
        try:
            super().closed(reason)
            
            # Log additional WebsiteSpider-specific stats
            if hasattr(self, 'crawler') and self.crawler.stats:
                stats         = self.crawler.stats
                
                items_scraped = stats.get_value('item_scraped_count', 0)
                items_dropped = stats.get_value('item_dropped_count', 0)
                pages_crawled = stats.get_value('response_received_count', 0)
                
                success_rate  = (items_scraped / max(pages_crawled, 1)) * 100
                
                logger.info(f"WebsiteSpider final summary:")
                logger.info(f"  - Pages crawled: {pages_crawled}")
                logger.info(f"  - Items scraped: {items_scraped}")
                logger.info(f"  - Items dropped: {items_dropped}")
                logger.info(f"  - Success rate: {success_rate:.1f}%")
                
        except Exception as e:
            logger.error(f"Error in spider close handler: {e}")