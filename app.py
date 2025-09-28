from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
import feedparser
import requests
from datetime import datetime, timedelta
import json
import re
from rss_analyzer import RSSAnalyzer
from integrations import IntegrationManager
from industry_feeds import IndustryFeedManager

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize components
analyzer = RSSAnalyzer()
integration_manager = IntegrationManager()
industry_manager = IndustryFeedManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/industries')
def get_industries():
    """Get list of available industries"""
    return jsonify(industry_manager.get_industries())

@app.route('/api/feeds/discover', methods=['POST'])
def discover_feeds():
    """Discover RSS feeds for a given industry"""
    data = request.json
    industry = data.get('industry')
    custom_industry = data.get('custom_industry')
    max_feeds = data.get('max_feeds', 10)
    
    if custom_industry:
        industry = custom_industry
    
    feeds = industry_manager.discover_feeds(industry, max_feeds)
    return jsonify(feeds)

@app.route('/api/feeds/analyze', methods=['POST'])
def analyze_feeds():
    """Analyze RSS feeds and return relevant articles"""
    data = request.json
    feed_urls = data.get('feed_urls', [])
    max_articles = data.get('max_articles', 20)
    relevance_criteria = data.get('relevance_criteria', [])
    industry = data.get('industry', '')
    
    # Parse feeds and get articles
    articles = []
    for feed_url in feed_urls:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]:  # Limit per feed
                articles.append({
                    'title': entry.get('title', ''),
                    'summary': entry.get('summary', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'source': feed.feed.get('title', 'Unknown'),
                    'feed_url': feed_url
                })
        except Exception as e:
            print(f"Error parsing feed {feed_url}: {e}")
    
    # Analyze articles with AI
    analyzed_articles = analyzer.analyze_articles(articles, industry, relevance_criteria)
    
    # Return top articles
    return jsonify(analyzed_articles[:max_articles])

@app.route('/api/integrations/send', methods=['POST'])
def send_to_integration():
    """Send analyzed articles to external services"""
    data = request.json
    articles = data.get('articles', [])
    integration_type = data.get('integration_type')
    config = data.get('config', {})
    
    result = integration_manager.send_articles(articles, integration_type, config)
    return jsonify(result)

@app.route('/api/criteria')
def get_relevance_criteria():
    """Get available relevance criteria options"""
    criteria = [
        {
            'id': 'relevance',
            'name': 'Content Relevance',
            'description': 'How closely the content matches your industry focus'
        },
        {
            'id': 'recency',
            'name': 'Recency',
            'description': 'How recent the article is (newer is better)'
        },
        {
            'id': 'authority',
            'name': 'Source Authority',
            'description': 'Credibility and reputation of the source'
        },
        {
            'id': 'engagement',
            'name': 'Engagement Potential',
            'description': 'Likelihood to generate discussion or interest'
        },
        {
            'id': 'trending',
            'name': 'Trending Topics',
            'description': 'Articles covering currently trending topics'
        },
        {
            'id': 'expertise',
            'name': 'Expert Analysis',
            'description': 'Articles with expert opinions or analysis'
        },
        {
            'id': 'innovation',
            'name': 'Innovation Focus',
            'description': 'Articles about new technologies or methodologies'
        },
        {
            'id': 'market_impact',
            'name': 'Market Impact',
            'description': 'Potential impact on markets or business'
        }
    ]
    return jsonify(criteria)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
