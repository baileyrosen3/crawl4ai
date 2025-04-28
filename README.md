# crawl4ai Usage Example

This project contains a Python script (`crawler_script.py`) demonstrating how to use the `crawl4ai` library to crawl a website and save the content of individual pages as Markdown files.

## Purpose

The script showcases using `crawl4ai` to:

- Navigate a website starting from a specific URL.
- Employ deep crawling strategies (like BFS) to discover linked pages.
- Filter crawled URLs based on domain and path patterns.
- Extract the main content from pages using a scraping strategy.
- Convert the extracted content into Markdown format.
- Save the results to a local directory.

## Setup and Usage

1.  **Prerequisites:**

    - Python 3.x
    - pip (Python package installer)

2.  **Installation:**
    Install the required library:

    ```bash
    pip install crawl4ai
    ```

3.  **Configuration:**
    Before running, you can adjust the configuration variables at the top of `crawler_script.py`:

    - `start_url`: The initial URL to begin crawling.
    - `base_doc_path`: An example variable, often used to define a base URL path for filtering crawled pages.
    - `max_docs`: The maximum number of pages to crawl.
    - `output_dir`: The directory where the crawled Markdown files will be saved.

4.  **Running the Script:**
    Execute the script from your terminal:
    ```bash
    python crawler_script.py
    ```

## Key `crawl4ai` Features Used

This script leverages several features of the `crawl4ai` library:

- **`AsyncWebCrawler`**: The core asynchronous crawler class.
- **`CrawlerRunConfig`**: Used to configure the crawling process, including strategies and filters.
- **`BFSDeepCrawlStrategy`**: Implements a Breadth-First Search strategy for recursively discovering and crawling linked pages up to a specified depth (`max_depth`) and page count (`max_pages`).
- **Filters (`FilterChain`, `DomainFilter`, `URLPatternFilter`)**: Used to restrict the crawl to specific domains and URL patterns, ensuring only relevant documentation pages are processed.
- **`LXMLWebScrapingStrategy`**: Extracts content from web pages using LXML and converts it to Markdown format.
- **`target_elements`**: Focuses the content extraction on specific HTML elements (like `<main>`) to improve the quality of the generated Markdown.

For more detailed information about `crawl4ai` and its capabilities, please refer to the [official documentation](https://docs.crawl4ai.com/).

## Output

The script will create the specified `output_dir` if it doesn't exist and save the crawled pages as `.md` files within that directory. Each file typically contains the Markdown content of a single web page, often prefixed with a comment indicating the source URL.

## `.gitignore`

A `.gitignore` file is included to prevent common Python artifacts and the specified `output_dir` from being committed to version control.
