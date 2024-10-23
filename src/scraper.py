import json
import os
import logging
import time
import re
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional

class RufusClient:
    def __init__(self, api_key: str):
        """Initialize Rufus client with API key and configuration"""
        self.api_key = api_key
        self.visited_urls = set() # Keep track of visited URLs
        self.base_url = None # Base URL for domain checking
        self.setup_logging()
        self.setup_webdriver()
        
        try:
            nltk.download('punkt')
            nltk.download('punkt_tab')
            nltk.download('stopwords')
        except:
            pass
        
        # Set stopwords for filtering common words
        self.stop_words = set(stopwords.words('english'))
        self.vectorizer = TfidfVectorizer(stop_words='english')
        
    def setup_logging(self):
        """Configure logging for the client"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def setup_webdriver(self):
        """Initialize Selenium webdriver with appropriate options"""
        self.options = Options()
        self.options.add_argument('--headless') # No browser window
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])

    def get_driver(self):
        """Create and return a new webdriver instance"""
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.options
        )

    def normalize_url(self, url: str) -> Optional[str]:
        """Normalize URL to ensure proper formatting"""
        if not url:
            return None
        try:
            # Append base_url if it's a relative link
            if not url.startswith(('http://', 'https://')):
                return urljoin(self.base_url, url)
            return url
        except Exception as e:
            self.logger.error(f"Error normalizing URL {url}: {str(e)}")
            return None

    def is_valid_url(self, url: str) -> bool:
        """Validate URL format and structure"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def is_same_domain(self, url: str) -> bool:
        """Check if URL belongs to the same domain as base_url"""
        try:
            return urlparse(url).netloc == urlparse(self.base_url).netloc
        except Exception:
            return False

    def is_relevant_to_prompt(self, text: str, prompt: str, threshold: float = 0.1) -> bool:
        """
        Determine if a piece of text is relevant to a given prompt using TF-IDF and keyword matching.
        
        Args:
            text: The content to analyze.
            prompt: The reference prompt for relevance comparison.
            threshold: The minimum cosine similarity score for relevance.
            
        Returns:
            True if the text is relevant to the prompt, otherwise False.
        """
        if not text or not prompt:
            return False

        # Preprocess both text and prompt
        text = self.preprocess_text(text)
        prompt = self.preprocess_text(prompt)

        if not text or not prompt:
            return False

        # Method 1: TF-IDF Similarity
        try:
            tfidf_matrix = self.vectorizer.fit_transform([prompt, text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            if similarity >= threshold:
                return True
        except:
            pass

        # Method 2: Keyword matching
        prompt_keywords = self.extract_keywords(prompt)
        text_keywords = self.extract_keywords(text)
        
        keyword_overlap = len(prompt_keywords.intersection(text_keywords))
        if keyword_overlap > 0:
            return True

        # Method 3: Check for partial matches between keywords
        for p_word in prompt_keywords:
            for t_word in text_keywords:
                if (len(p_word) > 3 and p_word in t_word) or \
                   (len(t_word) > 3 and t_word in p_word):
                    return True

        return False

    def preprocess_text(self, text: str) -> str:
        """
        Clean up text by converting to lowercase, removing special characters and extra spaces.
        """
        text = text.lower()
        
        text = re.sub(r'[^\w\s]', ' ', text)    # Remove whitespace and special characters
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def extract_keywords(self, text: str) -> set:
        """
        Extract keywords from a given text, filtering out stopwords and short words.
        """
        tokens = word_tokenize(text.lower())
        
        keywords = {word for word in tokens 
                   if word not in self.stop_words 
                   and len(word) > 2
                   and not word.isnumeric()}
        
        return keywords # After removing stop words and short words

    def process_results(self, results: List[Dict], prompt: Optional[str] = None) -> List[Dict]:
        """
        Filter the scraped results based on relevance to the prompt.
        
        Args:
            results: List of scraped content.
            prompt: Prompt to filter relevant content.
            
        Returns:
            A list of processed results, including only relevant content.
        """
        if not prompt:
            return results

        processed_results = []
        for result in results:
            processed_content = {
                'url': result['url'],
                'title': result['title'],
                'content': [],
                'relevance_score': 0.0
            }

            relevant_content_count = 0
            total_content_score = 0.0 
            for content in result['content']:
                if self.is_relevant_to_prompt(content, prompt):
                    processed_content['content'].append(content)
                    relevant_content_count += 1
                    total_content_score += 1.0

            if relevant_content_count > 0:
                processed_content['relevance_score'] = total_content_score / len(result['content'])
                processed_results.append(processed_content)

        return processed_results
    
    def extract_data(self, html, current_url, prompt=None, depth=1):
        """
            Extract relevant data (text, headings, lists) from HTML content and recursively follow links.
        
        Args:
            html: Raw HTML content to parse.
            current_url: The URL of the page.
            prompt: Reference prompt for filtering.
            depth: Recursion depth for following links.
            
        Returns:
            List of extracted data from the page and its linked pages.
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            data = []

            # Extract page title
            title = soup.title.string if soup.title else ''

            # Define which tags to search for content (paragraphs, headings, etc.)
            content_elements = {
                'text': ['p', 'div', 'section', 'article'],
                'headings': ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
                'lists': ['ul', 'ol'],
                'tables': ['table']
            }

            page_content = []

            # Extract content from each element type
            for category, tags in content_elements.items():
                for tag in tags:
                    elements = soup.find_all(tag)
                    for element in elements:
                        text = element.get_text(strip=True)
                        if text and len(text) > 20:  # Skip very short content
                            page_content.append(text)

            # Store the extracted content
            result = {
                'url': current_url,
                'title': title,
                'content': page_content
            }
            
            data.append(result)

            # If depth > 0, find and process links
            if depth > 0:
                links = soup.find_all('a', href=True)
                for link in links:
                    next_url = self.normalize_url(link['href'])
                    if next_url and self.is_same_domain(next_url):
                        # Recursively scrape linked pages
                        nested_results = self.scrape(next_url, prompt, depth - 1)
                        data.extend(nested_results)

            return data

        except Exception as e:
            print(f"Error extracting data: {str(e)}")
            return []

    def scrape(self, url, prompt=None, depth=1):
        """
        Scrape the provided URL, extract content, and follow links up to the specified depth.
        
        Args:
            url: The URL to scrape.
            prompt: Reference prompt for filtering.
            depth: Recursion depth for following links.
            
        Returns:
            A list of scraped data from the page and any linked pages.
        """
        # Set base_url if not already set
        if not self.base_url:
            self.base_url = url

        # Normalize and validate URL
        url = self.normalize_url(url)
        if not url or not self.is_valid_url(url):
            print(f"Skipping invalid URL: {url}")
            return []

        # Check if URL has already been visited or max_depth has been reached
        if url in self.visited_urls or depth < 0:
            return []

        self.visited_urls.add(url)
        print(f"Scraping URL: {url}")

        try:
            # Setup and use Selenium WebDriver
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), 
                                    options=self.options)
            driver.set_page_load_timeout(20)
            driver.get(url)
            
            # Wait for dynamic content to load
            time.sleep(3)
            
            # Get the current page's HTML source and the final URL (after redirects if any)
            html = driver.page_source
            current_url = driver.current_url  # Get the final URL after any redirects
            
            # Close the browser after retreival
            driver.quit()

            # Extract relevant data from the page using helper function `extract_data`
            results = self.extract_data(html, current_url, prompt, depth)

            # If a prompt is provided, filter or process results based on it
            if prompt:
                results = self.process_results(results, prompt)

            return results

        except Exception as e:
            print(f"Error accessing {url}: {str(e)}")
            return []

    def save_results(self, results: List[Dict], output_file: str):
        """
        Save the scraped results to a file
        
        Args:
            results: List of scraped content
            output_file: Path to save the results
        """
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False) # Save as pretty-printed JSON
        
        print(f"Results saved to {output_file}")

    def clear_cache(self):
        """Clear the visited URLs cache and TF-IDF vectorizer"""
        self.visited_urls.clear()   # Clear list of visited URLs
        self.base_url = None    # Reset the base URL
        # Reset the TF-IDF vectorizer for filtering content by prompt
        self.vectorizer = TfidfVectorizer(stop_words='english')