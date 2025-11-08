"""
Satel Product Web Scraper

This script scrapes product information from Satel website and saves it to CSV.
"""
import asyncio
import os
import json
import csv
import sys
import psutil
import requests
from typing import List
from bs4 import BeautifulSoup
from crawl4ai import (
    AsyncWebCrawler,
    CrawlerRunConfig,
    CacheMode,
    CrawlResult,
    JsonCssExtractionStrategy,
    BrowserConfig
)
schema = {
  "name": "satel Product",
  "baseSelector": "body",
  "fields": [
    {
      "name": "model_code",
      "selector": "h1.product_symbol",
      "type": "text"
    },
    {
      "name": "product_name",
      "selector": "h1#productname",
      "type": "text"
    },
    {
      "name": "description",
      "selector": "div#leftpane > p",
      "type": "text"
    },
    {
      "name": "features_description",
      "selector": "div#leftpane > ul > li",
      "type": "list",
      "fields": [
        {
          "name": "feature",
          "type": "text"
        }
      ]
    },
    {
      "name": "technical_specifications",
      "selector": "#dg_specs > div.row",
      "type": "list",
      "fields": [
        {
          "name": "spec_name",
          "selector": "div.cell:nth-child(1)",
          "type": "text"
        },
        {
          "name": "spec_value",
          "selector": "div.cell:nth-child(2)",
          "type": "text"
        }
      ]
    },
    {
      "name": "documents",
      "selector": "#dg_docs > div.row",
      "type": "list",
      "fields": [
        {
          "name": "filename",
          "selector": "div.cell:nth-child(1) > a",
          "type": "text"
        },
        {
          "name": "file_url",
          "selector": "div.cell a[href]",
          "type": "attribute",
          "attribute": "href"
        },
        {
          "name": "document_type",
          "selector": "div.cell:nth-child(2)",
          "type": "text"
        },
        {
          "name": "update_date",
          "selector": "div.cell:nth-child(3)",
          "type": "text"
        },
        {
          "name": "file_size",
          "selector": "div.cell:nth-child(4)",
          "type": "text"
        }
      ]
    },
    {
      "name": "softwares",
      "selector": "#dg_soft > div.row",
      "type": "list",
      "fields": [
        {
          "name": "software_name",
          "selector": "div.cell:nth-child(1) > a",
          "type": "text"
        },
        {
          "name": "software_url",
          "selector": "div.cell:nth-child(1) > a",
          "type": "attribute",
          "attribute": "href"
        },
        {
          "name": "language",
          "selector": "div.cell:nth-child(2)",
          "type": "text"
        },
        {
          "name": "version_date",
          "selector": "div.cell:nth-child(3)",
          "type": "text"
        },
        {
          "name": "file_size",
          "selector": "div.cell:nth-child(4)",
          "type": "text"
        }
      ]
    },
    {
      "name": "certificates",
      "selector": "#dg_cert > div.row",
      "type": "list",
      "fields": [
        {
          "name": "certificate_name",
          "selector": "div.cell:nth-child(1) > a",
          "type": "text"
        },
        {
          "name": "certificate_url",
          "selector": "div.cell:nth-child(1) > a",
          "type": "attribute",
          "attribute": "href"
        },
        {
          "name": "certificate_type",
          "selector": "div.cell:nth-child(2)",
          "type": "text"
        },
        {
          "name": "update_date",
          "selector": "div.cell:nth-child(3)",
          "type": "text"
        },
        {
          "name": "file_size",
          "selector": "div.cell:nth-child(4)",
          "type": "text"
        },
            {
      "name": "specific_documents",
      "selector": "#dg_info_materials div.row",
      "type": "list",
      "fields": [
        {
          "name": "document_title",
          "selector": "div.cell:nth-child(1) a",
          "type": "text"
        },
        {
          "name": "document_url",
          "selector": "div.cell:nth-child(1) a",
          "type": "attribute",
          "attribute": "href"
        },
        {
          "name": "file_size",
          "selector": "div.cell:nth-child(2)",
          "type": "text"
        }
      ]
    }
      ]
    },
    {
  "name": "specific_document_row0",
  "selector": "#dg_info_materials div#row0",  
  "type": "list",
  "fields": [
   
    {
      "name": "document_url",
      "selector": "div.cell:nth-child(1) a", 
      "type": "attribute",
      "attribute": "href"
    },
   
  ]
}
    


  ]
}



#this function is to scape the content of a page:
async def demo_css_structured_extraction_no_schema(url):   

    schema = {
  "name": "satel Product",
  "baseSelector": "body",
  "fields": [
    {
      "name": "model_code",
      "selector": "h1.product_symbol",
      "type": "text"
    },
    {
      "name": "product_name",
      "selector": "h1#productname",
      "type": "text"
    },
    {
      "name": "description",
      "selector": "div#leftpane > p",
      "type": "text"
    },
    {
      "name": "features_description",
      "selector": "div#leftpane > ul > li",
      "type": "list",
      "fields": [
        {
          "name": "feature",
          "type": "text"
        }
      ]
    },
    {
      "name": "technical_specifications",
      "selector": "#dg_specs > div.row",
      "type": "list",
      "fields": [
        {
          "name": "spec_name",
          "selector": "div.cell:nth-child(1)",
          "type": "text"
        },
        {
          "name": "spec_value",
          "selector": "div.cell:nth-child(2)",
          "type": "text"
        }
      ]
    },
    {
      "name": "documents",
      "selector": "#dg_docs > div.row",
      "type": "list",
      "fields": [
        {
          "name": "filename",
          "selector": "div.cell:nth-child(1) > a",
          "type": "text"
        },
        {
          "name": "file_url",
          "selector": "div.cell:nth-child(1) > a",
          "type": "attribute",
          "attribute": "href"
        },
        {
          "name": "document_type",
          "selector": "div.cell:nth-child(2)",
          "type": "text"
        },
        {
          "name": "update_date",
          "selector": "div.cell:nth-child(3)",
          "type": "text"
        },
        {
          "name": "file_size",
          "selector": "div.cell:nth-child(4)",
          "type": "text"
        }
      ]
    },
    {
      "name": "softwares",
      "selector": "#dg_soft > div.row",
      "type": "list",
      "fields": [
        {
          "name": "software_name",
          "selector": "div.cell:nth-child(1) > a",
          "type": "text"
        },
        {
          "name": "software_url",
          "selector": "div.cell:nth-child(1) > a",
          "type": "attribute",
          "attribute": "href"
        },
        {
          "name": "language",
          "selector": "div.cell:nth-child(2)",
          "type": "text"
        },
        {
          "name": "version_date",
          "selector": "div.cell:nth-child(3)",
          "type": "text"
        },
        {
          "name": "file_size",
          "selector": "div.cell:nth-child(4)",
          "type": "text"
        }
      ]
    },
    {
      "name": "certificates",
      "selector": "#dg_cert > div.row",
      "type": "list",
      "fields": [
        {
          "name": "certificate_name",
          "selector": "div.cell:nth-child(1) > a",
          "type": "text"
        },
        {
          "name": "certificate_url",
          "selector": "div.cell:nth-child(1) > a",
          "type": "attribute",
          "attribute": "href"
        },
        {
          "name": "certificate_type",
          "selector": "div.cell:nth-child(2)",
          "type": "text"
        },
        {
          "name": "update_date",
          "selector": "div.cell:nth-child(3)",
          "type": "text"
        },
        {
          "name": "file_size",
          "selector": "div.cell:nth-child(4)",
          "type": "text"
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
            config=config)
        
        for result in results:
            print(f'URL: {result.url}')
            print(f" success:{result.success}")
            if result.success:
                data=json.loads(result.extracted_content)
                print(json.dumps(data, indent=3)) 
            else :
                print("failed to cral")




def get_product_urls(category_url):
    response = requests.get(category_url)
    soup = BeautifulSoup(response.text, "html.parser")
    hrefs=[]
# Use the refined selector
    links = soup.select("div#rightpane div.groups h2 > a")

# Print the text and href
    for link in links:
        href = link.get("href")
        hrefs.append('https://www.satel.eu'+href)


        #text = link.text.strip()
        #print(f"{text} => {href}")
    len(links)
    return(hrefs)



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
def save_products_to_csv(products, filename="products.csv"):
    """Sauvegarde un CSV avec champs principaux + listes concaténées"""

    def flatten_product(product):
     flat = {}
     flat['model_code'] = product.get('model_code', '')
     flat['product_name'] = product.get('product_name', '')
     flat['description'] = product.get('description', '')

    # Features list
     flat['features_description'] = '|'.join(
        f.get('feature', '') for f in product.get('features_description', [])
    )

    # Technical specifications
     flat['technical_specifications'] = '|'.join(
        f"{s.get('spec_name','')}:{s.get('spec_value','')}"
        for s in product.get('technical_specifications', [])
     )

    # Documents - extract all fields
     flat['documents'] = '|'.join(
        f"{d.get('filename','')}[{d.get('file_url','')}],{d.get('document_type','')},{d.get('update_date','')},{d.get('file_size','')}"
        for d in product.get('documents', [])
    )

    # Softwares - extract all fields
     flat['softwares'] = '|'.join(
        f"{s.get('software_name','')}[{s.get('software_url','')}],{s.get('language','')},{s.get('version_date','')},{s.get('file_size','')}"
        for s in product.get('softwares', [])
    )

    # Certificates - extract all fields
     flat['certificates'] = '|'.join(
        f"{c.get('certificate_name','')}[{c.get('certificate_url','')}],{c.get('certificate_type','')},{c.get('update_date','')},{c.get('file_size','')}"
        for c in product.get('certificates', [])
    )
    # Specific document row0 - extract only URL if exists
     flat['specific_document_row0'] = '|'.join(
          f"{sd.get('document_url','')}"
          for sd in product.get('specific_document_row0', [])
      ) if product.get('specific_document_row0') else ''


     return flat

    if not products:
        print("No products to save.")
        return

    # Flatten nested list of products
    flat_products = []
    for sublist in products:
        if isinstance(sublist, list):
            flat_products.extend(sublist)
        else:
            flat_products.append(sublist)

    if not flat_products:
        print("No products to save.")
        return

    header = flatten_product(flat_products[0]).keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for p in flat_products:
            writer.writerow(flatten_product(p))

import asyncio

async def main():
    category_url = "https://www.satel.eu/fr/cat/357"

    print(f"Récupération des URLs produits à partir de la catégorie : {category_url}")
    product_urls = get_product_urls(category_url)
    print(f"{len(product_urls)} URLs produits trouvées.")

    print("Début du crawling parallèle...")
    extracted_data = await crawl_parallel(product_urls)
    
    print(f"Données extraites pour {len(extracted_data)} produits.")
    print(extracted_data)
    print("Sauvegarde des données produits dans products.csv")
    save_products_to_csv(extracted_data, filename="product_satel.csv")


    #save_to_csv(data)

if __name__ == "__main__":
    asyncio.run(main())

