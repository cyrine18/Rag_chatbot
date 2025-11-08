# Web Scraping Scripts

This directory contains web scraping scripts for collecting product data from Hikvision and Satel websites.

## Scripts

### `hikvision_scraper.py`
Scrapes product information from Hikvision website.

**Usage:**
```bash
python scripts/hikvision_scraper.py
```

**Features:**
- Extracts product codes, names, descriptions, features
- Scrapes technical specifications
- Downloads data sheets and documents
- Saves data to CSV format

**Output:** `product_Hikvision_europe.csv`

### `satel_scraper.py`
Scrapes product information from Satel website.

**Usage:**
```bash
python scripts/satel_scraper.py
```

**Features:**
- Extracts model codes, product names, descriptions
- Scrapes technical specifications
- Downloads documents, software, and certificates
- Saves data to CSV format

**Output:** `product_satel.csv`

## Requirements

Install the required dependencies:
```bash
pip install crawl4ai beautifulsoup4 requests psutil
```

## Notes

- These scripts use async web crawling for efficient data collection
- Memory usage is monitored during scraping
- Parallel crawling is used to speed up the process
- The scrapers respect website structure and use CSS selectors for extraction

## Data Format

The scraped data is saved in CSV format with the following structure:
- Product codes/names
- Descriptions and features (pipe-separated)
- Technical specifications (pipe-separated)
- Documents and links (pipe-separated)

## Important

- Make sure you have a stable internet connection
- The scraping process may take time depending on the number of products
- Respect the website's robots.txt and terms of service
- Use these scripts responsibly and ethically

