"""Vector search engine using local embeddings"""
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import hashlib


class VectorSearchEngine:
    """Vector-based semantic search using local embeddings"""

    def __init__(self, persist_directory: str = "./chroma_db"):
        # Initialize ChromaDB (local vector database)
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="healthcare_docs",
            metadata={"description": "Healthcare compliance documents"}
        )

        # Initialize local embedding model (runs on your machine)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    async def index_document(self, url: str, source_name: str, chunks: List[str]):
        """Add document chunks to the vector index"""

        # Generate embeddings for all chunks
        embeddings = self.model.encode(chunks).tolist()

        # Create unique IDs for each chunk
        ids = [
            hashlib.md5(f"{url}_{i}".encode()).hexdigest()
            for i in range(len(chunks))
        ]

        # Metadata for each chunk
        metadatas = [
            {
                "url": url,
                "source": source_name,
                "chunk_index": i
            }
            for i in range(len(chunks))
        ]

        # Add to ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )

    async def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for documents matching the query"""

        # Generate embedding for query
        query_embedding = self.model.encode([query]).tolist()[0]

        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=max_results
        )

        # Format results
        formatted_results = []

        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'text': results['documents'][0][i],
                    'source': results['metadatas'][0][i]['source'],
                    'url': results['metadatas'][0][i]['url'],
                    'score': 1 - results['distances'][0][i]  # Convert distance to similarity
                })

        return formatted_results

    async def list_documents(self) -> List[Dict]:
        """List all indexed documents"""

        # Get all items from collection
        all_items = self.collection.get()

        if not all_items['metadatas']:
            return []

        # Group by URL
        docs_by_url = {}
        for metadata in all_items['metadatas']:
            url = metadata['url']
            if url not in docs_by_url:
                docs_by_url[url] = {
                    'url': url,
                    'source': metadata['source'],
                    'chunk_count': 0
                }
            docs_by_url[url]['chunk_count'] += 1

        return list(docs_by_url.values())
