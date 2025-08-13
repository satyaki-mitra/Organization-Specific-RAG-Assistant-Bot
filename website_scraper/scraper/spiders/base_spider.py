# Dependencies
import scrapy
import logging
from typing import Any
from typing import List
from typing import Union
from typing import Optional
from typing import Generator
from scrapy.http import Request
from scrapy.http import Response
from urllib.parse import urlparse
from scrapy.exceptions import CloseSpider
from scraper.utils.url_helpers import get_domain
from scraper.utils.url_helpers import is_valid_url
from scraper.utils.url_helpers import normalize_url

# Configure logging
logger = logging.getLogger(__name__)


class BaseSpider(scrapy.Spider):
    """
    Base spider class with foundational features for web scraping including:
    - URL normalization and validation
    - Domain-based filtering
    - Link following with depth control
    - Error handling and logging
    - Request generation and processing
    
    Attributes:
    -----------
        start_urls      { List[str] } : List of URLs to start scraping from

        allowed_domains { List[str] } : Domains allowed for scraping

        name                { str }   : Spider identifier name
    """

    def __init__(self, start_url: Optional[str] = None, allowed_domains: Optional[Union[str, List[str]]] = None, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the base spider with URL and domain configuration
        
        Arguments:
        ----------
            start_url                { Optional[str] }          : The initial URL to start scraping from, if None, start_urls should be set elsewhere
            
            allowed_domains { Optional[Union[str, List[str]]] } : Domain(s) allowed for scraping, which can be a single domain string or list of domains
            
            *args                                               : Variable length argument list passed to parent class

            **kwargs                                            : Arbitrary keyword arguments passed to parent class
        
        Raises:
        -------
            ValueError                                          : If start_url is provided but is not a valid HTTP/HTTPS URL
            
            CloseSpider                                         : If no valid start URLs or allowed domains are configured.
            
        """
        try:
            super(BaseSpider, self).__init__(*args, **kwargs)
            
            # Initialize start URLs
            if start_url:
                if not isinstance(start_url, str):
                    raise ValueError("start_url must be a string")
                
                # Validate start URL format
                parsed_url = urlparse(start_url)
                if ((not parsed_url.scheme) or (not parsed_url.netloc)):
                    raise ValueError(f"Invalid start_url format: {start_url}")
                
                if (parsed_url.scheme not in ['http', 'https']):
                    raise ValueError(f"start_url must use HTTP or HTTPS protocol: {start_url}")
                
                self.start_urls = [start_url]
                logger.info(f"Initialized spider with start URL: {start_url}")
            
            else:
                self.start_urls = []
                logger.info("Initialized spider without start URL")
            
            # Initialize allowed domains
            self.allowed_domains = self._setup_allowed_domains(start_url, allowed_domains)
            
            # Validate configuration
            if (not self.start_urls and (not hasattr(self, 'start_urls'))):
                logger.warning("No start URLs configured - spider may not work properly")
            
            if not self.allowed_domains:
                logger.warning("No allowed domains configured - all domains will be allowed")
            
            else:
                logger.info(f"Configured allowed domains: {self.allowed_domains}")
            
        except Exception as e:
            logger.error(f"Failed to initialize BaseSpider: {e}")
            raise CloseSpider(f"Spider initialization failed: {e}")


    def _setup_allowed_domains(self, start_url: Optional[str], allowed_domains: Optional[Union[str, List[str]]]) -> List[str]:
        """
        Setup and validate allowed domains configuration
        
        Arguments:
        ----------
            start_url               { Optional[str] }           : The start URL to extract domain from
            
            allowed_domains { Optional[Union[str, List[str]]] } : Explicit allowed domains

        Raises:
        -------
            ValueError                                          : If domain configuration is invalid
        
        Returns:
        --------
                          { List[str] }                         : List of validated allowed domains
        """
        try:
            domains = list()
            
            if allowed_domains:
                if (isinstance(allowed_domains, str)):
                    domains = [allowed_domains.strip()]
                
                elif (isinstance(allowed_domains, (list, tuple))):
                    domains = [domain.strip() for domain in allowed_domains if domain and domain.strip()]
                
                else:
                    raise ValueError("allowed_domains must be string or list of strings")
                
                # Validate domain formats
                for domain in domains:
                    if (not domain or '://' in domain):
                        raise ValueError(f"Invalid domain format (should not include protocol): {domain}")
                
                logger.debug(f"Using explicit allowed domains: {domains}")
                
            elif start_url:
                # Extract domain from start URL
                parsed_url = urlparse(start_url)
                
                if parsed_url.netloc:
                    domains = [parsed_url.netloc]
                    logger.debug(f"Extracted allowed domain from start_url: {domains}")
                
                else:
                    logger.warning(f"Could not extract domain from start_url: {start_url}")
            
            return domains
            
        except Exception as e:
            logger.error(f"Error setting up allowed domains: {e}")
            return []


    def follow_links(self, response: Response, callback: Optional[callable] = None) -> Generator[Request, None, None]:
        """
        Extracts all links from the response and yields Request objects for valid URLs that pass domain and content type filtering
        
        Arguments:
        ----------
            response       { Response }        : The Scrapy response object containing the page to extract links from

            callback { Optional[callable] }    : The callback function to handle responses, and defaults to self.parse if not provided
        
        Yields:
        -------
            { Generator[Request, None, None] } : Scrapy Request objects for valid links found on the page
        """
        try:
            callback       = callback or self.parse
            links_found    = 0
            links_followed = 0
            
            # Extract all href attributes from anchor tags
            href_list      = response.css('a::attr(href)').getall()

            logger.debug(f"Found {len(href_list)} potential links on {response.url}")
            
            for href in href_list:
                try:
                    if not href:
                        continue
                    
                    links_found   += 1
                    
                    # Normalize the URL
                    normalized_url = normalize_url(response.url, href)

                    if not normalized_url:
                        logger.debug(f"Failed to normalize URL: {href}")
                        continue
                    
                    # Validate URL (checks for file types, protocols, etc.)
                    if (not is_valid_url(normalized_url)):
                        logger.debug(f"URL failed validation: {normalized_url}")
                        continue
                    
                    # Check domain restrictions
                    if (not self._is_allowed_domain(normalized_url)):
                        logger.debug(f"URL not in allowed domains: {normalized_url}")
                        continue
                    
                    links_followed += 1
                    logger.debug(f"Following link: {normalized_url}")
                    
                    # Yield request with error handling
                    try:
                        yield response.follow(normalized_url, callback=callback)
                    
                    except Exception as e:
                        logger.warning(f"Failed to create request for {normalized_url}: {e}")
                        continue
                        
                except Exception as e:
                    logger.warning(f"Error processing link {href}: {e}")
                    continue
            
            logger.info(f"Processed {links_found} links, following {links_followed} on {response.url}")
            
        except Exception as e:
            logger.error(f"Critical error in follow_links for {response.url}: {e}")
            # Don't yield anything if there's a critical error


    def _is_allowed_domain(self, url: str) -> bool:
        """
        Check if URL belongs to an allowed domain
        
        Arguments:
        ----------
            url { str } : The URL to check
        
        Returns:
        --------
            { bool }    : True if the URL's domain is allowed, False otherwise
        """
        try:
            if not self.allowed_domains:
                # If no domains specified, allow all
                return True
            
            url_domain = get_domain(url)
            
            if not url_domain:
                logger.debug(f"Could not extract domain from URL: {url}")
                return False
            
            # Check if URL domain matches any allowed domain
            for allowed_domain in self.allowed_domains:
                if url_domain == allowed_domain:
                    return True
                
                # Also check for subdomains
                if url_domain.endswith(f'.{allowed_domain}'):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking domain for URL {url}: {e}")
            return False


    def parse(self, response: Response, **kwargs: Any) -> Generator[Any, None, None]:
        """
        Default parse method - provides a basic implementation that logs the response and can be used as a fallback or for testing
        
        Arguments:
        ----------
            response { Response }          : The Scrapy response object to parse

            **kwargs                       : Additional keyword arguments
        
        Yields:
        -------
            { Generator[Any, None, None] } : Items or requests (implementation dependent)
        """
        try:
            logger.info(f"Parsing response from: {response.url}")
            logger.debug(f"Response status: {response.status}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            # Basic response validation
            if response.status != 200:
                logger.warning(f"Non-200 response status {response.status} for {response.url}")
            
            # Extract basic page information
            title = response.css('title::text').get()
            if title:
                logger.info(f"Page title: {title.strip()}")
            
            # This is a base implementation - subclasses should override
            yield {'url'       : response.url,
                   'title'     : title.strip() if title else '',
                   'status'    : response.status,
                   'parsed_by' : 'BaseSpider',
                  }
            
        except Exception as e:
            logger.error(f"Error parsing response from {response.url}: {e}")
            # Yield error information for debugging
            yield {'url'       : response.url,
                   'error'     : str(e),
                   'status'    : getattr(response, 'status', 'unknown'),
                   'parsed_by' : 'BaseSpider'
                  }


    def start_requests(self) -> Generator[Request, None, None]:
        """
        Generate initial requests from start_urls with error handling

        Raises:
        -------
            CloseSpider                        : If no valid start URLs are available
        
        Yields:
        -------
            { Generator[Request, None, None] } : Initial Scrapy Request objects
        """
        try:
            if not self.start_urls:
                logger.error("No start URLs configured")
                raise CloseSpider("No start URLs available")
            
            valid_requests = 0
            
            for url in self.start_urls:
                try:
                    if not is_valid_url(url):
                        logger.warning(f"Skipping invalid start URL: {url}")
                        continue
                    
                    logger.info(f"Creating request for start URL: {url}")
                    valid_requests += 1
                    
                    yield scrapy.Request(url      = url, 
                                         callback = self.parse,
                                        )
                    
                except Exception as e:
                    logger.error(f"Failed to create request for start URL {url}: {e}")
                    continue
            
            if (valid_requests == 0):
                raise CloseSpider("No valid start URLs available")
            
            logger.info(f"Generated {valid_requests} initial requests")
            
        except CloseSpider:
            raise
        
        except Exception as e:
            logger.error(f"Critical error generating start requests: {e}")
            raise CloseSpider(f"Failed to generate start requests: {e}")


    def closed(self, reason: str) -> None:
        """
        Called when the spider is closed.
        
        Arguments:
        ----------
            reason { str } : The reason why the spider was closed
        """
        logger.info(f"Spider {self.name} closed: {reason}")
        
        # Log final statistics if available
        if hasattr(self, 'crawler') and self.crawler.stats:
            stats = self.crawler.stats
            logger.info(f"Final stats - "
                        f"Items: {stats.get_value('item_scraped_count', 0)}, "
                        f"Requests: {stats.get_value('downloader/request_count', 0)}, "
                        f"Responses: {stats.get_value('downloader/response_count', 0)}")
