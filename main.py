import sys
from webscrapping import WebScraper
from name_entity import EntityExtractor
from sentiment_analysis import SentimentAnalyzer

def analyze_article(url):
    """
    Perform comprehensive analysis of an article from a given URL
    
    :param url: URL of the article to analyze
    """
    web_scraper = WebScraper()
    entity_extractor = EntityExtractor()
    sentiment_analyzer = SentimentAnalyzer()

    # Scrape article
    article = web_scraper.scrape_article(url)
    
    if article is None:
        print("Failed to scrape the article. Please check the URL and try again.")
        return

    # Extract title
    print("\n--- Article Title ---")
    print(article['title'])

    # Display scraped content
    print("\n--- Scraped Article Content ---")
    print(article['text'][:1000] + "..." if len(article['text']) > 1000 else article['text'])

    # Extract named entities
    print("\n--- Named Entities ---")
    entities = entity_extractor.extract_entities(article['text'])
    if entities:
        print("Persons and Organizations:")
        for entity in entities:
            print(f"- {entity['text']} (Type: {entity['label']})")
    else:
        print("No named entities found.")

    # Perform sentiment analysis
    print("\n--- Sentiment Analysis ---")
    sentiment = sentiment_analyzer.analyze_sentiment(article['text'])
    print(f"Overall Sentiment: {sentiment}")

def main():
    # Check if URL is provided
    if len(sys.argv) < 2:
        print("Usage: python main.py <article_url>")
        sys.exit(1)

    # Get URL from command line argument
    url = sys.argv[1]
    analyze_article(url)

if __name__ == "__main__":
    main()