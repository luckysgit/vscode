from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
from config.settings import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

class Neo4jClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    def initialize_schema_and_data(self):
        with self.driver.session() as session:
            session.run("""
            CREATE VECTOR INDEX `document_embeddings` IF NOT EXISTS
            FOR (d:Document) ON (d.embedding)
            OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}
            """)
            
            docs = [
                {"id": "doc1", "text": "GraphRAG combines vector search with knowledge graph traversals to give LLMs structured context.", "cat": "Architecture"},
                {"id": "doc2", "text": "Neo4j Community Edition supports native HNSW vector indexes without enterprise licensing.", "cat": "Database"}
            ]
            
            for doc in docs:
                vec = self.embedder.encode(doc["text"]).tolist()
                session.run("""
                MERGE (d:Document {id: $id})
                SET d.text = $text, d.embedding = $vec
                MERGE (c:Category {name: $cat})
                MERGE (d)-[:BELONGS_TO]->(c)
                """, id=doc["id"], text=doc["text"], vec=vec, cat=doc["cat"])

db_client = Neo4jClient()
