import sqlite3
import logging
import os
from typing import List, Dict, Optional

class ArticleAnalysisDatabase:
    def __init__(self, db_path=None):
        """
        Initialize the database connection and create tables if they don't exist.
        
        :param db_path: Optional custom path for the database file
        """
        if db_path is None:
            db_path = os.path.join(os.getcwd(), 'article_analysis.db')
        
        self.db_path = db_path
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='database.log',  # Log to a file for persistent tracking
            filemode='a'
        )
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Create tables
        self.create_tables()

    def _get_connection(self):
        """
        Create and return a new database connection.
        
        :return: SQLite database connection
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Allow accessing columns by name
            return conn
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {e}")
            print(f"Database connection error: {e}")
            return None

    def create_tables(self):
        """
        Create necessary tables in the database if they don't exist.
        """
        try:
            conn = self._get_connection()
            if not conn:
                logging.error("Failed to establish database connection for table creation")
                return False

            cursor = conn.cursor()

            # Create articles table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                content TEXT,
                analysis_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')

            # Create entities table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER,
                entity_text TEXT,
                entity_type TEXT,
                FOREIGN KEY (article_id) REFERENCES articles (id)
            )''')

            # Create sentiment table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS sentiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER,
                sentiment TEXT,
                FOREIGN KEY (article_id) REFERENCES articles (id)
            )''')

            # Commit changes and close connection
            conn.commit()
            logging.info(f"Database tables created successfully at {self.db_path}")
            print(f"Database tables created successfully at {self.db_path}")
            return True

        except sqlite3.Error as e:
            logging.error(f"Database setup error: {e}")
            print(f"Database setup error: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def insert_article_analysis(
        self, 
        url: str, 
        title: str, 
        content: str, 
        entities: List[Dict[str, str]], 
        sentiment: str
    ) -> Optional[int]:
        """
        Insert article analysis into the database.
        
        :param url: Article URL
        :param title: Article title
        :param content: Article content
        :param entities: List of named entities
        :param sentiment: Sentiment analysis result
        :return: Article ID or None if insertion fails
        """
        conn = None
        try:
            # Establish a connection
            conn = self._get_connection()
            if not conn:
                logging.error("Failed to establish database connection")
                return None

            cursor = conn.cursor()

            # Detailed logging of input data
            logging.info(f"Attempting to insert article: {url}")
            logging.info(f"Title length: {len(title)}")
            logging.info(f"Content length: {len(content)}")
            logging.info(f"Entities count: {len(entities) if entities else 0}")
            logging.info(f"Sentiment: {sentiment}")

            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO articles (url, title, content)
                    VALUES (?, ?, ?)
                ''', (url, title, content))
                article_id = cursor.lastrowid
                logging.info(f"Article inserted with ID: {article_id}")

                # Clear existing entities and sentiments for this article to avoid duplicates
                cursor.execute('DELETE FROM entities WHERE article_id = ?', (article_id,))
                cursor.execute('DELETE FROM sentiments WHERE article_id = ?', (article_id,))

                # Insert entities
                if entities:
                    entity_data = [
                        (article_id, entity.get('text', ''), entity.get('label', 'Unknown'))
                        for entity in entities
                    ]
                    cursor.executemany('''
                        INSERT INTO entities (article_id, entity_text, entity_type)
                        VALUES (?, ?, ?)
                    ''', entity_data)
                    logging.info(f"Inserted {len(entities)} entities")

                # Insert sentiment
                cursor.execute('''
                    INSERT INTO sentiments (article_id, sentiment)
                    VALUES (?, ?)
                ''', (article_id, sentiment))
                logging.info("Sentiment inserted")

                # Commit changes
                conn.commit()
                return article_id

            except sqlite3.Error as insertion_error:
                logging.error(f"Insertion error: {insertion_error}")
                print(f"Insertion error: {insertion_error}")
                # Rollback in case of error
                conn.rollback()
                return None

        except Exception as e:
            logging.error(f"Comprehensive database insertion error: {e}")
            print(f"Comprehensive database insertion error: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            if conn:
                conn.close()

    def get_article_analysis(self, url: str) -> Optional[Dict]:
        """
        Retrieve article analysis by URL.
        
        :param url: Article URL
        :return: Dictionary of article analysis or None
        """
        conn = None
        try:
            conn = self._get_connection()
            if not conn:
                logging.error("Failed to establish database connection")
                return None

            cursor = conn.cursor()

            # Fetching article details
            cursor.execute('''
                SELECT id, url, title, content, analysis_timestamp 
                FROM articles 
                WHERE url = ?
            ''', (url,))
            article = cursor.fetchone()

            if not article:
                return None

            # Fetching entities
            cursor.execute('''
                SELECT entity_text, entity_type 
                FROM entities 
                WHERE article_id = ?
            ''', (article['id'],))
            entities = cursor.fetchall()

            # Fetching sentiment
            cursor.execute('''
                SELECT sentiment 
                FROM sentiments 
                WHERE article_id = ?
            ''', (article['id'],))
            sentiment = cursor.fetchone()

            return {
                'id': article['id'],
                'url': article['url'],
                'title': article['title'],
                'content': article['content'],
                'timestamp': article['analysis_timestamp'],
                'entities': [{'text': e['entity_text'], 'label': e['entity_type']} for e in entities],
                'sentiment': sentiment['sentiment'] if sentiment else None
            }

        except sqlite3.Error as e:
            logging.error(f"Error retrieving article analysis: {e}")
            return None
        finally:
            if conn:
                conn.close()

if __name__ == "__main__":
    # Test database creation and connection
    database = ArticleAnalysisDatabase()
    print(f"Database initialized at {database.db_path}")