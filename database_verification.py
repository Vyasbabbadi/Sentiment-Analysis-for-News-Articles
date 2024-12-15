import sqlite3
import logging

logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def verify_database(db_name='article_analysis.db'):
    """
    Comprehensive database verification script
    """
    try:
        # Connection to the database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Check articles table
        cursor.execute("SELECT * FROM articles")
        articles = cursor.fetchall()
        logging.info(f"Total articles: {len(articles)}")

        if articles:
            # Print details of first article
            for article in articles:
                logging.info(f"Article Details: {article}")
        else:
            logging.warning("No articles found in the database")

        # Check entities table
        cursor.execute("SELECT * FROM entities")
        entities = cursor.fetchall()
        logging.info(f"Total entities: {len(entities)}")

        # Check sentiments table
        cursor.execute("SELECT * FROM sentiments")
        sentiments = cursor.fetchall()
        logging.info(f"Total sentiments: {len(sentiments)}")

    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

#manually inserting data to check wheather the connection is established and the data is being stored in the database
def manual_insertion_test(db_name='article_analysis.db'):
    """
    Manually insert a test record to verify insertion works
    """
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Insert test article
        cursor.execute('''
            INSERT INTO articles (url, title, content)
            VALUES (?, ?, ?)
        ''', ('https://test.com', 'Test Title', 'Test Content'))
        
        # Get the last inserted ID
        article_id = cursor.lastrowid

        # Insert test entity
        cursor.execute('''
            INSERT INTO entities (article_id, entity_text, entity_type)
            VALUES (?, ?, ?)
        ''', (article_id, 'Test Entity', 'PERSON'))

        # Insert test sentiment
        cursor.execute('''
            INSERT INTO sentiments (article_id, sentiment)
            VALUES (?, ?)
        ''', (article_id, 'positive'))

        # Commit changes
        conn.commit()
        logging.info("Manual test insertion successful")

    except sqlite3.Error as e:
        logging.error(f"Manual insertion error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Verifying database...")
    verify_database()
    
    print("\nPerforming manual insertion test...")
    manual_insertion_test()
    
    print("\nVerifying database after insertion...")
    verify_database()