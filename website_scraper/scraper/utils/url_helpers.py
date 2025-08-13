# Dependencies
import re
import logging
from typing import Set
from typing import List
from typing import Optional
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.parse import parse_qs
from urllib.parse import urlencode
from urllib.parse import ParseResult

# Configure logging
logger = logging.getLogger(__name__)

# File extensions to skip during scraping
SKIP_EXTENSIONS : Set[str] = {'.jpg', 
                              '.jpeg', 
                              '.png', 
                              '.gif', 
                              '.bmp', 
                              '.webp', 
                              '.svg', 
                              '.ico', 
                              '.tiff', 
                              '.tif', 
                              '.raw', 
                              '.psd', 
                              '.ai', 
                              '.eps', 
                              '.mp3', 
                              '.wav', 
                              '.flac', 
                              '.aac', 
                              '.ogg', 
                              '.wma', 
                              '.m4a', 
                              '.opus', 
                              '.mp4', 
                              '.avi', 
                              '.mkv', 
                              '.mov', 
                              '.wmv', 
                              '.flv', 
                              '.webm', 
                              '.m4v',
                              '.mpg', 
                              '.mpeg', 
                              '.3gp', 
                              '.ogv', 
                              '.pdf', 
                              '.doc', 
                              '.docx', 
                              '.xls', 
                              '.xlsx', 
                              '.ppt', 
                              '.pptx', 
                              '.zip', 
                              '.rar', 
                              '.tar', 
                              '.gz', 
                              '.7z', 
                              '.exe', 
                              '.dmg', 
                              '.pkg', 
                              '.deb', 
                              '.rpm', 
                              '.msi', 
                              '.apk',
                             }

# Protocol schemes to skip
SKIP_PROTOCOLS  : Set[str] = {'mailto:', 
                              'tel:', 
                              'javascript:', 
                              'data:', 
                              'file:', 
                              'ftp:', 
                              'ftps:',
                             }


def normalize_url(base_url: str, url: Optional[str]) -> Optional[str]:
    """
    Handles various URL formats including relative paths, absolute paths, protocol-relative URLs, and malformed URLs
    
    Arguments:
    ----------
        base_url  { str }      : The base URL to resolve relative URLs against. Must be a valid HTTP/HTTPS URL

        url  { Optional[str] } : The URL to normalize. Can be relative or absolute. None values are handled gracefully

    Raises:
    -------
        ValueError             : If base_url is not a valid HTTP/HTTPS URL
    
    Returns:
    ---------
               { str }         : The normalized absolute URL, or None if the URL is invalid or cannot be processed
    """
    try:
        if not url:
            logger.debug("URL is None or empty, returning None")
            return None
        
        if not base_url:
            raise ValueError("base_url cannot be None or empty")
        
        # Validate base_url format
        parsed_base = urlparse(base_url)
        
        if ((not parsed_base.scheme) or (not parsed_base.netloc)):
            raise ValueError(f"Invalid base_url format : {base_url}")
        
        # Clean the URL
        url = url.strip()
        if not url:
            return None
        
        # Remove fragments for consistency
        if ('#' in url):
            url = url.split('#')[0]
            
        # Skip if URL is empty after fragment removal
        if not url:
            return None
        
        # Handle different URL formats
        if url.startswith('//'):
            # Protocol-relative URL
            normalized = f"{parsed_base.scheme}:{url}"
            logger.debug(f"Normalized protocol-relative URL: {url} -> {normalized}")
            return normalized
            
        elif url.startswith('http'):
            # Already absolute URL
            logger.debug(f"URL is already absolute: {url}")
            return url
            
        elif url.startswith('/'):
            # Absolute path
            normalized = f"{parsed_base.scheme}://{parsed_base.netloc}{url}"
            logger.debug(f"Normalized absolute path: {url} -> {normalized}")
            return normalized
            
        elif url.startswith('./'):
            # Relative path starting with ./
            try:
                normalized = urljoin(base_url, url[2:])
                logger.debug(f"Normalized relative path (./ prefix): {url} -> {normalized}")
                return normalized
            
            except Exception as e:
                logger.warning(f"Failed to join relative URL {url} with base {base_url}: {e}")
                return None
                
        elif url.startswith('../'):
            # Relative path going up directories
            try:
                normalized = urljoin(base_url, url)
                logger.debug(f"Normalized relative path (../ prefix): {url} -> {normalized}")
                return normalized
            
            except Exception as e:
                logger.warning(f"Failed to join relative URL {url} with base {base_url}: {e}")
                return None
                
        else:
            # Simple relative path
            try:
                normalized = urljoin(base_url, url)
                logger.debug(f"Normalized simple relative path: {url} -> {normalized}")
                return normalized
            
            except Exception as e:
                logger.warning(f"Failed to join relative URL {url} with base {base_url}: {e}")
                return None
                
    except ValueError:
        # Re-raise ValueError as it's expected
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error normalizing URL {url} with base {base_url}: {e}")
        return None



def is_valid_url(url: Optional[str]) -> bool:
    """
    Validates URL format and filters out unwanted protocols and file types that should not be scraped (images, audio, video, documents, etc.)
    
    Arguments:
    ----------
        url { Optional[str] } : The URL to validate. None values return False
    
    Returns:
    --------
              { bool }        : True if the URL is valid and should be scraped, False otherwise
    """
    try:
        if (not url or (not isinstance(url, str))):
            return False
        
        url = url.strip().lower()
        if not url:
            return False
        
        # Check for skip protocols first (most efficient)
        for protocol in SKIP_PROTOCOLS:
            if url.startswith(protocol):
                logger.debug(f"Skipping URL with excluded protocol: {url}")
                return False
        
        # Must start with http or https
        if (not url.startswith(('http://', 'https://'))):
            logger.debug(f"Skipping non-HTTP URL: {url}")
            return False
        
        # Parse URL to check for file extensions
        try:
            parsed = urlparse(url)
            path   = parsed.path.lower()
            
            # Check if path ends with any skip extensions
            for extension in SKIP_EXTENSIONS:
                if path.endswith(extension):
                    logger.debug(f"Skipping URL with excluded extension {extension}: {url}")
                    return False
                    
            # Additional check for query parameters that might indicate files
            if parsed.query:
                query_lower = parsed.query.lower()
                # Common patterns for file downloads
                file_indicators = ['download', 'attachment', 'file=']
                
                if any(indicator in query_lower for indicator in file_indicators):
                    logger.debug(f"Skipping URL with file download indicators: {url}")
                    return False
        
        except Exception as e:
            logger.warning(f"Error parsing URL {url}: {e}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Unexpected error validating URL {url}: {e}")
        return False



def clean_url(url: Optional[str]) -> Optional[str]:
    """
    Removes common tracking parameters while preserving functional query parameters
    Also removes URL fragments for consistency
    
    Arguments:
    ----------
        url { Optional[str] } : The URL to clean. None values return None
    
    Returns:
    --------
        { Optional[str] }     : The cleaned URL, or None if input was None or cleaning failed
    """
    try:
        if not url:
            return url
        
        # Remove common tracking parameters
        tracking_params: List[str] = ['utm_source', 
                                      'utm_medium', 
                                      'utm_campaign', 
                                      'utm_content', 
                                      'utm_term',
                                      'gclid', 
                                      'fbclid', 
                                      'msclkid', 
                                      '_ga', 
                                      '_gid', 
                                      'ref', 
                                      'referrer',
                                     ]
        
        parsed: ParseResult        = urlparse(url)
        
        # Handle query parameters
        if parsed.query:
            try:
                query_params = parse_qs(parsed.query, keep_blank_values=True)
                
                # Remove tracking parameters (case-insensitive)
                for param in list(query_params.keys()):
                    
                    if (param.lower() in [tp.lower() for tp in tracking_params]):
                        del query_params[param]
                        logger.debug(f"Removed tracking parameter: {param}")
                
                # Rebuild URL
                cleaned_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                
                if query_params:
                    new_query    = urlencode(query_params, doseq=True)
                    cleaned_url += f"?{new_query}"
                    
                logger.debug(f"Cleaned URL: {url} -> {cleaned_url}")
                return cleaned_url
                
            except Exception as e:
                logger.warning(f"Error processing query parameters for {url}: {e}")
                # Fallback: return URL without query parameters
                return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        # No query parameters, just remove fragment if present
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
    except Exception as e:
        logger.error(f"Error cleaning URL {url}: {e}")
        return url



def get_domain(url: Optional[str]) -> Optional[str]:
    """
    Extract domain from URL with error handling
    
    Arguments:
    ----------
        url { str }          : The URL to extract domain from.
    
    Returns:
    --------
        { Optional[str] }    : The domain name, or None if extraction failed.
    """
    try:
        if not url:
            return None
            
        parsed = urlparse(url)
        return parsed.netloc if parsed.netloc else None
        
    except Exception as e:
        logger.error(f"Error extracting domain from URL {url}: {e}")
        return None



def is_same_domain(url1: Optional[str], url2: Optional[str]) -> bool:
    """
    Check if two URLs belong to the same domain
    
    Arguments:
    ----------
        url1 { str } : First URL to compare

        url2 { str } : Second URL to compare
    
    Returns:
    --------
        { bool }     : True if both URLs belong to the same domain, False otherwise
    """
    try:
        if not url1 or not url2:
            return False
            
        domain1 = get_domain(url1)
        domain2 = get_domain(url2)
        
        return domain1 is not None and domain1 == domain2
        
    except Exception as e:
        logger.error(f"Error comparing domains for {url1} and {url2}: {e}")
        return False
