"""
Schedule class for autoscheduler2.

Contains the database and NetworkX representation of the schedule.
"""

import logging
import os
from typing import Optional
import networkx as nx
from neo4j import GraphDatabase
import chromadb
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Schedule:
    """Contains the database and NetworkX representation of the schedule."""
    
    def __init__(self):
        """Initialize Schedule with Neo4j database, NetworkX graph, and embeddings."""
        # Set up logging
        self.logger = logging.getLogger('autoscheduler.core.schedule')
        self.logger.setLevel(logging.INFO)
        
        # Create console handler if no handlers exist
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        self.logger.info("Starting Schedule initialization...")
        
        # Initialize databases
        self.neo4j_db = self._initialize_neo4j()
        self.chroma_client = self._initialize_chromadb()
        
        # NetworkX DiGraph for critical path calculations
        self.graph = nx.DiGraph()
        self.logger.info("NetworkX DiGraph initialized for critical path calculations")
        
        # Vector embeddings collections
        self.activities_embeddings = self._get_or_create_collection("activities")
        self.relationships_embeddings = self._get_or_create_collection("relationships")
        
        self.logger.info("Schedule initialization completed successfully")
    
    def _initialize_neo4j(self) -> Optional[GraphDatabase.driver]:
        """Initialize Neo4j database connection."""
        try:
            uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
            username = os.getenv('NEO4J_USERNAME', 'neo4j')
            password = os.getenv('NEO4J_PASSWORD', 'password')
            
            self.logger.info(f"Attempting to connect to Neo4j at {uri}")
            driver = GraphDatabase.driver(uri, auth=(username, password))
            
            # Test connection
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                if test_value == 1:
                    self.logger.info("Neo4j connection established successfully")
                    return driver
                    
        except Exception as e:
            self.logger.warning(f"Failed to connect to Neo4j: {e}")
            self.logger.info("Continuing without Neo4j connection - will use in-memory graph only")
            
        return None
    
    def _initialize_chromadb(self) -> Optional[chromadb.Client]:
        """Initialize ChromaDB client for vector embeddings."""
        try:
            # Try to connect to ChromaDB server, fallback to persistent client
            chroma_host = os.getenv('CHROMADB_HOST', 'localhost')
            chroma_port = int(os.getenv('CHROMADB_PORT', '8000'))
            
            try:
                self.logger.info(f"Attempting to connect to ChromaDB server at {chroma_host}:{chroma_port}")
                # Use the correct client initialization for ChromaDB
                from chromadb.config import Settings
                client = chromadb.HttpClient(
                    host=chroma_host,
                    port=chroma_port
                )
                # Test connection
                client.heartbeat()
                self.logger.info("ChromaDB server connection established successfully")
                return client
            except Exception as server_error:
                self.logger.info(f"ChromaDB server not available: {server_error}")
                
            # Fallback to persistent client
            self.logger.info("Falling back to ChromaDB persistent client")
            data_path = os.getenv('CHROMADB_DATA_PATH', './chroma_data')
            client = chromadb.PersistentClient(path=data_path)
            self.logger.info(f"ChromaDB persistent client initialized at {data_path}")
            return client
            
        except Exception as e:
            self.logger.warning(f"Failed to initialize ChromaDB: {e}")
            self.logger.info("Continuing without vector database - semantic search will be unavailable")
            
        return None
    
    def _get_or_create_collection(self, collection_name: str):
        """Get or create a ChromaDB collection."""
        if not self.chroma_client:
            self.logger.debug(f"ChromaDB not available, skipping collection creation for {collection_name}")
            return None
            
        try:
            collection = self.chroma_client.get_or_create_collection(
                name=f"autoscheduler_{collection_name}",
                metadata={"description": f"Autoscheduler {collection_name} embeddings"}
            )
            self.logger.info(f"ChromaDB collection '{collection_name}' ready")
            return collection
        except Exception as e:
            self.logger.error(f"Failed to create ChromaDB collection '{collection_name}': {e}")
            return None
    
    @property
    def is_neo4j_connected(self) -> bool:
        """Check if Neo4j is connected and available."""
        if not self.neo4j_db:
            return False
        try:
            with self.neo4j_db.session() as session:
                session.run("RETURN 1").single()
            return True
        except Exception:
            return False
    
    @property
    def is_chromadb_connected(self) -> bool:
        """Check if ChromaDB is connected and available."""
        if not self.chroma_client:
            return False
        try:
            self.chroma_client.heartbeat()
            return True
        except Exception:
            return False
    
    def add_activity(self, activity) -> bool:
        """Add an activity to both Neo4j and embeddings databases.
        
        Args:
            activity (ActivitySchema): Activity object with name, description, duration, etc.
            
        Returns:
            bool: True if activity successfully added, False if failed
            
        Function:
            - Add activity entry to both Neo4j and Embeddings databases
            - Include the start, end, and intra relationship nodes in Neo4j
            - Include the standard activity details for embeddings matrix
            - Use two phase commit (try/except logic adding both, don't add if both don't work)
        """
        print(f"Adding activity to schedule: {activity}")
        return False
    
    def remove_activity(self, activity_id: str) -> bool:
        """Remove an activity from both databases.
        
        Args:
            activity_id (str): UUID of the activity to remove
            
        Returns:
            bool: True if activity successfully removed, False if not found or failed
            
        Function:
            - Remove activity and all its sub-nodes (start, end, intra) from Neo4j
            - Remove activity from embeddings database
            - Use two phase commit (try/except logic removing both)
        """
        print(f"Removing activity from schedule: {activity_id}")
        return False
    
    def add_relationship(self, relationship) -> bool:
        """Add a relationship to both databases.
        
        Args:
            relationship (RelationshipSchema): Relationship object with type, predecessor, successor, lag
            
        Returns:
            bool: True if relationship successfully added, False if failed
            
        Function:
            - Add inter-activity relationship node to both Neo4j and Embeddings databases
            - Create directed edges in Neo4j based on relationship type (FS, SS, FF, SF)
            - Use two phase commit (try/except logic adding both, don't add if both don't work)
        """
        print(f"Adding relationship to schedule: {relationship}")
        return False
    
    def remove_relationship(self, relationship_id: str) -> bool:
        """Remove a relationship from both databases.
        
        Args:
            relationship_id (str): UUID of the relationship to remove
            
        Returns:
            bool: True if relationship successfully removed, False if not found or failed
            
        Function:
            - Remove relationship node and associated edges from Neo4j
            - Remove relationship from embeddings database
            - Use two phase commit (try/except logic removing both)
        """
        print(f"Removing relationship from schedule: {relationship_id}")
        return False
    
    def update_graph(self) -> bool:
        """Recompute NetworkX DiGraph from Neo4j database.
        
        Returns:
            bool: True if graph successfully updated, False if failed
            
        Function:
            - Query Neo4j database for all nodes and edges
            - Rebuild NetworkX DiGraph with current schedule topology
            - Called when schedule changes to keep graph representation current
        """
        print("Updating NetworkX graph from Neo4j database...")
        return False
    
    def compute_critical_path(self) -> list:
        """Compute the critical path using NetworkX algorithms.
        
        Returns:
            list: List of activity IDs representing the critical path, empty if no path found
            
        Function:
            - Use NetworkX longest path algorithms on the directed graph
            - Account for activity durations and relationship lags
            - Return sequence of activities that determines overall project duration
        """
        print("Computing critical path...")
        return []
    
    def get_activities(self) -> list:
        """Get all activities from the schedule.
        
        Returns:
            list: List of ActivitySchema objects representing all activities in the schedule
            
        Function:
            - Query activities from embeddings database
            - Return high-level activity objects (not sub-nodes)
        """
        return []
    
    def get_relationships(self) -> list:
        """Get all relationships from the schedule.
        
        Returns:
            list: List of RelationshipSchema objects representing all relationships in the schedule
            
        Function:
            - Query relationships from embeddings database
            - Return inter-activity relationship objects
        """
        return []
    
    def semantic_search_activities(self, query: str) -> list:
        """Search activities using semantic similarity.
        
        Args:
            query (str): Natural language query describing activities to find
            
        Returns:
            list: List of ActivitySchema objects matching the query, ranked by similarity
            
        Function:
            - Use vector embeddings to find activities semantically similar to query
            - Search through activity names, descriptions, and durations
            - Return ranked results for LLM decision making
        """
        print(f"Searching activities for: {query}")
        return []
    
    def semantic_search_relationships(self, query: str) -> list:
        """Search relationships using semantic similarity.
        
        Args:
            query (str): Natural language query describing relationships to find
            
        Returns:
            list: List of RelationshipSchema objects matching the query, ranked by similarity
            
        Function:
            - Use vector embeddings to find relationships semantically similar to query
            - Search through relationship types, predecessor/successor activity info, and lags
            - Return ranked results for LLM decision making
        """
        print(f"Searching relationships for: {query}")
        return []