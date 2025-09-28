import smtplib
import requests
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

class IntegrationManager:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
    
    def send_articles(self, articles, integration_type, config):
        """Send articles to the specified integration"""
        try:
            if integration_type == 'email':
                return self._send_email(articles, config)
            elif integration_type == 'slack':
                return self._send_slack(articles, config)
            elif integration_type == 'airtable':
                return self._send_airtable(articles, config)
            elif integration_type == 'notion':
                return self._send_notion(articles, config)
            else:
                return {'success': False, 'error': 'Unsupported integration type'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _send_email(self, articles, config):
        """Send articles via email"""
        try:
            # Email configuration
            to_email = config.get('to_email')
            subject = config.get('subject', 'RSS Feed Analysis Results')
            
            if not to_email:
                return {'success': False, 'error': 'Email address required'}
            
            # Create email content
            html_content = self._format_articles_html(articles)
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            return {'success': True, 'message': f'Email sent to {to_email}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _send_slack(self, articles, config):
        """Send articles to Slack"""
        try:
            webhook_url = config.get('webhook_url')
            channel = config.get('channel', '#general')
            
            if not webhook_url:
                return {'success': False, 'error': 'Slack webhook URL required'}
            
            # Format articles for Slack
            slack_message = self._format_articles_slack(articles)
            
            payload = {
                'text': f'RSS Feed Analysis Results - {len(articles)} articles',
                'blocks': slack_message
            }
            
            response = requests.post(webhook_url, json=payload)
            
            if response.status_code == 200:
                return {'success': True, 'message': 'Message sent to Slack'}
            else:
                return {'success': False, 'error': f'Slack API error: {response.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _send_airtable(self, articles, config):
        """Send articles to Airtable"""
        try:
            api_key = config.get('api_key')
            base_id = config.get('base_id')
            table_name = config.get('table_name', 'RSS Articles')
            
            if not all([api_key, base_id]):
                return {'success': False, 'error': 'Airtable API key and base ID required'}
            
            # Prepare records for Airtable
            records = []
            for article in articles:
                record = {
                    'fields': {
                        'Title': article.get('title', ''),
                        'Summary': article.get('summary', ''),
                        'Link': article.get('link', ''),
                        'Source': article.get('source', ''),
                        'Published': article.get('published', ''),
                        'Relevance Score': article.get('relevance_score', 0),
                        'Analysis': article.get('analysis', '')
                    }
                }
                records.append(record)
            
            # Send to Airtable
            url = f'https://api.airtable.com/v0/{base_id}/{table_name}'
            headers = {'Authorization': f'Bearer {api_key}'}
            
            # Airtable allows up to 10 records per request
            batch_size = 10
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                payload = {'records': batch}
                
                response = requests.post(url, json=payload, headers=headers)
                
                if response.status_code != 200:
                    return {'success': False, 'error': f'Airtable API error: {response.status_code}'}
            
            return {'success': True, 'message': f'{len(articles)} articles sent to Airtable'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _send_notion(self, articles, config):
        """Send articles to Notion"""
        try:
            api_key = config.get('api_key')
            database_id = config.get('database_id')
            
            if not all([api_key, database_id]):
                return {'success': False, 'error': 'Notion API key and database ID required'}
            
            # Prepare records for Notion
            for article in articles:
                self._create_notion_page(api_key, database_id, article)
            
            return {'success': True, 'message': f'{len(articles)} articles sent to Notion'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _create_notion_page(self, api_key, database_id, article):
        """Create a Notion page for an article"""
        url = 'https://api.notion.com/v1/pages'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        }
        
        payload = {
            'parent': {'database_id': database_id},
            'properties': {
                'Title': {'title': [{'text': {'content': article.get('title', '')}}]},
                'Summary': {'rich_text': [{'text': {'content': article.get('summary', '')}}]},
                'Link': {'url': article.get('link', '')},
                'Source': {'rich_text': [{'text': {'content': article.get('source', '')}}]},
                'Relevance Score': {'number': article.get('relevance_score', 0)}
            }
        }
        
        response = requests.post(url, json=payload, headers=headers)
        return response.status_code == 200
    
    def _format_articles_html(self, articles):
        """Format articles as HTML for email"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .article {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
                .title {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
                .summary {{ color: #666; margin-bottom: 10px; }}
                .meta {{ font-size: 12px; color: #999; }}
                .score {{ background: #f0f0f0; padding: 5px; border-radius: 3px; display: inline-block; }}
            </style>
        </head>
        <body>
            <h2>RSS Feed Analysis Results</h2>
            <p>Found {len(articles)} relevant articles:</p>
        """
        
        for article in articles:
            html += f"""
            <div class="article">
                <div class="title">{article.get('title', 'No title')}</div>
                <div class="summary">{article.get('summary', 'No summary')}</div>
                <div class="meta">
                    Source: {article.get('source', 'Unknown')} | 
                    Published: {article.get('published', 'Unknown')} |
                    <span class="score">Relevance: {article.get('relevance_score', 0):.1f}%</span>
                </div>
                <div class="analysis">{article.get('analysis', '')}</div>
            </div>
            """
        
        html += "</body></html>"
        return html
    
    def _format_articles_slack(self, articles):
        """Format articles for Slack"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"RSS Feed Analysis Results ({len(articles)} articles)"
                }
            }
        ]
        
        for article in articles:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{article.get('title', 'No title')}*\n"
                           f"{article.get('summary', 'No summary')[:200]}...\n"
                           f"Source: {article.get('source', 'Unknown')} | "
                           f"Relevance: {article.get('relevance_score', 0):.1f}%"
                }
            })
        
        return blocks

