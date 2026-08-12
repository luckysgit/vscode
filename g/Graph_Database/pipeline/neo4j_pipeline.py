from neo4j import GraphDatabase
from benchmark import measure_execution

def run_neo4j_pipeline():
    URI = "bolt://localhost:7687"
    AUTH = ("neo4j", "password")
    
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        # 1. Clean Database & Setup Index
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n;")
            session.run("CREATE INDEX user_id_idx IF NOT EXISTS FOR (u:User) ON (u.id);")

        # 2. Load Users
        def load_users():
            query = """
            LOAD CSV WITH HEADERS FROM 'file:///users.csv' AS row
            CREATE (:User {id: toInteger(row.id), name: row.name, age: toInteger(row.age)});
            """
            with driver.session() as session:
                session.run(query)

        # 3. Load Edges
        def load_edges():
            query = """
            LOAD CSV WITH HEADERS FROM 'file:///follows.csv' AS row
            MATCH (u1:User {id: toInteger(row.source_id)}), (u2:User {id: toInteger(row.target_id)})
            CREATE (u1)-[:FOLLOWS {since: toInteger(row.since)}]->(u2);
            """
            with driver.session() as session:
                session.run(query)

        # 4. Measure Ingestion
        def load_all_data():
            load_users()
            load_edges()

        ingest_stats = measure_execution(load_all_data)
        print(f"[Neo4j Ingestion] Time: {ingest_stats['execution_time_sec']}s | RAM: {ingest_stats['memory_used_mb']} MB")

        # 5. Measure 2-Hop Traversal Query
        def run_2hop_query():
            query = "MATCH (a:User {id: 100})-[:FOLLOWS]->(b:User)-[:FOLLOWS]->(c:User) RETURN c.name;"
            with driver.session() as session:
                return session.run(query).data()

        query_stats = measure_execution(run_2hop_query)
        print(f"[Neo4j 2-Hop Query] Time: {query_stats['execution_time_sec']}s")

if __name__ == "__main__":
    run_neo4j_pipeline()
