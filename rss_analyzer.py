import openai
import os
from datetime import datetime
import re
from textblob import TextBlob
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except:
    pass

class RSSAnalyzer:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # Initialize TF-IDF vectorizer for content similarity
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def analyze_articles(self, articles, industry, relevance_criteria):
        """Analyze articles and return scored results"""
        if not articles:
            return []
        
        # Score articles based on multiple criteria
        scored_articles = []
        
        for article in articles:
            score = self._calculate_relevance_score(
                article, industry, relevance_criteria
            )
            
            article['relevance_score'] = score
            article['analysis'] = self._get_ai_analysis(article, industry)
            scored_articles.append(article)
        
        # Sort by relevance score
        scored_articles.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return scored_articles
    
    def _calculate_relevance_score(self, article, industry, criteria):
        """Calculate relevance score based on multiple factors"""
        score = 0.0
        max_score = 100.0
        
        # Content relevance (40% weight)
        content_score = self._analyze_content_relevance(article, industry)
        score += content_score * 0.4
        
        # Recency (20% weight)
        recency_score = self._analyze_recency(article)
        score += recency_score * 0.2
        
        # Source authority (20% weight)
        authority_score = self._analyze_source_authority(article)
        score += authority_score * 0.2
        
        # Custom criteria (20% weight)
        criteria_score = self._analyze_custom_criteria(article, criteria)
        score += criteria_score * 0.2
        
        return min(score, max_score)
    
    def _analyze_content_relevance(self, article, industry):
        """Analyze how relevant the content is to the industry"""
        if not industry:
            return 50.0  # Neutral score if no industry specified
        
        # Industry keywords mapping
        industry_keywords = {
            'technology': ['tech', 'software', 'AI', 'machine learning', 'cloud', 'cybersecurity', 'startup', 'innovation'],
            'finance': ['finance', 'banking', 'investment', 'trading', 'cryptocurrency', 'fintech', 'market', 'economy'],
            'healthcare': ['health', 'medical', 'pharmaceutical', 'biotech', 'healthcare', 'clinical', 'treatment', 'research'],
            'marketing': ['marketing', 'advertising', 'brand', 'social media', 'digital', 'content', 'SEO', 'campaign'],
            'business': ['business', 'corporate', 'management', 'strategy', 'leadership', 'entrepreneurship', 'startup'],
            'science': ['science', 'research', 'study', 'discovery', 'experiment', 'analysis', 'data', 'findings']
        }
        
        # Get keywords for the industry
        keywords = industry_keywords.get(industry.lower(), [industry])
        
        # Analyze title and summary
        text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        
        # Count keyword matches
        matches = sum(1 for keyword in keywords if keyword.lower() in text)
        relevance = min(matches * 20, 100)  # Max 100 points
        
        return relevance
    
    def _analyze_recency(self, article):
        """Analyze how recent the article is"""
        try:
            published = article.get('published', '')
            if not published:
                return 50.0  # Neutral if no date
            
            # Parse date (simplified)
            now = datetime.now()
            
            # Try to extract date from various formats
            date_patterns = [
                r'(\d{4}-\d{2}-\d{2})',
                r'(\d{2}/\d{2}/\d{4})',
                r'(\w+ \d{1,2}, \d{4})'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, published)
                if match:
                    try:
                        article_date = datetime.strptime(match.group(1), '%Y-%m-%d')
                        days_old = (now - article_date).days
                        
                        # Score based on age (newer = higher score)
                        if days_old <= 1:
                            return 100.0
                        elif days_old <= 7:
                            return 90.0
                        elif days_old <= 30:
                            return 70.0
                        elif days_old <= 90:
                            return 50.0
                        else:
                            return 30.0
                    except:
                        continue
            
            return 50.0  # Default if can't parse date
        except:
            return 50.0
    
    def _analyze_source_authority(self, article):
        """Analyze source authority and credibility"""
        source = article.get('source', '').lower()
        
        # Known authoritative sources
        authoritative_sources = [
            'reuters', 'bloomberg', 'wsj', 'wall street journal', 'new york times',
            'techcrunch', 'wired', 'arstechnica', 'hacker news', 'medium',
            'forbes', 'cnn', 'bbc', 'npr', 'pbs', 'scientific american',
            'nature', 'science', 'harvard', 'mit', 'stanford'
        ]
        
        for auth_source in authoritative_sources:
            if auth_source in source:
                return 90.0
        
        # Check for common indicators of authority
        authority_indicators = ['news', 'journal', 'times', 'post', 'tribune', 'herald']
        for indicator in authority_indicators:
            if indicator in source:
                return 70.0
        
        return 50.0  # Default neutral score
    
    def _analyze_custom_criteria(self, article, criteria):
        """Analyze based on user-selected criteria"""
        if not criteria:
            return 50.0
        
        score = 0.0
        text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        
        for criterion in criteria:
            if criterion == 'trending':
                # Look for trending indicators
                trending_words = ['trending', 'viral', 'popular', 'breaking', 'urgent']
                if any(word in text for word in trending_words):
                    score += 20
            elif criterion == 'innovation':
                # Look for innovation indicators
                innovation_words = ['new', 'breakthrough', 'innovation', 'disruptive', 'revolutionary']
                if any(word in text for word in innovation_words):
                    score += 20
            elif criterion == 'expertise':
                # Look for expert analysis indicators
                expertise_words = ['expert', 'analysis', 'research', 'study', 'report']
                if any(word in text for word in expertise_words):
                    score += 20
        
        return min(score, 100.0)
    
    def _get_ai_analysis(self, article, industry):
        """Get AI-powered analysis of the article"""
        if not self.openai_api_key:
            return "AI analysis not available (OpenAI API key required)"
        
        try:
            prompt = f"""
            Analyze this article for relevance to the {industry} industry:
            
            Title: {article.get('title', '')}
            Summary: {article.get('summary', '')}
            
            Provide a brief analysis (2-3 sentences) covering:
            1. Key relevance to {industry}
            2. Main insights or implications
            3. Why this article matters
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"AI analysis error: {str(e)}"

