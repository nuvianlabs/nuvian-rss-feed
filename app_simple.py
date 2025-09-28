from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests
from datetime import datetime
import json
import re
from rss_analyzer_simple import RSSAnalyzer
from integrations import IntegrationManager
from industry_feeds_simple import IndustryFeedManager

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
            # Simple RSS parsing using requests
            response = requests.get(feed_url, timeout=10)
            if response.status_code == 200:
                # Basic XML parsing to extract articles
                content = response.text
                articles.extend(parse_rss_content(content, feed_url))
        except Exception as e:
            print(f"Error parsing feed {feed_url}: {e}")
    
    # Analyze articles with AI
    analyzed_articles = analyzer.analyze_articles(articles, industry, relevance_criteria)
    
    # Return top articles
    return jsonify(analyzed_articles[:max_articles])

def parse_rss_content(content, feed_url):
    """Simple RSS content parser"""
    articles = []
    try:
        # Extract title, link, and description using regex
        import re
        
        # Find all item blocks
        items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
        
        for item in items[:10]:  # Limit to 10 items per feed
            title_match = re.search(r'<title>(.*?)</title>', item, re.DOTALL)
            link_match = re.search(r'<link>(.*?)</link>', item, re.DOTALL)
            desc_match = re.search(r'<description>(.*?)</description>', item, re.DOTALL)
            pub_match = re.search(r'<pubDate>(.*?)</pubDate>', item, re.DOTALL)
            
            if title_match and link_match:
                article = {
                    'title': clean_html(title_match.group(1)),
                    'link': clean_html(link_match.group(1)),
                    'summary': clean_html(desc_match.group(1)) if desc_match else '',
                    'published': clean_html(pub_match.group(1)) if pub_match else '',
                    'source': 'RSS Feed',
                    'feed_url': feed_url
                }
                articles.append(article)
    except Exception as e:
        print(f"Error parsing RSS content: {e}")
    
    return articles

def clean_html(text):
    """Remove HTML tags from text"""
    if not text:
        return ''
    import re
    # Remove HTML tags
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()

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
