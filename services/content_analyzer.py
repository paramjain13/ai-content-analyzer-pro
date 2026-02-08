import re
from collections import Counter
from textblob import TextBlob
import spacy
from langdetect import detect, detect_langs, LangDetectException

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy language model...")
    import os
    os.system("python3 -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

class ContentAnalyzer:
    def __init__(self):
        # Built-in stopwords list
        self.stop_words = {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're",
            "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he',
            'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's",
            'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
            'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
            'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
            'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
            'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
            'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
            'there', 'when', 'where', 'why', 'how', 'all', 'both', 'each', 'few', 'more', 'most',
            'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
            'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've",
            'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn',
            "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't",
            'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't",
            'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't",
            'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
        }
        
        # Topic keywords for classification
        self.topic_keywords = {
            "Technology": [
                "software", "hardware", "computer", "internet", "technology", "digital",
                "app", "application", "data", "algorithm", "ai", "artificial", "intelligence",
                "machine", "learning", "coding", "programming", "developer", "tech", "startup",
                "cloud", "cybersecurity", "blockchain", "crypto", "bitcoin", "database",
                "api", "code", "python", "javascript", "mobile", "android", "ios"
            ],
            "Business": [
                "business", "company", "market", "economy", "finance", "investment",
                "stock", "revenue", "profit", "sales", "management", "strategy", "corporate",
                "entrepreneur", "ceo", "executive", "trading", "investor", "capital",
                "merger", "acquisition", "startup", "venture", "enterprise", "commerce"
            ],
            "Health": [
                "health", "medical", "doctor", "patient", "disease", "treatment", "hospital",
                "medicine", "drug", "therapy", "diagnosis", "symptom", "clinic", "healthcare",
                "wellness", "fitness", "nutrition", "diet", "exercise", "mental", "pharmaceutical",
                "vaccine", "virus", "pandemic", "covid", "cancer", "surgery"
            ],
            "Science": [
                "science", "research", "study", "scientist", "experiment", "discovery",
                "theory", "hypothesis", "laboratory", "chemistry", "physics", "biology",
                "astronomy", "climate", "environment", "nature", "evolution", "genetic",
                "molecule", "atom", "particle", "quantum", "nasa", "space"
            ],
            "Sports": [
                "sport", "game", "team", "player", "coach", "championship", "tournament",
                "soccer", "football", "basketball", "baseball", "tennis", "golf", "olympic",
                "athlete", "competition", "match", "score", "win", "victory", "league",
                "fitness", "training", "nba", "nfl", "fifa"
            ],
            "Politics": [
                "politics", "government", "election", "president", "minister", "congress",
                "parliament", "senate", "vote", "policy", "law", "legislation", "democrat",
                "republican", "campaign", "political", "administration", "official",
                "legislation", "regulation", "democracy", "diplomatic"
            ],
            "Entertainment": [
                "movie", "film", "music", "actor", "actress", "celebrity", "entertainment",
                "television", "show", "series", "concert", "album", "song", "artist",
                "performance", "theater", "hollywood", "netflix", "streaming", "gaming",
                "video", "youtube", "social", "media"
            ],
            "Education": [
                "education", "school", "university", "college", "student", "teacher",
                "professor", "learning", "course", "degree", "academic", "research",
                "study", "curriculum", "classroom", "tuition", "scholarship", "exam",
                "graduate", "undergraduate", "diploma"
            ]
        }
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of the text"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        if polarity > 0.1:
            sentiment = "Positive"
            emoji = "😊"
        elif polarity < -0.1:
            sentiment = "Negative"
            emoji = "😟"
        else:
            sentiment = "Neutral"
            emoji = "😐"
        
        return {
            "sentiment": sentiment,
            "emoji": emoji,
            "polarity": round(polarity, 2),
            "subjectivity": round(subjectivity, 2),
            "description": self._get_sentiment_description(polarity, subjectivity)
        }
    
    def _get_sentiment_description(self, polarity, subjectivity):
        """Generate human-readable sentiment description"""
        tone = "positive" if polarity > 0.1 else "negative" if polarity < -0.1 else "neutral"
        style = "subjective/opinion-based" if subjectivity > 0.5 else "objective/factual"
        return f"The content has a {tone} tone and is {style}."
    
    def calculate_reading_time(self, text):
        """Calculate estimated reading time"""
        words = text.split()
        word_count = len(words)
        minutes = round(word_count / 225)
        
        if minutes < 1:
            reading_time = "Less than 1 minute"
        elif minutes == 1:
            reading_time = "1 minute"
        else:
            reading_time = f"{minutes} minutes"
        
        return {
            "reading_time": reading_time,
            "word_count": word_count,
            "minutes": minutes
        }
    
    def extract_keywords(self, text, top_n=10):
        """Extract top keywords from text"""
        text_lower = text.lower()
        words = re.findall(r'\b[a-z]+\b', text_lower)
        
        keywords = [
            word for word in words 
            if word not in self.stop_words 
            and len(word) > 3
        ]
        
        word_freq = Counter(keywords)
        top_keywords = word_freq.most_common(top_n)
        
        return [
            {"word": word, "frequency": freq} 
            for word, freq in top_keywords
        ]
    
    def get_content_stats(self, text):
        """Get basic content statistics"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        words = text.split()
        
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        unique_words = len(set(word.lower() for word in words if word.isalnum()))
        vocab_richness = unique_words / len(words) if words else 0
        
        return {
            "total_sentences": len(sentences),
            "total_words": len(words),
            "unique_words": unique_words,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "vocabulary_richness": round(vocab_richness * 100, 1)
        }
    
    def extract_entities(self, text, max_chars=100000):
        """Extract named entities using spaCy NER"""
        text = text[:max_chars]
        doc = nlp(text)
        
        entities = {
            "people": [],
            "organizations": [],
            "locations": [],
            "dates": [],
            "money": [],
            "other": []
        }
        
        for ent in doc.ents:
            entity_text = ent.text.strip()
            
            if len(entity_text) < 2:
                continue
            
            if ent.label_ == "PERSON":
                if entity_text not in entities["people"]:
                    entities["people"].append(entity_text)
            elif ent.label_ == "ORG":
                if entity_text not in entities["organizations"]:
                    entities["organizations"].append(entity_text)
            elif ent.label_ in ["GPE", "LOC"]:
                if entity_text not in entities["locations"]:
                    entities["locations"].append(entity_text)
            elif ent.label_ == "DATE":
                if entity_text not in entities["dates"]:
                    entities["dates"].append(entity_text)
            elif ent.label_ == "MONEY":
                if entity_text not in entities["money"]:
                    entities["money"].append(entity_text)
            elif ent.label_ in ["PRODUCT", "EVENT", "WORK_OF_ART", "LAW", "LANGUAGE"]:
                if entity_text not in entities["other"]:
                    entities["other"].append(entity_text)
        
        for key in entities:
            entities[key] = entities[key][:10]
        
        return entities
    
    def detect_topics(self, text):
        """
        Detect main topics/categories in the text
        Returns: list of detected topics with scores
        """
        text_lower = text.lower()
        words = set(re.findall(r'\b[a-z]+\b', text_lower))
        
        topic_scores = {}
        
        for topic, keywords in self.topic_keywords.items():
            # Count how many topic keywords appear in the text
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            
            if matches > 0:
                # Calculate score (normalize by text length)
                score = (matches / len(keywords)) * 100
                topic_scores[topic] = round(score, 1)
        
        # Sort by score and get top 3 topics
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        if not sorted_topics:
            return [{"topic": "General", "confidence": "50%", "score": 50}]
        
        return [
            {
                "topic": topic,
                "confidence": f"{min(int(score * 2), 95)}%",  # Scale confidence
                "score": score
            }
            for topic, score in sorted_topics if score > 0
        ]
    
    def detect_language(self, text):
        """
        Detect language of the text
        Returns: dict with language info
        """
        try:
            # Limit text for performance
            sample_text = text[:1000]
            
            # Detect language
            lang_code = detect(sample_text)
            
            # Get probabilities for all detected languages
            lang_probs = detect_langs(sample_text)
            
            # Language name mapping
            lang_names = {
                'en': 'English',
                'es': 'Spanish',
                'fr': 'French',
                'de': 'German',
                'it': 'Italian',
                'pt': 'Portuguese',
                'ru': 'Russian',
                'ja': 'Japanese',
                'zh-cn': 'Chinese (Simplified)',
                'zh-tw': 'Chinese (Traditional)',
                'ar': 'Arabic',
                'hi': 'Hindi',
                'ko': 'Korean',
                'nl': 'Dutch',
                'sv': 'Swedish',
                'pl': 'Polish',
                'tr': 'Turkish'
            }
            
            primary_lang = lang_probs[0]
            confidence = round(primary_lang.prob * 100, 1)
            
            return {
                "language": lang_names.get(lang_code, lang_code.upper()),
                "code": lang_code,
                "confidence": f"{confidence}%",
                "is_english": lang_code == 'en'
            }
            
        except LangDetectException:
            return {
                "language": "Unknown",
                "code": "unknown",
                "confidence": "0%",
                "is_english": False
            }
    
    def calculate_readability(self, text):
        """
        Calculate readability score (Flesch Reading Ease)
        Score: 0-100 (higher = easier to read)
        """
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        words = text.split()
        
        if not sentences or not words:
            return {
                "score": 0,
                "level": "Unknown",
                "description": "Insufficient text"
            }
        
        # Count syllables (simplified method)
        def count_syllables(word):
            word = word.lower()
            vowels = 'aeiouy'
            count = 0
            previous_was_vowel = False
            
            for char in word:
                is_vowel = char in vowels
                if is_vowel and not previous_was_vowel:
                    count += 1
                previous_was_vowel = is_vowel
            
            # Adjust for silent e
            if word.endswith('e'):
                count -= 1
            
            # Ensure at least 1 syllable
            return max(1, count)
        
        total_syllables = sum(count_syllables(word) for word in words)
        
        # Flesch Reading Ease formula
        # Score = 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = total_syllables / len(words)
        
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        score = max(0, min(100, score))  # Clamp between 0-100
        
        # Determine reading level
        if score >= 90:
            level = "Very Easy"
            description = "Easily understood by 11-year-olds"
        elif score >= 80:
            level = "Easy"
            description = "Conversational English for consumers"
        elif score >= 70:
            level = "Fairly Easy"
            description = "Accessible to 13-15 year-olds"
        elif score >= 60:
            level = "Standard"
            description = "Plain English for general audience"
        elif score >= 50:
            level = "Fairly Difficult"
            description = "Requires high school level reading"
        elif score >= 30:
            level = "Difficult"
            description = "College level reading required"
        else:
            level = "Very Difficult"
            description = "Best understood by university graduates"
        
        return {
            "score": round(score, 1),
            "level": level,
            "description": description
        }
    
    def analyze_full(self, text):
        """Perform complete content analysis"""
        return {
            "sentiment": self.analyze_sentiment(text),
            "reading_time": self.calculate_reading_time(text),
            "keywords": self.extract_keywords(text),
            "statistics": self.get_content_stats(text),
            "entities": self.extract_entities(text),
            "topics": self.detect_topics(text),
            "language": self.detect_language(text),
            "readability": self.calculate_readability(text)
        }