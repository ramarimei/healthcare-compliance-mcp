# Healthcare Compliance MCP Server - Setup Guide

## Installation Complete!

All dependencies have been installed. Follow these steps to configure Claude Desktop:

## Configuration

1. **Locate your Claude Desktop config file:**
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Add this MCP server to your config:**

```json
{
  "mcpServers": {
    "healthcare-compliance": {
      "command": "python",
      "args": [
        "C:\\Users\\ramar\\Projects\\MCP-Project\\src\\healthcare_mcp\\server.py"
      ]
    }
  }
}
```

3. **Restart Claude Desktop**

## Usage

Once configured, you can use these tools in Claude Desktop:

### 1. Scrape a Document
```
Can you scrape this Medsafe page: https://www.medsafe.govt.nz/profs/datasheet/...
```

### 2. Search Indexed Documents
```
Search for "controlled drug prescribing requirements"
```

### 3. List Indexed Documents
```
What documents are currently indexed?
```

## Example Workflow

1. **Index some documents:**
   - "Scrape https://www.medsafe.govt.nz/regulatory/... and index it as 'Medsafe Guidelines'"

2. **Search your knowledge base:**
   - "What are the special authority requirements for this medication?"
   - "Search for prescription format requirements"

## Important Notes

- All documents stay local on your machine
- Uses local embeddings (no data sent to external APIs)
- For educational/research use only
- Not for clinical decision-making

## Testing the Server

You can test the server directly before configuring Claude Desktop:

```bash
python src/healthcare_mcp/server.py
```

The server should start without errors. Press Ctrl+C to stop.
