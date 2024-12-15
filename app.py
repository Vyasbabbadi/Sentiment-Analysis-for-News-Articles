import os
import logging
import gradio as gr
import traceback
from webscrapping import WebScraper
from name_entity import EntityExtractor
from sentiment_analysis import SentimentAnalyzer
from ArticleAnalysisDatabse import ArticleAnalysisDatabase

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='article_analysis.log',
    filemode='a'
)

class ArticleAnalysisApp:
    def __init__(self, db_path=None):
        """
        Initialize the Article Analysis Application.
        
        :param db_path: Optional custom path for the database file
        """
        # Initialization
        self.web_scraper = WebScraper()
        self.entity_extractor = EntityExtractor()
        self.sentiment_analyzer = SentimentAnalyzer()
        
        # Initialization of database
        self.database = ArticleAnalysisDatabase(db_path)

    def analyze_article(self, url):
        """
        Comprehensive article analysis function for Gradio interface.
        
        :param url: URL of the article to analyze.
        :return: Formatted analysis results or error dictionary.
        """
        try:
            existing_analysis = self.database.get_article_analysis(url)
            if existing_analysis:
                logging.info(f"Found existing analysis for URL: {url}")
                return self._format_existing_analysis(existing_analysis)

            # Scrapping article
            logging.info(f"Scraping article from URL: {url}")
            article = self.web_scraper.scrape_article(url)
            
            if article is None:
                error_msg = "Failed to scrape the article. Please check the URL."
                logging.error(error_msg)
                return {"Error": error_msg}

            # Extracting named entities
            logging.info("Extracting named entities.")
            entities = self.entity_extractor.extract_entities(article['text'])
            
            # Performing sentiment analysis
            logging.info("Performing sentiment analysis.")
            sentiment = self.sentiment_analyzer.analyze_sentiment(article['text'])
            logging.info(f"Sentiment result: {sentiment}")

            # Storing analysis in database
            try:
                article_id = self.database.insert_article_analysis(
                    url, 
                    article['title'], 
                    article['text'], 
                    entities, 
                    sentiment
                )

                if article_id is None:
                    logging.error("Failed to store article analysis in the database.")
                    return {"Error": "Database insertion failed. Check logs for details."}

                logging.info(f"Article analysis stored with ID: {article_id}")

            except Exception as db_error:
                logging.error(f"Database insertion error: {db_error}")
                return {"Error": f"Database error: {str(db_error)}"}

            return self._format_analysis_result(article, entities, sentiment)

        except Exception as e:
            logging.error(f"Comprehensive analysis error: {e}")
            traceback.print_exc()
            return {"Error": f"An unexpected error occurred: {str(e)}"}

    def _format_existing_analysis(self, existing_analysis):
        """
        Format existing analysis from database.
        
        :param existing_analysis: Dictionary of existing analysis
        :return: Formatted analysis result
        """
        entities_text = "Persons and Organizations:\n"
        if existing_analysis['entities']:
            for entity in existing_analysis['entities']:
                entities_text += f"- {entity['text']} (Type: {entity['label']})\n"
        else:
            entities_text += "No named entities found."

        return {
            'Title': existing_analysis['title'],
            'Content': existing_analysis['content'][:1000] + '...' if len(existing_analysis['content']) > 1000 else existing_analysis['content'],
            'Entities': entities_text,
            'Sentiment': f"Overall Sentiment: {existing_analysis['sentiment']}"
        }

    def _format_analysis_result(self, article, entities, sentiment):
        """
        Format analysis result for display.
        
        :param article: Scraped article dictionary
        :param entities: List of extracted entities
        :param sentiment: Sentiment analysis result
        :return: Formatted analysis dictionary
        """
        entities_text = "Persons and Organizations:\n"
        if entities:
            for entity in entities:
                entities_text += f"- {entity['text']} (Type: {entity['label']})\n"
        else:
            entities_text += "No named entities found."

        return {
            'Title': article['title'],
            'Content': article['text'][:1000] + '...' if len(article['text']) > 1000 else article['text'],
            'Entities': entities_text,
            'Sentiment': f"Overall Sentiment: {sentiment}"
        }

def create_gradio_interface(app):
    """
    Create and return the Gradio interface.
    
    :param app: ArticleAnalysisApp instance
    :return: Gradio interface
    """
    def process_url(url):
        """
        Wrapper function to handle Gradio's multiple output requirement.
        """
        result = app.analyze_article(url)
        
        if isinstance(result, dict) and 'Error' in result:
            return result['Error'], '', '', ''
        
        # Return formatted results
        return (
            result.get('Title', ''),
            result.get('Content', ''),
            result.get('Entities', ''),
            result.get('Sentiment', '')
        )

    # Creating Gradio interface with multiple outputs
    iface = gr.Interface(
        fn=process_url,
        inputs=gr.Textbox(label="Enter Article URL", placeholder="https://example.com/article"),
        outputs=[
            gr.Textbox(label="Article Title"),
            gr.Textbox(label="Article Content"),
            gr.Textbox(label="Named Entities"),
            gr.Textbox(label="Sentiment Analysis")
        ],
        title="Sentiment Analysis for News articles",
        description="Scrape and analyze web articles with entity extraction and sentiment analysis",
        theme="default",
        allow_flagging="never"
    )

    return iface

def main():
    app = ArticleAnalysisApp()  
    iface = create_gradio_interface(app)
    iface.launch(share=False)

if __name__ == "__main__":
    main()