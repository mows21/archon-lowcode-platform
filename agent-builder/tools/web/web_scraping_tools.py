from pydantic_ai import Agent, RunContext
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import json
import re
from urllib.parse import urljoin

# Web Scraping Tools for ARCHON Agent Builder
# Compatible with Pydantic AI agent framework

class WebScrapingTools:
    """Collection of web scraping tools for AI agents"""
    
    @staticmethod
    def register_tools(agent: Agent):
        """Register all web scraping tools to an agent"""
        
        @agent.tool
        async def fetch_webpage(ctx: RunContext, url: str, timeout: int = 30) -> str:
            """
            Fetch the HTML content of a webpage
            
            Args:
                url: The URL to fetch
                timeout: Request timeout in seconds
                
            Returns:
                HTML content of the page
            """
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, timeout=timeout)
                    response.raise_for_status()
                    return response.text
            except httpx.RequestError as e:
                return f"Error fetching {url}: {str(e)}"
        
        @agent.tool
        async def extract_text(ctx: RunContext, html: str) -> str:
            """
            Extract readable text from HTML
            
            Args:
                html: HTML content
                
            Returns:
                Extracted text content
            """
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text and clean it
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        
        @agent.tool
        async def find_links(ctx: RunContext, html: str, base_url: Optional[str] = None) -> List[Dict[str, str]]:
            """
            Extract all links from HTML
            
            Args:
                html: HTML content
                base_url: Base URL for relative links
                
            Returns:
                List of links with text and href
            """
            soup = BeautifulSoup(html, 'html.parser')
            links = []
            
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                text = a_tag.get_text(strip=True)
                
                # Convert relative to absolute URLs
                if base_url and not href.startswith(('http://', 'https://')):
                    href = urljoin(base_url, href)
                
                links.append({
                    "text": text,
                    "url": href
                })
            
            return links
        
        @agent.tool
        async def find_images(ctx: RunContext, html: str, base_url: Optional[str] = None) -> List[Dict[str, str]]:
            """
            Extract all images from HTML
            
            Args:
                html: HTML content
                base_url: Base URL for relative paths
                
            Returns:
                List of images with alt text and src
            """
            soup = BeautifulSoup(html, 'html.parser')
            images = []
            
            for img_tag in soup.find_all('img'):
                src = img_tag.get('src', '')
                alt = img_tag.get('alt', '')
                
                # Convert relative to absolute URLs
                if base_url and not src.startswith(('http://', 'https://')):
                    src = urljoin(base_url, src)
                
                images.append({
                    "alt": alt,
                    "src": src
                })
            
            return images
        
        @agent.tool
        async def extract_tables(ctx: RunContext, html: str) -> List[List[List[str]]]:
            """
            Extract all tables from HTML
            
            Args:
                html: HTML content
                
            Returns:
                List of tables, each as list of rows, each row as list of cells
            """
            soup = BeautifulSoup(html, 'html.parser')
            tables = []
            
            for table in soup.find_all('table'):
                table_data = []
                for row in table.find_all('tr'):
                    row_data = []
                    for cell in row.find_all(['td', 'th']):
                        row_data.append(cell.get_text(strip=True))
                    table_data.append(row_data)
                tables.append(table_data)
            
            return tables
        
        @agent.tool
        async def extract_metadata(ctx: RunContext, html: str) -> Dict[str, Any]:
            """
            Extract metadata from HTML (title, meta tags, etc.)
            
            Args:
                html: HTML content
                
            Returns:
                Dictionary of extracted metadata
            """
            soup = BeautifulSoup(html, 'html.parser')
            metadata = {}
            
            # Extract title
            title_tag = soup.find('title')
            if title_tag:
                metadata['title'] = title_tag.get_text(strip=True)
            
            # Extract meta tags
            metadata['meta'] = {}
            for meta in soup.find_all('meta'):
                if meta.get('name'):
                    metadata['meta'][meta['name']] = meta.get('content', '')
                elif meta.get('property'):
                    metadata['meta'][meta['property']] = meta.get('content', '')
            
            # Extract headers
            metadata['headers'] = {}
            for i in range(1, 7):
                headers = [h.get_text(strip=True) for h in soup.find_all(f'h{i}')]
                if headers:
                    metadata['headers'][f'h{i}'] = headers
            
            return metadata
        
        @agent.tool
        async def find_by_pattern(ctx: RunContext, html: str, pattern: str) -> List[str]:
            """
            Find content using regex pattern
            
            Args:
                html: HTML content
                pattern: Regex pattern to search for
                
            Returns:
                List of matches
            """
            try:
                matches = re.findall(pattern, html)
                return matches
            except re.error as e:
                return [f"Invalid regex pattern: {str(e)}"]
        
        @agent.tool
        async def select_elements(ctx: RunContext, html: str, selector: str) -> List[Dict[str, Any]]:
            """
            Select elements using CSS selector
            
            Args:
                html: HTML content
                selector: CSS selector
                
            Returns:
                List of selected elements with text and attributes
            """
            soup = BeautifulSoup(html, 'html.parser')
            elements = []
            
            try:
                selected = soup.select(selector)
                for element in selected:
                    elem_data = {
                        "tag": element.name,
                        "text": element.get_text(strip=True),
                        "attributes": dict(element.attrs)
                    }
                    elements.append(elem_data)
                return elements
            except Exception as e:
                return [{"error": str(e)}]

# Example usage in an agent
if __name__ == "__main__":
    from pydantic_ai import Agent
    
    # Create an agent
    agent = Agent('gpt-4', system_prompt="You are a web scraping assistant.")
    
    # Register web scraping tools
    WebScrapingTools.register_tools(agent)
    
    # Agent can now use all the web scraping tools
    print("Web scraping tools registered successfully!")
