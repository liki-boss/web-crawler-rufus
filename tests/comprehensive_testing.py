import pytest
import os
import responses
import json
from src.scraper import RufusClient
from bs4 import BeautifulSoup

@pytest.fixture
def client():
    """Fixture to create a RufusClient instance for tests"""
    return RufusClient(api_key="test_api_key")

@pytest.fixture
def sample_html():
    """Fixture providing sample HTML content"""
    return """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Welcome to Test Site</h1>
            <p>This is a paragraph about data analytics and insights.</p>
            <div>Some content about pricing and products.</div>
            <a href="/about">About</a>
            <a href="https://lifesight.io/">External Link</a>
        </body>
    </html>
    """

class TestRufusClient:
    """Test suite for RufusClient"""

    def test_initialization(self, client):
        """Test proper client initialization"""
        assert client.api_key == "test_api_key"
        assert isinstance(client.visited_urls, set)
        assert client.base_url is None

    def test_url_normalization(self, client): # Check
        client.base_url = "https://lifesight.io"
        assert client.normalize_url("/page") == "https://lifesight.io/page"
        assert client.normalize_url("https://google.com") == "https://google.com"
        assert client.normalize_url("") is None

    def test_url_validation(self, client):
        """Test URL validation"""
        assert client.is_valid_url("https://lifesight.io/")
        assert not client.is_valid_url("invalid-url")
        assert not client.is_valid_url("")

    def test_domain_checking(self, client):
        """Test same domain checking"""
        client.base_url = "https://lifesight.io/"
        assert client.is_same_domain("https://lifesight.io//page")
        assert not client.is_same_domain("https://google.com")

    @responses.activate
    def test_basic_scraping(self, client, sample_html, mocker):
        """Test basic scraping functionality"""
        # Mock Selenium WebDriver
        mock_driver = mocker.Mock()
        mock_driver.page_source = sample_html
        mock_driver.current_url = "https://lifesight.io"
        
        # Mock the webdriver creation
        mocker.patch('selenium.webdriver.Chrome', return_value=mock_driver)
        
        results = client.scrape("https://lifesight.io")
        
        assert isinstance(results, list)
        assert len(results) > 0
        assert 'url' in results[0]
        assert 'title' in results[0]
        assert 'Test Page' in results[0]['title']

    def test_relevance_detection(self, client):
        """Test content relevance detection"""
        text = "This is content about data analytics and visualization"
        prompt = "data analytics"
        
        assert client.is_relevant_to_prompt(text, prompt)
        assert not client.is_relevant_to_prompt(text, "unrelated topic")

    def test_content_extraction(self, client, sample_html):
        """Test content extraction from HTML"""
        BeautifulSoup(sample_html, 'lxml')
        data = client.extract_data(sample_html, "https://lifesight.io")
        
        assert isinstance(data, list)
        assert len(data) > 0
        assert 'content' in data[0]
        assert any('data analytics' in str(content).lower() 
                  for content in data[0]['content'])

    def test_results_saving(self, client, tmp_path):
        """Test saving results to file"""
        results = [{
            'url': 'https://test.com',
            'title': 'Test Page',
            'content': ['Sample content']
        }]
        
        output_file = tmp_path / "docs/basic_results.json"
        
        client.save_results(results, str(output_file))
        
        # Check if file exists and has content
        assert os.path.exists(output_file)
        with open(output_file, 'r') as f:
            saved_results = json.load(f)
            assert saved_results == results

if __name__ == "__main__":
    pytest.main([__file__])