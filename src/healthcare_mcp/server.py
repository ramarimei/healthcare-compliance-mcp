"""Main MCP server implementation"""
import asyncio
import sys
from pathlib import Path
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import AnyUrl

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from healthcare_mcp.scraper import HealthDocumentScraper
from healthcare_mcp.search import VectorSearchEngine

# Initialize MCP server
app = Server("healthcare-compliance-mcp")

# Initialize components
scraper = HealthDocumentScraper()
search_engine = VectorSearchEngine()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="search_regulations",
            description="Search healthcare regulatory documents and guidelines using semantic search. Returns relevant excerpts from official sources like Medsafe, Pharmac, and clinical guidelines.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query (e.g., 'controlled drug prescribing requirements')"
                    },
                    "max_results": {
                        "type": "number",
                        "description": "Maximum number of results to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="scrape_document",
            description="Scrape and index a new healthcare document from a public URL. Use this to add new regulatory documents to the search index.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL of the document to scrape"
                    },
                    "source_name": {
                        "type": "string",
                        "description": "Name of the source (e.g., 'Medsafe', 'Pharmac')"
                    }
                },
                "required": ["url", "source_name"]
            }
        ),
        Tool(
            name="list_indexed_documents",
            description="List all documents currently indexed in the search database",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""

    if name == "search_regulations":
        query = arguments["query"]
        max_results = arguments.get("max_results", 5)

        results = await search_engine.search(query, max_results)

        if not results:
            return [TextContent(
                type="text",
                text="No matching documents found. Try rephrasing your query or scrape additional documents."
            )]

        # Format results
        response = "## Search Results\n\n"
        for i, result in enumerate(results, 1):
            response += f"### Result {i} (Relevance: {result['score']:.2f})\n"
            response += f"**Source:** {result['source']}\n"
            response += f"**URL:** {result['url']}\n\n"
            response += f"{result['text']}\n\n"
            response += "---\n\n"

        return [TextContent(type="text", text=response)]

    elif name == "scrape_document":
        url = arguments["url"]
        source_name = arguments["source_name"]

        try:
            doc_count = await scraper.scrape_and_index(url, source_name, search_engine)
            return [TextContent(
                type="text",
                text=f"Successfully scraped and indexed {doc_count} document chunks from {source_name}"
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error scraping document: {str(e)}"
            )]

    elif name == "list_indexed_documents":
        docs = await search_engine.list_documents()

        if not docs:
            return [TextContent(
                type="text",
                text="No documents indexed yet. Use 'scrape_document' to add documents."
            )]

        response = "## Indexed Documents\n\n"
        for doc in docs:
            response += f"- **{doc['source']}**: {doc['url']} ({doc['chunk_count']} chunks)\n"

        return [TextContent(type="text", text=response)]

    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


async def main():
    """Run the MCP server"""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
