# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Package Management
- Install dependencies: `uv sync`
- Add new dependency: `uv add <package>`
- Update dependencies: `uv lock --upgrade`

### Running the Application
- Main demo script: `uv run python test.py`
- Note: `main.py` is currently a placeholder

### Environment Setup
Create a `.env` file with the following variables:
```
FALKORDB_USERNAME=<your_username>
FALKORDB_PASSWORD=<your_password>
FALKORDB_HOST=localhost  # optional, defaults to localhost
FALKORDB_PORT=6379       # optional, defaults to 6379
FALKORDB_DATABASE=test   # optional, defaults to test
```

## Code Architecture

### Overview
This is a graph-based conversational AI context engineering application using Graphiti Core with FalkorDB as the backend. The project demonstrates how to build a knowledge graph from conversational data for improved context retrieval in chatbots.

### Key Components

1. **Graph Database Integration**
   - Uses FalkorDB (Redis-based graph database) via `graphiti-core[falkordb]`
   - Manages conversational context as graph nodes and relationships
   - Supports semantic search with BM25 retrieval and graph-based reranking

2. **Main Application Flow** (`test.py`)
   - Initializes FalkorDB connection and Graphiti instance
   - Builds graph indices and constraints
   - Adds conversational episodes to the graph
   - Performs various search operations:
     - Basic hybrid search (semantic + BM25)
     - Center node search with graph distance reranking
     - Direct node search using search recipes

3. **Episode Structure**
   - Episodes are the primary units of information
   - Each episode contains:
     - `content`: The actual conversation text
     - `type`: Episode type (e.g., `EpisodeType.message`)
     - `description`: Context about the conversation segment
   - Episodes are automatically processed to extract entities and relationships

4. **Search Capabilities**
   - Hybrid search combining semantic similarity and text retrieval
   - Graph-based reranking using center node distance
   - Configurable search recipes (e.g., `NODE_HYBRID_SEARCH_RRF`)

### Current Use Case
The demo (`test.py`) implements a Vietnamese language customer service chatbot for FPT Telecom, handling queries about:
- Internet packages (Super100, Super200)
- Combo deals (Internet + FPT Play)
- Product recommendations based on customer needs

### Async Programming
All database operations use async/await patterns for better performance and scalability.