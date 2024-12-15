import re
import string

class SentimentAnalyzer:
    def __init__(self):
        """
        Initialize the Custom Sentiment Analyzer with predefined lexicons
        """
        # Lists of sentiment positive and negative words
        self.positive_words = {
            'good', 'great', 'excellent', 'awesome', 'wonderful', 'fantastic', 
            'amazing', 'perfect', 'brilliant', 'outstanding', 'superb', 'nice', 
            'love', 'happy', 'joy', 'delightful', 'pleasant', 'beautiful', 
            'best', 'success', 'win', 'positive', 'hope', 'bright', 'excellent',
            'fantastic', 'terrific', 'incredible', 'delighted', 'glad', 'fortunate'
        }

        self.negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'worst', 'poor', 'disappointing', 
            'dreadful', 'unpleasant', 'negative', 'fail', 'problem', 'issue', 'sad', 
            'unhappy', 'trouble', 'difficult', 'worse', 'worse', 'hate', 'angry', 
            'frustrating', 'disaster', 'catastrophe', 'loss', 'pain', 'challenge', 
            'struggle', 'difficult', 'miserable', 'unfortunate'
        }

        # Intensity modifiers
        self.intensity_multipliers = {
            'very': 2.0, 'extremely': 2.5, 'incredibly': 2.5, 
            'absolutely': 2.0, 'totally': 2.0, 'completely': 2.0,
            'highly': 1.5, 'quite': 1.5, 'really': 1.5,
            'somewhat': 0.5, 'slightly': 0.5
        }

        # Negation words that can invert sentiment
        self.negation_words = {
            'not', 'no', 'never', 'neither', 'hardly', 'scarcely', 
            'nothing', 'nobody', 'none', 'without'
        }

    def preprocess_text(self, text):
        """
        Preprocess the input text
        
        :param text: Input text to preprocess
        :return: Cleaned and tokenized text
        """
        text = text.lower()
        
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Tokenization
        return text.split()

    def analyze_sentiment(self, text, max_length=512):
        """
        Analyze sentiment using a custom rule-based approach
        
        :param text: Input text to analyze
        :param max_length: Maximum text length to process
        :return: Sentiment label (positive/negative/neutral)
        """
        try:
            text = text[:max_length]
            words = self.preprocess_text(text)
            
            # Sentiment tracking variables
            sentiment_score = 0
            negation_active = False
            
            # Analyze each word
            for i, word in enumerate(words):
                # Check for intensity multipliers
                if word in self.intensity_multipliers:
                    # Look ahead to see if next word is sentiment-bearing
                    if i + 1 < len(words):
                        multiplier = self.intensity_multipliers[word]
                        next_word = words[i+1]
                        if next_word in self.positive_words:
                            sentiment_score += 1 * multiplier
                        elif next_word in self.negative_words:
                            sentiment_score -= 1 * multiplier
                
                # Check for negation
                if word in self.negation_words:
                    negation_active = not negation_active
                
                # Check positive words
                if word in self.positive_words:
                    sentiment_score += 1 if not negation_active else -1
                
                # Check negative words
                if word in self.negative_words:
                    sentiment_score -= 1 if not negation_active else 1
                
                # Reset negation after each clause or sentiment word
                if word in {'.', ',', ';', 'and', 'but', 'or'}:
                    negation_active = False
            
            # Determine final sentiment
            if sentiment_score > 1:
                return 'positive'
            elif sentiment_score < -1:
                return 'negative'
            else:
                return 'neutral'
        
        except Exception as e:
            print(f"Custom sentiment analysis error: {e}")
            return 'neutral'

