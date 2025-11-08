"""
Hikvision Product Web Scraper

This script scrapes product information from Hikvision website and saves it to CSV.
"""
import asyncio
import os
import json
import csv
import re
import sys
import psutil
import requests
import xml.etree.ElementTree as ET
from typing import List
from crawl4ai import (
    AsyncWebCrawler,
    CrawlerRunConfig,
    CacheMode,
    CrawlResult,
    JsonCssExtractionStrategy,
    BrowserConfig
)
schema= {
  "name": "hikvision Product",
  "baseSelector": "body",
  "fields": [
    {
      "name": "product_code",
      "selector": "div.product_description_title h2",
      "type": "text",
    },
    {
      "name": "product_name",
      "selector": "div.product_description-wrapper h1.prod_name",
      "type": "text"
    },
    {
      "name": "description_features",
      "selector": "div.product_description-wrapper ul.product_description_item-list > li.product_description_item",
      "type": "list",
      "fields": [
        {
          "name": "feature",
          "type": "text"
        }
      ]
    },
    {
      "name": "data_sheet",
      "selector": "div.product_description_tab_container.data_sheet_sales_Inquiry_container a.product_data_sheet.hiknow-link.at-download",
      "type": "attribute",
      "attribute": "href"
    },
    {
      "name": "data_sheet_en",
      "selector": "div.product_description_tab_container.data_sheet_sales_Inquiry_container a.product_data_sheet.products__links.hiknow-link",
      "type": "attribute",
      "attribute": "href"
    },

    {
      "name": "available_models",
      "selector": "div.product_description-wrapper div.content-list > div.content-item",
      "type": "list",
      "fields": [
        {
          "name": "model",
          "type": "text"
        }
      ]
    },
     {
            "name": "technical_specifications",
            "selector": "ul.tech-specs-items-description[data-target]",  # each category block
            "type": "nested_list",
            "fields": [
                {
                    "name": "category",
                    "selector": "li.tech-specs-items-description-list > span.tech-specs-items-description__title--heading",
                    "type": "text"
                },
                {
                    "name": "specs",
                    "selector": "li.tech-specs-items-description-list:not(:first-child)",
                    "type": "list",
                    "fields": [
                        {
                            "name": "spec_name",
                            "selector": "span.tech-specs-items-description__title",
                            "type": "text"
                        },
                        {
                            "name": "spec_value",
                            "selector": "span.tech-specs-items-description__title-details",
                            "type": "text",
                            "optional": True
                        }
                    ]
                }
            ]
        }


  ]
}

async def demo_css_structured_extraction_no_schema(url):   

    schema= {
  "name": "hikvision Product",
  "baseSelector": "body",
  "fields": [
    {
      "name": "product_code",
      "selector": "div.product_description_title h2",
      "type": "text",
    },
    {
      "name": "product_name",
      "selector": "div.product_description-wrapper h1.prod_name",
      "type": "text"
    },
    {
      "name": "description_features",
      "selector": "div.product_description-wrapper ul.product_description_item-list > li.product_description_item",
      "type": "list",
      "fields": [
        {
          "name": "feature",
          "type": "text"
        }
      ]
    },
    {
      "name": "documents",
      "selector": "div.product_description-wrapper div.product_description_tab_container a.at-download",
      "type": "list",
      "fields": [
        {
          "name": "document_type",
          "selector": "div.card-space",
          "type": "text"
        },
        {
          "name": "document_url",
          "selector": "a.at-download",
          "type": "attribute",
          "attribute": "href"
        }
      ]
    },
    {
      "name": "available_models",
      "selector": "div.product_description-wrapper div.content-list > div.content-item",
      "type": "list",
      "fields": [
        {
          "name": "model",
          "type": "text"
        }
      ]
    },
     {
            "name": "technical_specifications",
            "selector": "ul.tech-specs-items-description[data-target]",  # each category block
            "type": "nested_list",
            "fields": [
                {
                    "name": "category",
                    "selector": "li.tech-specs-items-description-list > span.tech-specs-items-description__title--heading",
                    "type": "text"
                },
                {
                    "name": "specs",
                    "selector": "li.tech-specs-items-description-list:not(:first-child)",
                    "type": "list",
                    "fields": [
                        {
                            "name": "spec_name",
                            "selector": "span.tech-specs-items-description__title",
                            "type": "text"
                        },
                        {
                            "name": "spec_value",
                            "selector": "span.tech-specs-items-description__title-details",
                            "type": "text",
                            "optional": True
                        }
                    ]
                }
            ]
        }


  ]
}


     





    extraction_startegy=JsonCssExtractionStrategy(schema=schema)
    config=CrawlerRunConfig(extraction_strategy=extraction_startegy,        cache_mode = CacheMode.BYPASS,
)
    #use the fast css extraction (no llm call during extraction)
    async with AsyncWebCrawler() as crawler :
        results : List[CrawlResult]=await crawler.arun(
            url,
            config=config,bypass_cache=True, magic=True)
        
        for result in results:
            print(f'URL: {result.url}')
            print(f" success:{result.success}")
            if result.success:
                data=json.loads(result.extracted_content)
                print(json.dumps(data, indent=3)) 
            else :
                print("failed to cral")

def get_product_urls():
    sitemap_url = "https://www.hikvision.com/fr/sitemap.xml"

    # Fetch the sitemap XML content
    response = requests.get(sitemap_url)
    response.raise_for_status()

    # Parse XML content
    root = ET.fromstring(response.content)

    # Namespace dictionary to use for XML parsing
    ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    # Extract all URLs
    all_urls = [loc.text for loc in root.findall('ns:url/ns:loc', ns)]

    def is_product_url(url: str) -> bool:
        # Match if the last segment of the path contains at least one digit
        pattern = r'/d[^/]*'
        return re.search(pattern, url) is not None

    # Filter product URLs
    product_urls_fr = [
        url for url in all_urls 
        if ("/products/" in url) and (is_product_url(url=url))
    ]

    # Convert to English by replacing /fr/ with /en/
    product_urls_en = [url.replace("/fr/", "/en/") for url in product_urls_fr]

    print(f"Total URLs in sitemap: {len(all_urls)}")
    print(f"Number of product URLs (FR): {len(product_urls_fr)}")
    print(f"Number of product URLs (EN): {len(product_urls_en)}")

    return product_urls_en

def get_product_urls_europe():
    sitemap_url = "https://www.hikvision.com/fr/sitemap.xml"

    # Fetch the sitemap XML content
    response = requests.get(sitemap_url)
    response.raise_for_status()

    # Parse XML content
    root = ET.fromstring(response.content)

    # Namespace dictionary to use for XML parsing
    ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    # Extract all URLs
    all_urls = [loc.text for loc in root.findall('ns:url/ns:loc', ns)]

    def is_product_url(url: str) -> bool:
        # Match if the last segment of the path contains at least one digit
        pattern = r'/d[^/]*'
        return re.search(pattern, url) is not None

    # Filter product URLs
    product_urls_fr = [
        url for url in all_urls 
        if ("/products/" in url) and (is_product_url(url=url))
    ]

    # Convert to Europe by replacing /fr/ with /europe/
    product_urls_europe = [url.replace("/fr/", "/europe/") for url in product_urls_fr]

    print(f"Total URLs in sitemap: {len(all_urls)}")
    print(f"Number of product URLs (FR): {len(product_urls_fr)}")
    print(f"Number of product URLs (Europe): {len(product_urls_europe)}")

    return product_urls_europe

async def crawl_parallel(urls: List[str], max_concurrent: int = 3):
    print("\n=== Parallel Crawling with Browser Reuse + Memory Check ===")

    # Memory tracking
    peak_memory = 0
    process = psutil.Process(os.getpid())

    def log_memory(prefix: str = ""):
        nonlocal peak_memory
        current_mem = process.memory_info().rss
        if current_mem > peak_memory:
            peak_memory = current_mem
        print(f"{prefix} Current Memory: {current_mem // (1024 * 1024)} MB, Peak: {peak_memory // (1024 * 1024)} MB")

    # Browser configuration
    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )

    extraction_strategy = JsonCssExtractionStrategy(schema=schema)
    crawl_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        cache_mode=CacheMode.BYPASS
    )

    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    extracted_data = []
    success_count = 0
    fail_count = 0

    try:
        for i in range(0, len(urls), max_concurrent):
            batch = urls[i : i + max_concurrent]
            tasks = []

            for j, url in enumerate(batch):
                session_id = f"parallel_session_{i + j}"
                task = crawler.arun(url=url, config=crawl_config, session_id=session_id)
                tasks.append(task)

            log_memory(prefix=f"Before batch {i // max_concurrent + 1}: ")

            results = await asyncio.gather(*tasks, return_exceptions=True)

            log_memory(prefix=f"After batch {i // max_concurrent + 1}: ")

            for idx, result in enumerate(results):
                url = batch[idx]

                if isinstance(result, Exception):
                    print(f"Error crawling {url}: {result}")
                    fail_count += 1
                    continue

                if result.success:
                    try:
                        data = json.loads(result.extracted_content)
                        extracted_data.append(data)
                        print(f"The {i + idx + 1} link is extracted")
                        print(f"The data is {data}")
                        success_count += 1
                    except json.JSONDecodeError:
                        print(f"Failed to parse JSON for {url}")
                        fail_count += 1
                else:
                    print(f"Failed to crawl {url}: {result.error_message}")
                    fail_count += 1

        print("\nSummary:")
        print(f"  - Successfully crawled: {success_count}")
        print(f"  - Failed: {fail_count}")

    finally:
        print("\nClosing crawler...")
        await crawler.close()
        log_memory(prefix="Final: ")
        print(f"\nPeak memory usage (MB): {peak_memory // (1024 * 1024)}")

    return extracted_data


import csv

def save_hikvision_products_to_csv(products, filename="hikvision_products.csv"):
    """Sauvegarde un CSV avec champs principaux + listes concaténées pour le schéma Hikvision"""

    def flatten_product(product):
        flat = {}
        # Champs principaux
        flat['product_code'] = product.get('product_code', '')
        flat['product_name'] = product.get('product_name', '')
        flat['data_sheet'] = product.get('data_sheet', '')
        flat['data_sheet_en'] = product.get('data_sheet_en', '')
        # Description features
        flat['description_features'] = '|'.join(
            f.get('feature', '') for f in product.get('description_features', [])
        )

        # Documents
        flat['documents'] = '|'.join(
            f"{d.get('document_type','')}[{d.get('document_url','')}]"
            for d in product.get('documents', [])
        )

        # Available models
        flat['available_models'] = '|'.join(
            m.get('model', '') for m in product.get('available_models', [])
        )

        # Technical specifications
        tech_specs_flat = []
        for cat in product.get('technical_specifications', []):
            cat_name = cat.get('category', '')
            for spec in cat.get('specs', []):
                spec_name = spec.get('spec_name', '')
                spec_value = spec.get('spec_value', '')
                tech_specs_flat.append(f"{cat_name}:{spec_name}:{spec_value}")
        flat['technical_specifications'] = '|'.join(tech_specs_flat)

        return flat

    if not products:
        print("No products to save.")
        return

    # Aplatir la liste des produits
    flat_products = []
    for sublist in products:
        if isinstance(sublist, list):
            flat_products.extend(sublist)
        else:
            flat_products.append(sublist)

    header = flatten_product(flat_products[0]).keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for p in flat_products:
            writer.writerow(flatten_product(p))


















async def main():
    print(f"Récupération des URLs produits à partir de la catégorie ")
    product_urls = get_product_urls_europe()

    

    print("Début du crawling parallèle...")
    extracted_data = await crawl_parallel(product_urls)
    
    print(f"Données extraites pour {len(extracted_data)} produits.")
    print(extracted_data)


    print("Sauvegarde des données produits dans products.csv")
    save_hikvision_products_to_csv(extracted_data, filename="product_Hikvision_europe.csv")


if __name__ == "__main__":
    asyncio.run(main())