# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Autoscheduler2** is a Python-based project management scheduling tool that uses LLM agents to automate Critical Path Method (CPM) scheduling. The system uses AI to generate, modify, and remove project scope on behalf of users, with semantic search capabilities for querying schedules.

## Development Environment

- **Platform**: WSL (Windows Subsystem for Linux) running Ubuntu
- **Runtime**: Python with virtual environment
- **Databases**: 
  - Neo4j graph database (stores network topology)
  - Vector database with OpenAI embeddings (semantic search)
- **AI Integration**: OpenAI API for LLM agents and embeddings
- **Docker**: For Neo4j containerization

## Key Commands

```bash
# Environment setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Development
python main.py                    # Run the CLI application
pytest                           # Run tests
black .                          # Format code
flake8 .                         # Lint code
mypy .                           # Type checking

# Docker commands for Neo4j
docker ps                        # Check running containers
docker start <neo4j-container>   # Start Neo4j container
```

## Core Architecture

The system follows a multi-layered architecture with distinct separation of concerns:

### Data Layer
- **Neo4j Graph Database**: Stores complete network topology including activity sub-nodes (start, end, intra-activity nodes)
- **Vector Database**: OpenAI embeddings for activities and inter-activity relationships, enabling semantic search

### Domain Models (Pydantic Schemas)
- **ActivitySchema**: Represents project activities with UUID, name, description, duration
- **RelationshipSchema**: Represents dependencies between activities (FS, SS, FF, SF types)
- **RelationshipType**: Enum for relationship types (Finish-to-Start, Start-to-Start, etc.)

### Core Classes

#### Schedule Class
- Manages dual database representation (Neo4j + Vector embeddings)
- Maintains NetworkX DiGraph for critical path calculations
- Handles activity and relationship CRUD operations with two-phase commits

#### ScopeManager Class
- Primary interface between CLI and schedule logic
- Processes natural language requests into structured scope changes
- Key methods:
  - `_dispatch()`: Main entry point for user commands
  - `_separate_prompt()`: Splits user input into additions/removals
  - `_read_scope()`: Converts prompts to function calls using LLM tools
  - `_add_scope()` / `_remove_scope()`: Execute scope modifications
  - `_add_activity()` / `_delete_activity()`: Activity management
  - `_add_relationship()` / `_delete_relationship()`: Relationship management
  - `_dissolve_activity()`: Removes activity while preserving relationships

#### CLI Class
- Provides interactive command-line interface
- Offers structured menu options for direct operations
- Includes open-ended prompt mode for natural language interaction

#### LLMClient Class
- Handles OpenAI API interactions
- Provides methods for:
  - `prompt()`: Basic chat completions
  - `prompt_with_tools()`: Tool-calling functionality
  - `parse_structured()`: Structured output parsing

### Activity Representation Model
Activities are represented as three-node structures in Neo4j:
- **Start Node** (s-prefix): Activity beginning
- **End Node** (e-prefix): Activity completion  
- **Intra-Activity Node**: Represents duration between start and end
- Connected by directed edges with zero weight (duration picked up by intra-node)

### Relationship Handling
- **Intra-Activity**: Relationships within activities (start→duration→end)
- **Inter-Activity**: Dependencies between different activities
- **Database Strategy**: All nodes in Neo4j, but only high-level activities and inter-activity relationships in vector database

## Semantic Search Strategy
- Vector database queries identify relevant activities/relationships
- LLM agents make decisions on specific modifications
- Operations execute within activity sub-nodes to prevent incomplete semantic search issues
- Two-phase commit ensures data consistency across both databases

## Current State
The project has detailed architectural documentation and requirements.txt but no implementation code yet. The architecture is designed for a sophisticated scheduling system with AI-driven scope management.