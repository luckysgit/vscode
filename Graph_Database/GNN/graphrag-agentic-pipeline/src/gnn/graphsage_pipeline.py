import os
import time
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

class Neo4jGNNPipeline:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    def close(self):
        self.driver.close()

    def setup_sample_network(self):
        """1. Ingests a synthetic host topology with telemetry features."""
        print("📥 [Step 1] Ingesting Network Telemetry Graph...")
        with self.driver.session() as session:
            # Clear old test data
            session.run("MATCH (n:Host) DETACH DELETE n")
            
            # Create network nodes with metadata features: [failed_logins, bytes_sent_mb, cpu_load]
            hosts = [
                {"id": "H1", "name": "Web-Gateway", "failed_logins": 2.0, "bytes_sent": 500.0, "cpu": 0.45},
                {"id": "H2", "name": "App-Server-1", "failed_logins": 1.0, "bytes_sent": 120.0, "cpu": 0.30},
                {"id": "H3", "name": "App-Server-2", "failed_logins": 0.0, "bytes_sent": 150.0, "cpu": 0.25},
                {"id": "H4", "name": "Core-DB", "failed_logins": 0.0, "bytes_sent": 2000.0, "cpu": 0.85},
                {"id": "H5", "name": "Compromised-Host", "failed_logins": 145.0, "bytes_sent": 9500.0, "cpu": 0.98}, # Anomaly
                {"id": "H6", "name": "C2-Proxy", "failed_logins": 80.0, "bytes_sent": 8200.0, "cpu": 0.90},        # Anomaly
            ]
            
            for h in hosts:
                session.run("""
                MERGE (h:Host {id: $id})
                SET h.name = $name,
                    h.failed_logins = $failed_logins,
                    h.bytes_sent = $bytes_sent,
                    h.cpu = $cpu
                """, **h)

            # Create connection topology
            connections = [
                ("H1", "H2"), ("H1", "H3"), ("H2", "H4"), ("H3", "H4"),
                ("H5", "H1"), ("H5", "H6"), ("H5", "H4") # Malicious lateral scan
            ]
            
            for source, target in connections:
                session.run("""
                MATCH (s:Host {id: $s}), (t:Host {id: $t})
                MERGE (s)-[:CONNECTS_TO]->(t)
                """, s=source, t=target)
        print("✅ Network topology created with 6 hosts and telemetry features.")

    def run_graphsage_gnn(self):
        """2. Projects graph, trains GraphSAGE GNN model, and writes back embeddings."""
        graph_name = "networkTelemetryGraph"
        model_name = "hostAnomalyGnnModel"

        with self.driver.session() as session:
            # Clean up previous GDS projections/models if they exist
            print("\n🧹 Cleaning existing GDS projections...")
            session.run("CALL gds.graph.drop($name, false)", name=graph_name)
            session.run("CALL gds.model.drop($model, false)", model=model_name)

            # 2a. Project Graph in GDS memory with Node Features
            print("🧠 [Step 2] Projecting Graph into Neo4j GDS Memory...")
            session.run("""
            CALL gds.graph.project(
                $graph_name,
                {
                    Host: {
                        properties: ['failed_logins', 'bytes_sent', 'cpu']
                    }
                },
                {
                    CONNECTS_TO: { orientation: 'UNDIRECTED' }
                }
            )
            """, graph_name=graph_name)

            # 2b. Train Inductive GraphSAGE GNN
            print("⚙️ [Step 3] Training Inductive GraphSAGE GNN Model...")
            start_time = time.time()
            session.run("""
            CALL gds.beta.graphSage.train(
                $graph_name,
                {
                    modelName: $model_name,
                    featureProperties: ['failed_logins', 'bytes_sent', 'cpu'],
                    embeddingDimension: 32,
                    epochs: 10,
                    aggregator: 'MEAN'
                }
            )
            """, graph_name=graph_name, model_name=model_name)
            print(f"✅ GNN Model trained in {round(time.time() - start_time, 2)} seconds.")

            # 2c. Write GNN Embeddings back to Neo4j Node Properties
            print("💾 [Step 4] Writing GNN Embeddings back to Neo4j Node Properties...")
            session.run("""
            CALL gds.beta.graphSage.write(
                $graph_name,
                {
                    modelName: $model_name,
                    writeProperty: 'gnnEmbedding'
                }
            )
            """, graph_name=graph_name, model_name=model_name)

            # 2d. Create Neo4j HNSW Vector Index on GNN Embeddings
            print("🔍 [Step 5] Creating HNSW Vector Index on GNN Embeddings...")
            session.run("""
            CREATE VECTOR INDEX `gnn_host_embeddings` IF NOT EXISTS
            FOR (h:Host) ON (h.gnnEmbedding)
            OPTIONS {indexConfig: {`vector.dimensions`: 32, `vector.similarity_function`: 'cosine'}}
            """)
            print("✅ HNSW Vector Index 'gnn_host_embeddings' created!")

    def verify_gnn_results(self):
        """3. Queries nodes using GNN structural embeddings."""
        print("\n📊 [Step 6] Verifying Learned GNN Representations...")
        with self.driver.session() as session:
            result = session.run("""
            MATCH (h:Host)
            RETURN h.id AS id, h.name AS name, size(h.gnnEmbedding) AS embedding_dim
            """)
            for record in result:
                print(f"Host: {record['id']} ({record['name']}) | GNN Vector Dimension: {record['embedding_dim']}")

            # Query anomaly similarity using GNN HNSW index
            print("\n🎯 Finding hosts structurally similar to 'Compromised-Host' (H5) using GNN vectors:")
            sim_result = session.run("""
            MATCH (target:Host {id: 'H5'})
            CALL db.index.vector.queryNodes('gnn_host_embeddings', 3, target.gnnEmbedding)
            YIELD node AS neighbor, score
            WHERE neighbor.id <> 'H5'
            RETURN neighbor.id AS id, neighbor.name AS name, score
            """)
            for rec in sim_result:
                print(f" - Similar Node: {rec['id']} ({rec['name']}) | Topology + Feature Score: {round(rec['score'], 4)}")

if __name__ == "__main__":
    pipeline = Neo4jGNNPipeline()
    try:
        pipeline.setup_sample_network()
        pipeline.run_graphsage_gnn()
        pipeline.verify_gnn_results()
    finally:
        pipeline.close()