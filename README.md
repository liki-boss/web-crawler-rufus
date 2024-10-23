# Rufus Web Scraper 🕷️

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/selenium-%5E4.0.0-green)](https://www.selenium.dev/)

An intelligent web scraping library that combines the power of Selenium with smart content extraction capabilities. Rufus is designed to handle modern, JavaScript-heavy websites while providing relevant, structured data based on your requirements.

## 🚀 Features

- **Modern Website Support**: Handles JavaScript-rendered content seamlessly
- **Intelligent Content Extraction**: Uses TF-IDF to identify and extract relevant content
- **Domain-Aware Crawling**: Respects domain boundaries and prevents cycles
- **Structured Output**: Returns well-organized, categorized content
- **Configurable Depth**: Control how deep you want to crawl
- **Respectful Scraping**: Built-in rate limiting and robots.txt compliance

## 🛠️ Installation

To get started, clone the repository and install the required dependencies:

```bash
git clone https://github.com/yourusername/rufus.git
cd rufus
pip install -r requirements.txt
```
Ensure you have ChromeDriver installed for Selenium to work with Chrome.

## Usage

### 📖 Basic Scraping

You can use Rufus to scrape both static and dynamic websites with ease. Here's how to start:

```python
from rufus import RufusClient

# Create a new Rufus instance
scraper = RufusClient()

# Scrape a website
data = scraper.scrape('https://example.com')

# Print the extracted content
print(data)
```

### 🔧 Advanced Scraping

For more advanced use cases, such as handling depth control or extracting content based on a prompt, you can customize Rufus as follows:

```python
# Scrape with depth control and custom prompts
data = scraper.scrape('https://example.com', max_depth=3, prompt="Extract only articles and headings")
```

## 🏗️ Architecture

Rufus is built on three main components:

1. **URL Manager**: Handles URL normalization, validation, and cycle detection
2. **Selenium WebDriver**: Manages page rendering and JavaScript execution
3. **Content Extractor**: Processes and filters content using TF-IDF analysis

### Component Diagram
```mermaid
graph TB
    subgraph "Rufus Web Scraper Architecture"
    A[Client Application] --> B[RufusClient]
    
    subgraph "Core Components"
        B --> C[URL Manager]
        B --> D[Selenium WebDriver]
        B --> E[Content Extractor]
        
        C --> C1[URL Normalization]
        C --> C2[Domain Validation]
        C --> C3[Cycle Detection]
        
        D --> D1[Chrome Options]
        D --> D2[Page Rendering]
        D --> D3[JavaScript Execution]
        
        E --> E1[BeautifulSoup Parser]
        E --> E2[TF-IDF Analyzer]
        E --> E3[Content Categorization]
    end
    
    subgraph "Data Processing"
        E1 --> F1[HTML Parsing]
        E2 --> F2[Relevance Scoring]
        E3 --> F3[Content Structure]
    end
    
    subgraph "Output"
        F1 --> G[Structured Data]
        F2 --> G
        F3 --> G
    end
    end
  ```

## Key Components Description

1. **URL Manager**
   - Normalizes URLs to ensure consistent format.
   - Validates URLs for security and accessibility.
   - Prevents crawling cycles through URL tracking.
   - Manages domain restrictions and boundaries.

2. **Selenium WebDriver**
   - Handles JavaScript-rendered content.
   - Manages browser automation.
   - Controls page load timing.
   - Handles dynamic content loading.
   - Manages browser configurations and options.

3. **Content Extractor**
   - Parses HTML content using BeautifulSoup.
   - Implements TF-IDF analysis for content relevance.
   - Categorizes content by type (text, tables, lists).
   - Structures output data in a consistent format.
   - Filters content based on relevance scores.

## Data Flow

1. The client provides a URL and an optional prompt.
2. The URL Manager processes and validates the URL.
3. The Selenium WebDriver fetches and renders the page.
4. The Content Extractor processes the HTML content.
5. TF-IDF analysis determines content relevance.
6. Structured data is returned to the client.

## Technical Specifications

- Built with Python 3.7+
- Uses Selenium for browser automation.
- Implements BeautifulSoup4 for HTML parsing.
- Utilizes scikit-learn for TF-IDF analysis.
- Supports headless browser operation.

## ⚙️ Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | str | None | Your API key for authentication |
| `depth` | int | 1 | Crawling depth from start URL |
| `relevance_threshold` | float | 0.2 | Minimum relevance score for content |
| `restrict_domain` | bool | True | Stay within starting domain |
| `timeout` | int | 20 | Page load timeout in seconds |
| `headless` | bool | True | Run browser in headless mode |
| `max_retries` | int | 3 | Maximum retry attempts for failed requests |
| `delay` | float | 0.5 | Delay between requests in seconds |
| `user_agent` | str | None | Custom user agent string |
| `proxy` | dict | None | Proxy configuration settings |


## 📝 License

### License Badge

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
