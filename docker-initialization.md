# Docker Container Initialization in Autoscheduler2

This document explains how Docker containers for ChromaDB and Neo4j are initialized and managed in the Autoscheduler2 project.

## Overview

Autoscheduler2 uses Docker Compose to manage two database containers:
- **Neo4j**: Graph database for storing network topology and activity relationships
- **ChromaDB**: Vector database for semantic search capabilities using OpenAI embeddings

## Docker Compose Configuration

The project uses a `docker-compose.yml` file that defines both services:

### Neo4j Service Configuration

```yaml
neo4j:
  image: neo4j:5.15-community
  container_name: autoscheduler-neo4j
  ports:
    - "7474:7474"  # Web interface
    - "7687:7687"  # Bolt protocol
```

**Key Configuration Details:**
- Uses Neo4j Community Edition version 5.15
- Exposes port 7474 for the web-based Neo4j Browser interface
- Exposes port 7687 for Bolt protocol connections (used by the application)
- Default credentials: `neo4j/password`
- APOC plugin enabled for advanced graph operations
- Memory configuration: 512MB initial heap, 1GB max heap, 512MB page cache
- Health check via cypher-shell command

### ChromaDB Service Configuration

```yaml
chromadb:
  image: chromadb/chroma:0.4.24
  container_name: autoscheduler-chromadb
  ports:
    - "8000:8000"
```

**Key Configuration Details:**
- Uses ChromaDB version 0.4.24
- Exposes port 8000 for HTTP API access
- Server configured to listen on all interfaces (0.0.0.0)
- Telemetry disabled for privacy
- Health check via HTTP heartbeat endpoint

## Volume Management

The docker-compose configuration creates persistent volumes for data storage:

### Neo4j Volumes:
- `neo4j_data`: Database files
- `neo4j_logs`: Log files
- `neo4j_import`: Import directory for bulk data loading
- `neo4j_plugins`: Plugin directory (includes APOC)

### ChromaDB Volume:
- `chromadb_data`: Vector embeddings and metadata

All volumes use the local driver and persist data between container restarts.

## Network Configuration

Both containers are connected to a custom bridge network named `autoscheduler-network`, enabling:
- Container-to-container communication
- DNS resolution by container name
- Network isolation from other Docker applications

## Environment Variables

The application uses a `.env` file (created from `.env.example`) to configure database connections:

### Neo4j Environment Variables:
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
```

### ChromaDB Environment Variables:
```bash
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
```

## Application Integration

The Python application initializes database connections in the `Schedule` class (`src/autoscheduler/core/schedule.py`):

### Neo4j Initialization Process:
1. Load environment variables using `python-dotenv`
2. Create GraphDatabase driver with Bolt protocol
3. Test connection with `RETURN 1` query
4. Fall back to in-memory graph if connection fails

### ChromaDB Initialization Process:
1. Attempt HTTP client connection to ChromaDB server
2. Test connection with heartbeat check
3. Fall back to persistent client (file-based) if server unavailable
4. Create two collections:
   - `autoscheduler_activities`: For activity embeddings
   - `autoscheduler_relationships`: For relationship embeddings

## Starting the Containers

### Initial Setup:
1. Copy environment file: `cp .env.example .env`
2. Edit `.env` with appropriate values (especially OpenAI API key)
3. Start containers: `docker-compose up -d`

### Container Management Commands:
```bash
# Start containers in background
docker-compose up -d

# View container logs
docker-compose logs

# Stop containers (preserves data)
docker-compose down

# Stop containers and delete all data
docker-compose down -v

# Check container status
docker ps

# Restart a specific container
docker-compose restart neo4j
docker-compose restart chromadb
```

## Health Checks

Both containers include health check configurations:

### Neo4j Health Check:
- Executes cypher-shell command to verify database responsiveness
- Interval: 30 seconds
- Timeout: 10 seconds
- Retries: 3
- Start period: 40 seconds (allows for initial startup)

### ChromaDB Health Check:
- HTTP GET request to `/api/v1/heartbeat`
- Interval: 30 seconds
- Timeout: 10 seconds
- Retries: 3
- Start period: 20 seconds

## Initialization Flow

1. **Docker Compose Start**: `docker-compose up -d` creates and starts both containers
2. **Container Initialization**: 
   - Neo4j initializes graph database with configured memory settings
   - ChromaDB starts HTTP server on port 8000
3. **Health Check Validation**: Docker monitors container health
4. **Application Connection**:
   - Schedule class attempts to connect to both databases
   - Connections are tested before being accepted
   - Fallback mechanisms ensure application continues if databases unavailable
5. **Collection Creation**: ChromaDB collections are created on first run

## Troubleshooting

### Neo4j Connection Issues:
- Check if container is running: `docker ps | grep neo4j`
- View logs: `docker-compose logs neo4j`
- Access web interface: http://localhost:7474
- Verify credentials in `.env` file

### ChromaDB Connection Issues:
- Check if container is running: `docker ps | grep chromadb`
- View logs: `docker-compose logs chromadb`
- Test API endpoint: `curl http://localhost:8000/api/v1/heartbeat`
- Application will fall back to file-based storage if server unavailable

### Data Persistence:
- Data persists in Docker volumes between container restarts
- To reset databases: `docker-compose down -v` (WARNING: deletes all data)
- Volume data location: Managed by Docker (use `docker volume inspect` to find paths)

## Security Considerations

1. **Default Credentials**: Change Neo4j password in production
2. **Network Exposure**: Containers bind to localhost by default
3. **Authentication**: ChromaDB authentication is disabled but can be enabled via environment variables
4. **Data Encryption**: Not enabled by default in community editions

## Performance Tuning

### Neo4j Performance:
- Adjust heap memory based on available system resources
- Increase page cache for better query performance
- Monitor via Neo4j Browser metrics

### ChromaDB Performance:
- Vector search performance depends on collection size
- Consider indexing strategies for large datasets
- Monitor API response times

This initialization system provides a robust, containerized database infrastructure for the Autoscheduler2 project with automatic fallbacks and health monitoring.