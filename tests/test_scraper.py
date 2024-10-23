from src.scraper import RufusClient

def test_basic_scraping():
    """
    Basic test to verify scraper functionality and content relevance
    """
    # Initialize client
    client = RufusClient(api_key="your_api_key")
    
    # Test URL (using a simple, stable website)
    url = "https://lifesight.io/"  # Replace with your target website
    
    # Test Case 1: Basic scraping without prompt
    print("\nTest Case 1: Basic Scraping")
    print("-" * 50)
    try:
        results = client.scrape(url, depth=2)  # depth=0 for just the main page
        
        # Check if we got any results
        if results and len(results) > 0:
            print(f"✓ Successfully retrieved {len(results)} pages")
            
            # Print first result details
            first_result = results[0]
            print(f"\nFirst page title: {first_result.get('title', 'No title')}")
            print(f"URL: {first_result.get('url', 'No URL')}")
            print("\nSample content snippets:")
            for i, content in enumerate(first_result.get('content', [])[:3]):
                print(f"{i+1}. {content[:100]}...")
        else:
            print("✗ No results returned")
            
    except Exception as e:
        print(f"✗ Error in basic scraping: {str(e)}")

    # Test Case 2: Scraping with specific prompt
    print("\nTest Case 2: Prompted Scraping")
    print("-" * 50)
    try:
        prompt = "Boosting Customer Loyalty"
        prompted_results = client.scrape(url, prompt=prompt, depth=2)
        
        if prompted_results and len(prompted_results) > 0:
            print(f"✓ Successfully retrieved {len(prompted_results)} relevant pages")
            
            # Print relevant content
            first_result = prompted_results[0]
            print(f"\nRelevant content for prompt '{prompt}':")
            for i, content in enumerate(first_result.get('content', [])[:3]):
                print(f"{i+1}. {content[:100]}...")
                
            # Save results for inspection
            output_file = "docs\prompt_results.json"
            client.save_results(prompted_results, output_file)
            print(f"\nDetailed results saved to {output_file}")
        else:
            print(f"✗ No relevant content found for prompt: {prompt}")
            
    except Exception as e:
        print(f"✗ Error in prompted scraping: {str(e)}")
    
    finally:
        client.clear_cache()

if __name__ == "__main__":
    test_basic_scraping()