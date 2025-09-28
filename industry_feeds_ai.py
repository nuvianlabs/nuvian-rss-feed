import requests
import re
from urllib.parse import urljoin, urlparse
import time

class IndustryFeedManager:
    def __init__(self):
        # AI-focused RSS feeds with unique sources
        self.industry_feeds = {
            'ai': [
                'https://techcrunch.com/feed/',
                'https://www.wired.com/feed/rss',
                'https://feeds.arstechnica.com/arstechnica/index/',
                'https://feeds.feedburner.com/venturebeat/SZYF',
                'https://feeds.feedburner.com/TechCrunch/',
                'https://www.theverge.com/rss/index.xml',
                'https://feeds.feedburner.com/oreilly/radar',
                'https://feeds.feedburner.com/techcrunch/startups',
                'https://feeds.feedburner.com/venturebeat/SZYF',
                'https://feeds.feedburner.com/oreilly/radar'
            ],
            'ai-models': [
                'https://techcrunch.com/feed/',
                'https://www.wired.com/feed/rss',
                'https://feeds.arstechnica.com/arstechnica/index/',
                'https://feeds.feedburner.com/venturebeat/SZYF',
                'https://feeds.feedburner.com/TechCrunch/',
                'https://www.theverge.com/rss/index.xml',
                'https://feeds.feedburner.com/oreilly/radar',
                'https://feeds.feedburner.com/techcrunch/startups',
                'https://feeds.feedburner.com/venturebeat/SZYF',
                'https://feeds.feedburner.com/oreilly/radar'
            ],
            'machine-learning': [
                'https://techcrunch.com/feed/',
                'https://www.wired.com/feed/rss',
                'https://feeds.arstechnica.com/arstechnica/index/',
                'https://feeds.feedburner.com/venturebeat/SZYF',
                'https://feeds.feedburner.com/TechCrunch/',
                'https://www.theverge.com/rss/index.xml',
                'https://feeds.feedburner.com/oreilly/radar',
                'https://feeds.feedburner.com/techcrunch/startups',
                'https://feeds.feedburner.com/venturebeat/SZYF',
                'https://feeds.feedburner.com/oreilly/radar'
            ],
            'ai-research': [
                'https://techcrunch.com/feed/',
                'https://www.wired.com/feed/rss',
                'https://feeds.arstechnica.com/arstechnica/index/',
                'https://feeds.feedburner.com/venturebeat/SZYF',
                'https://feeds.feedburner.com/TechCrunch/',
                'https://www.theverge.com/rss/index.xml',
                'https://feeds.feedburner.com/oreilly/radar',
                'https://feeds.feedburner.com/techcrunch/startups',
                'https://feeds.feedburner.com/venturebeat/SZYF',
                'https://feeds.feedburner.com/oreilly/radar'
            ],
            'ai-news': [
                'https://techcrunch.com/feed/',
                'https://www.wired.com/feed/rss',
                'https://feeds.arstechnica.com/arstechnica/index/',
                'https://feeds.feedburner.com/venturebeat/SZYF',
                'https://feeds.feedburner.com/TechCrunch/',
                'https://www.theverge.com/rss/index.xml',
                'https://feeds.feedburner.com/oreilly/radar',
                'https://feeds.feedburner.com/techcrunch/startups',
                'https://feeds.feedburner.com/venturebeat/SZYF',
                'https://feeds.feedburner.com/oreilly/radar'
            ]
        }
        
        # Common RSS discovery patterns
        self.rss_patterns = [
            '/feed/',
            '/rss/',
            '/rss.xml',
            '/feed.xml',
            '/atom.xml',
            '/feeds/',
            '.rss',
            '.xml'
        ]
    
    def get_industries(self):
        """Get list of available industries"""
        return list(self.industry_feeds.keys())
    
    def discover_feeds(self, industry, max_feeds=10):
        """Discover RSS feeds for a given industry"""
        feeds = []
        
        # Get predefined feeds for the industry
        if industry.lower() in self.industry_feeds:
            predefined_feeds = self.industry_feeds[industry.lower()]
            for feed_url in predefined_feeds[:max_feeds]:
                feeds.append({
                    'url': feed_url,
                    'title': self._get_feed_title(feed_url),
                    'type': 'predefined',
                    'industry': industry
                })
        
        # If we need more feeds, try to discover them
        if len(feeds) < max_feeds:
            discovered_feeds = self._discover_new_feeds(industry, max_feeds - len(feeds))
            feeds.extend(discovered_feeds)
        
        return feeds[:max_feeds]
    
    def _get_feed_title(self, feed_url):
        """Get the title of an RSS feed"""
        try:
            response = requests.get(feed_url, timeout=5)
            if response.status_code == 200:
                content = response.text
                title_match = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
                if title_match:
                    return clean_html(title_match.group(1))
            return 'Unknown Feed'
        except:
            return 'Unknown Feed'
    
    def _discover_new_feeds(self, industry, max_feeds):
        """Discover new RSS feeds for an industry using web search"""
        discovered_feeds = []
        
        # Search terms for the industry
        search_terms = [
            f"{industry} RSS feed",
            f"{industry} news RSS",
            f"{industry} blog RSS",
            f"best {industry} RSS feeds"
        ]
        
        for term in search_terms:
            if len(discovered_feeds) >= max_feeds:
                break
            
            # Use a simple web search approach
            feeds = self._search_for_feeds(term)
            for feed in feeds:
                if len(discovered_feeds) >= max_feeds:
                    break
                if self._is_valid_feed(feed):
                    discovered_feeds.append({
                        'url': feed,
                        'title': self._get_feed_title(feed),
                        'type': 'discovered',
                        'industry': industry
                    })
        
        return discovered_feeds
    
    def _search_for_feeds(self, search_term):
        """Search for RSS feeds using web search"""
        # This is a simplified approach - in production, you'd use a proper search API
        feeds = []
        
        # Common RSS feed URLs for different industries
        common_feeds = {
            'ai': [
                'https://techcrunch.com/feed/',
                'https://www.wired.com/feed/rss',
                'https://feeds.arstechnica.com/arstechnica/index/',
                'https://feeds.feedburner.com/venturebeat/SZYF',
                'https://feeds.feedburner.com/TechCrunch/'
            ],
            'ai-models': [
                'https://techcrunch.com/feed/',
                'https://www.wired.com/feed/rss',
                'https://feeds.arstechnica.com/arstechnica/index/',
                'https://feeds.feedburner.com/venturebeat/SZYF',
                'https://feeds.feedburner.com/TechCrunch/'
            ]
        }
        
        # Return some common feeds as examples
        return common_feeds.get('ai', [])[:5]
    
    def _is_valid_feed(self, feed_url):
        """Check if a URL is a valid RSS feed"""
        try:
            response = requests.get(feed_url, timeout=5)
            if response.status_code == 200:
                content = response.text
                # Check if it contains RSS-like content
                return '<rss' in content.lower() or '<feed' in content.lower()
            return False
        except:
            return False

def clean_html(text):
    """Remove HTML tags from text"""
    if not text:
        return ''
    # Remove HTML tags
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()