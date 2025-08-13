# 🕷️ Website Data Scraper - Intelligent Content Extraction Tool

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Scrapy](https://img.shields.io/badge/Scrapy-2.11%2B-green.svg)](https://scrapy.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **A production-grade, modular web scraping framework that transforms unstructured web pages into clean, structured datasets with intelligent content extraction and automated data cleaning.**

----

## 🎯 Project Overview

A full-featured scraping solution powered by Scrapy, designed for:

- **Scalability** → Handles large, deep crawls efficiently

- **Flexibility** → Works across varied website structures

- **Data Quality** → Enforces cleaning, validation, and deduplication

This tool is ideal for research, analytics, content monitoring, or any workflow that needs structured data from the web.

---

### 🌟 Key Features

- **Modular Architecture**: Clean separation of concerns with base classes and utilities

- **Intelligent Extraction**: 
  - Content segmentation by headings (H1-H6)
  - Metadata extraction (Open Graph, SEO tags)
  - Smart content combination from multiple HTML elements

- **Data Quality Pipeline**:
  - Text normalization and cleaning
  - Length validation and truncation
  - Comprehensive error handling

- **Respectful Crawling**:
  - Configurable delays and concurrency
  - robots.txt compliance
  - Automatic throttling

----

## 🚀 Quick Start

### 1. Navigate to the project folder
```bash
cd website_scraper
```

### 2. Install dependencies
```bash
pip install scrapy itemadapter
```

### 3. Run the scraper programmatically
Update company_url and output_file in the script (or pass them as arguments if you adapt it for CLI):

```python
if __name__ == "__main__":
    company_url = "https://example.com"
    output_file = "outputs/data.jsonl"

    scrape(start_url   = company_url, 
           output_file = output_file,
          )
```

### 4. Run the scraper (default: itobuz.com)
```bash 
python run_scraper.py
```

### 5. Output & Logs
- Scraped data will be saved in outputs/data.jsonl (JSON Lines format).

- Logs will be saved under ../logs/scraper_logs/ with a timestamped filename.

---

## Project Structure
```
website-scraper/
├── run_scraper.py              # Main entry point
├── scrapy.cfg                  # Scrapy configuration
├── data/                       # Output directory
└── scraper/
    ├── settings.py             # Scraping configuration
    ├── pipelines.py            # Data processing pipelines
    ├── spiders/
    │   ├── base_spider.py      # Base spider class
    │   └── website_spider.py   # Main extraction logic
    └── utils/
        └── url_helpers.py      # URL processing utilities
```

--- 

## 🛠️ Key Components

### 1. Smart Content Extraction (`website_spider.py`)
- Extracts headings (H1-H6) and creates individual entries
- Combines text from multiple HTML elements (p, div, section, article)
- Extracts comprehensive metadata (Open Graph, meta tags)
- Implements depth-limited crawling

### 2. Data Processing Pipelines (`pipelines.py`)
- **Content Cleaning**: Removes extra whitespace, normalizes text
- **Duplicate Filtering**: Prevents duplicate entries based on URL + heading
- **Data Validation**: Ensures required fields and data quality
- **Error Logging**: Tracks processing issues for debugging

### 3. URL Management (`url_helpers.py`)
- Normalizes relative and absolute URLs
- Filters invalid protocols (mailto, javascript, etc.)
- Cleans tracking parameters
- Handles edge cases in URL parsing

### 4. Configuration Management (`settings.py`)
- Centralized scraping behavior control
- Performance tuning parameters
- Respectful crawling settings (delays, concurrent requests)
- Pipeline configuration and priorities

---

## ⚙️ Configuration Options

```python
# Performance Settings
CONCURRENT_REQUESTS = 8          # Parallel request handling
DOWNLOAD_DELAY = 1              # Respectful request spacing
DEPTH_LIMIT = 100               # Maximum crawl depth

# Quality Settings
ROBOTSTXT_OBEY = True           # Ethical scraping compliance
AUTOTHROTTLE_ENABLED = True     # Dynamic rate adjustment
RETRY_TIMES = 3                 # Fault tolerance
```

---

## 🎯 Problem-Solving Approach

| Challenge                     | Solution                                           |
| ----------------------------- | -------------------------------------------------- |
| Extracting meaningful content | Semantic HTML parsing + heading-based segmentation |
| Data consistency              | Cleaning, deduplication, and strict validation     |
| Scalability                   | Modular spiders, pipelines, and utilities          |

---

## 📌 Notes

- Doesn’t handle JavaScript-rendered content (needs Playwright/Selenium integration)

- Currently outputs to files only (DB support can be added)

- Basic throttling—can be upgraded with advanced rate-limiting

---

*This project showcases practical skills in web scraping, data processing, and software architecture. It demonstrates the ability to build production-ready tools with clean, maintainable code while considering ethical scraping practices and scalability challenges.*