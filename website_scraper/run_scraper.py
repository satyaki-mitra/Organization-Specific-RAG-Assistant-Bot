# Dependencies
import os
import logging
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scraper.spiders.website_spider import WebsiteSpider 



def scrape(start_url: str, output_file: str = None):
    """
    Programmatically run the WebsiteSpider using project settings, saving logs to scraper_logs/ and output to the given file

    Arguments:
    ----------
        start_url   { str } : The URL of the website which one to scrape

        output_file { str } : The name or path of the file where to save scraped data
    """
    # Create output and log folders
    os.makedirs(os.path.dirname(output_file), exist_ok = True)
    os.makedirs('../logs/scraper_logs', exist_ok = True)

    # Log file name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file  = os.path.join('../logs/scraper_logs', f"scrape_{timestamp}.log")

    # Configure logging for Scrapy
    logging.basicConfig(filename = log_file,
                        filemode = 'w',
                        format   = '%(asctime)s [%(levelname)s] %(message)s',
                        level    = logging.INFO,
                       )

    # Also suppress too much console logging from Scrapy
    logging.getLogger('scrapy').setLevel(logging.CRITICAL)

    # Get base settings from settings.py
    settings = get_project_settings()

    # Override feed export settings
    settings.update({'FEEDS'     : {output_file: {'format'    : 'jsonlines',
                                                  'overwrite' : True,
                                                 },
                                   },
                     'LOG_FILE'  : log_file,
                     'LOG_LEVEL' : 'INFO',
                   })

    process = CrawlerProcess(settings)

    process.crawl(WebsiteSpider, 
                  start_url = start_url,
                 )

    process.start()

    print(f"\n✅ Scraping complete! Data saved to {output_file}")
    print(f"📝 Logs saved to {log_file}")


# Execute
if __name__ == "__main__":
    
    company_url = "<url_here>"
    output_file = "<output_file_path_here>"

    scrape(start_url   = company_url,
           output_file = output_file,
          )
