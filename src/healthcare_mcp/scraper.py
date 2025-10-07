"""Web scraper for healthcare documents"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import re


class HealthDocumentScraper:
    """Scrapes and processes healthcare regulatory documents"""

    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Healthcare Compliance Research Bot)'
        })

    async def scrape_and_index(self, url: str, source_name: str, search_engine) -> int:
        """Scrape a document and add it to the search index"""

        # Fetch the page
        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # Extract text
        text = soup.get_text(separator='\n', strip=True)

        # Clean up text
        text = self._clean_text(text)

        # Split into chunks
        chunks = self._chunk_text(text)

        # Index chunks
        await search_engine.index_document(url, source_name, chunks)

        return len(chunks)

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        return text.strip()

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into manageable chunks"""
        # Split by paragraphs first
        paragraphs = text.split('\n\n')

        chunks = []
        current_chunk = ""

        for para in paragraphs:
            # If adding this paragraph exceeds chunk size, save current chunk
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para

        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks
