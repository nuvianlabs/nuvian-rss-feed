import requests
from bs4 import BeautifulSoup
import feedparser
import re
from urllib.parse import urljoin, urlparse
import time

class IndustryFeedManager:
    def __init__(self):
        # Predefined industry-specific RSS feeds
        self.industry_feeds = {
            'technology': [
                'https://feeds.feedburner.com/oreilly/radar',
                'https://techcrunch.com/feed/',
                'https://feeds.feedburner.com/venturebeat/SZYF',
                'https://www.wired.com/feed/rss',
                'https://feeds.arstechnica.com/arstechnica/index/',
                'https://feeds.feedburner.com/oreilly/radar',
                'https://feeds.feedburner.com/techcrunch/startups',
                'https://feeds.feedburner.com/TechCrunch/',
                'https://feeds.feedburner.com/venturebeat/SZYF',
                'https://feeds.feedburner.com/oreilly/radar'
            ],
            'finance': [
                'https://feeds.finance.yahoo.com/rss/2.0/headline',
                'https://feeds.bloomberg.com/markets/news.rss',
                'https://feeds.reuters.com/news/wealth',
                'https://feeds.feedburner.com/zerohedge/feed',
                'https://feeds.marketwatch.com/marketwatch/topstories/',
                'https://feeds.finance.yahoo.com/rss/2.0/headline',
                'https://feeds.bloomberg.com/markets/news.rss',
                'https://feeds.reuters.com/news/wealth',
                'https://feeds.feedburner.com/zerohedge/feed',
                'https://feeds.marketwatch.com/marketwatch/topstories/'
            ],
            'healthcare': [
                'https://feeds.feedburner.com/healthcareitnews',
                'https://www.healthleadersmedia.com/rss.xml',
                'https://feeds.feedburner.com/HealthcareITNews',
                'https://www.medscape.com/rss',
                'https://feeds.feedburner.com/HealthcareITNews'
            ],
            'marketing': [
                'https://feeds.feedburner.com/marketingland',
                'https://www.marketingprofs.com/rss',
                'https://feeds.feedburner.com/ContentMarketingInstitute',
                'https://www.socialmediaexaminer.com/feed/',
                'https://feeds.feedburner.com/MarketingLand'
            ],
            'business': [
                'https://feeds.feedburner.com/entrepreneur',
                'https://www.forbes.com/business/feed/',
                'https://feeds.feedburner.com/IncMagazine',
                'https://www.fastcompany.com/feed',
                'https://feeds.feedburner.com/IncMagazine'
            ],
            'science': [
                'https://feeds.nature.com/nature/rss/current',
                'https://www.scientificamerican.com/rss/',
                'https://feeds.feedburner.com/ScienceDaily',
                'https://www.science.org/rss',
                'https://feeds.feedburner.com/ScienceDaily'
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
            feed = feedparser.parse(feed_url)
            return feed.feed.get('title', 'Unknown Feed')
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
            'technology': [
                'https://feeds.feedburner.com/oreilly/radar',
                'https://techcrunch.com/feed/',
                'https://www.wired.com/feed/rss',
                'https://feeds.arstechnica.com/arstechnica/index/',
                'https://feeds.feedburner.com/techcrunch/startups'
            ],
            'finance': [
                'https://feeds.finance.yahoo.com/rss/2.0/headline',
                'https://feeds.bloomberg.com/markets/news.rss',
                'https://feeds.reuters.com/news/wealth',
                'https://feeds.feedburner.com/zerohedge/feed',
                'https://feeds.marketwatch.com/marketwatch/topstories/'
            ]
        }
        
        # Return some common feeds as examples
        return common_feeds.get('technology', [])[:5]
    
    def _is_valid_feed(self, feed_url):
        """Check if a URL is a valid RSS feed"""
        try:
            feed = feedparser.parse(feed_url)
            return len(feed.entries) > 0
        except:
            return False
    
    def _find_rss_links(self, url):
        """Find RSS links on a webpage"""
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            rss_links = []
            
            # Look for RSS link tags
            for link in soup.find_all('link', type=['application/rss+xml', 'application/atom+xml']):
                href = link.get('href')
                if href:
                    rss_links.append(urljoin(url, href))
            
            # Look for common RSS patterns in links
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if any(pattern in href.lower() for pattern in self.rss_patterns):
                    rss_links.append(urljoin(url, href))
            
            return rss_links
        except:
            return []

