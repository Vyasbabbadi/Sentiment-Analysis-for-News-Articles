import requests
from bs4 import BeautifulSoup

class WebScraper:
    def __init__(self, headers=None):
        """
        Initialize WebScraper with optional custom headers
        
        :param headers: Optional dictionary of HTTP headers
        """
        if headers is None:
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br'
            }
        else:
            self.headers = headers

    def scrape_article(self, url):
        """
        Scrape an article from a given URL
        
        :param url: URL of the news article
        :return: Dictionary containing article title and text, or None if scraping fails
        """
        try:
            # Send request
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title and content
            title = self._extract_title(soup)
            content = self._extract_content(soup)

            return {
                'title': title,
                'text': content
            }
        except Exception as e:
            print(f"Comprehensive scraping error for {url}: {e}")
            return None

    def _extract_title(self, soup):
        """
        Extract title with multiple fallback methods
        
        :param soup: BeautifulSoup parsed HTML
        :return: Extracted title or 'No Title Found'
        """
        title_options = [
            soup.find('meta', property='og:title'),
            soup.find('title'),
            soup.find('h1')
        ]
        
        for title_tag in title_options:
            if title_tag:
                return title_tag.get('content', title_tag.text).strip()
        
        return 'No Title Found'

    def _extract_content(self, soup):
        """
        Advanced content extraction
        
        :param soup: BeautifulSoup parsed HTML
        :return: Extracted article content or 'No Content Found'
        """
        # Content extraction strategies
        content_selectors = [
            'article', 
            'div.article-body', 
            'div.content', 
            'div.main-content',
            'body'
        ]
        
        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div:
                # Extract text, remove extra whitespaces
                paragraphs = content_div.find_all(['p', 'div'])
                content = ' '.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                
                if content:
                    return content
        
        return 'No Content Found'