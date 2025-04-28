import asyncio
import os
import re
from pathlib import Path
from urllib.parse import urlparse

# Make sure crawl4ai is installed: pip install crawl4ai

# --- Configuration ---
# The URL of the first page to crawl
start_url = "https://www.tradingview.com/pine-script-docs/welcome/"
# The base path of the documentation site
base_doc_path = "https://www.tradingview.com/pine-script-docs/v4/"
# The maximum number of pages to crawl
max_docs = 200
# The output directory for the crawled pages
output_dir = "pine-script-docs/v4"



try:
    from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
    # Import the specific deep crawl strategy
    from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
    # Import filter components
    from crawl4ai.deep_crawling.filters import FilterChain, DomainFilter, URLPatternFilter
    # Import a scraping strategy (likely enables markdown)
    from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
except ImportError:
    print("Please install crawl4ai first: pip install crawl4ai")
    exit(1)

def sanitize_filename(url):
    """Converts a URL into a safe filename."""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace(':', '_') # Sanitize port if present
    path = parsed_url.path.strip('/')
    
    # Replace common problematic characters in path components
    safe_components = [re.sub(r'[^\w\-.]', '_', comp) for comp in path.split('/') if comp]
    
    # Handle root URL or directories ending in '/'
    if not safe_components or parsed_url.path.endswith('/'):
        safe_components.append('index')
        
    filename_base = f"{domain}_{'_'.join(safe_components)}"
    
    # Limit length and ensure .md extension
    max_len = 200 
    return filename_base[:max_len] + ".md"

async def save_docs(start_url, output_dir, max_docs=100):
    """Crawls a documentation site and saves pages as Markdown."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"Saving documents to: {output_path.resolve()}")

    start_domain = urlparse(start_url).netloc
    if not start_domain:
        print(f"Invalid start URL: {start_url}")
        return

    # --- Configure Filters --- 
    # Create a filter to stay within the specified domain
    domain_filter = DomainFilter(allowed_domains=[start_domain])
    # Create a filter to match the specific BASE path prefix, regardless of start_url
    # This ensures we crawl all docs even if starting deeper
    url_pattern_filter = URLPatternFilter(patterns=[f"{base_doc_path}*"])
    # Create a filter chain containing the domain and pattern filters
    filter_chain = FilterChain([domain_filter, url_pattern_filter])

    # --- Configure the crawl run for deep crawling --- 
    run_config = CrawlerRunConfig(
        # Pass the strategy instance to deep_crawl_strategy
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=10,               # Adjust crawl depth as needed (e.g., 10 levels deep)
            max_pages=max_docs,         # Limit total pages crawled
            include_external=False,   # Stay within the same domain (also handled by filter)
            filter_chain=filter_chain   # Pass the filter chain here
        ),
        # allowed_domains is now handled by the filter_chain in the strategy

        # Use a scraping strategy (implies markdown generation)
        scraping_strategy=LXMLWebScrapingStrategy(),

        # --- Focus on Main Content ---
        # Specify the CSS selector for the main content area
        target_elements=['main'], # Common selector, adjust if needed

        # --- Other Settings ---
        # cache_mode=CacheMode.ENABLED, # Optional: Enable caching for faster re-runs
        verbose=True                # Set to True for detailed logs during crawl
    )

    print(f"Starting deep crawl from {start_url} (max {max_docs} pages) using BFS strategy...")
    all_results = []
    
    try:
        async with AsyncWebCrawler() as crawler:
            # Assuming arun returns a list of results when deep crawl is enabled
            crawl_results = await crawler.arun(url=start_url, config=run_config)
            
            # Check if the result is a list (expected for deep crawl)
            if isinstance(crawl_results, list):
                all_results = crawl_results
            elif hasattr(crawl_results, 'url'): # If it looks like a single CrawlResult
                 print("Warning: Deep crawl returned a single result object. Processing only that.")
                 all_results = [crawl_results]
            else:
                 print(f"Warning: Unexpected result type from arun: {type(crawl_results)}. Attempting to process if possible.")
                 # Attempt to handle other potential structures if necessary
                 if hasattr(crawl_results, 'results') and isinstance(crawl_results.results, list):
                     all_results = crawl_results.results
                 else:
                      print("Error: Could not extract list of results.")
                      return

    except Exception as e:
        print(f"An error occurred during crawling: {e}")
        return

    print(f"Crawl finished. Found {len(all_results)} results. Processing...")
    saved_count = 0
    failed_count = 0

    for result in all_results:
        if result and result.success and result.markdown and result.url:
            try:
                filename = sanitize_filename(result.url)
                filepath = output_path / filename
                
                # Ensure subdirectories are created if the sanitized path includes them
                # (Note: current sanitize_filename flattens path)
                # filepath.parent.mkdir(parents=True, exist_ok=True) 

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"# Source: {result.url}\n\n")
                    f.write(result.markdown)
                saved_count += 1
                # print(f"Saved: {result.url} -> {filepath}") # Uncomment for verbose saving
            except Exception as e:
                print(f"Error saving {result.url}: {e}")
                failed_count += 1
        elif result and result.url:
            # print(f"Skipped (failed or no markdown): {result.url} (Success: {result.success})") # Uncomment for verbose skipping
            failed_count += 1
        else:
            print("Skipped an invalid or empty result object.")
            failed_count += 1

    print(f"\nFinished saving. Saved: {saved_count}, Failed/Skipped: {failed_count}")
    print(f"Documents saved in: {output_path.resolve()}")

# --- Main Execution ---
if __name__ == "__main__":
    START_URL = start_url
    OUTPUT_DIRECTORY = output_dir
    MAX_DOCUMENTS_TO_CRAWL = max_docs # Adjust as needed

    # Ensure the script runs within an async context
    asyncio.run(save_docs(START_URL, OUTPUT_DIRECTORY, MAX_DOCUMENTS_TO_CRAWL))