import csv
from neo4j import GraphDatabase
from benchmark import measure_execution

def run_neo4j_pipeline():
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        session.run("CREATE INDEX user_id_index IF NOT EXISTS FOR (u:User) ON (u.id)")

        def load_all_data():
            # SET u = row dynamically loads all 50 attributes from users.csv
            session.run("""
            LOAD CSV WITH HEADERS FROM 'file:///users.csv' AS row
            CREATE (u:User)
            SET u = row,
                u.id = toInteger(row.id),
                u.age = toInteger(row.age)
            """)
            session.run("""
            LOAD CSV WITH HEADERS FROM 'file:///follows.csv' AS row
            MATCH (u1:User {id: toInteger(row.source_id)}), (u2:User {id: toInteger(row.target_id)})
            CREATE (u1)-[:FOLLOWS {since: toInteger(row.since)}]->(u2)
            """)

        ingest_stats = measure_execution(load_all_data)
        print(f"[Neo4j Ingestion] Time: {ingest_stats['execution_time_sec']}s | RAM: {ingest_stats['memory_used_mb']} MB")

        # Q1: Point Lookup
        def q1_point_lookup():
            return session.run("MATCH (u:User {id: 100}) RETURN u").data()
        q1_stats = measure_execution(q1_point_lookup)
        print(f"[Neo4j Q1 - Retrieval Time (Point Lookup)]: {q1_stats['execution_time_sec']}s")

        # Q2: 2-Hop Query
        def q2_2hop_query():
            return session.run("MATCH (a:User {id: 100})-[:FOLLOWS]->(b:User)-[:FOLLOWS]->(c:User) RETURN c.name").data()
        q2_stats = measure_execution(q2_2hop_query)
        print(f"[Neo4j Q2 - Retrieval Time (2-Hop Query)]: {q2_stats['execution_time_sec']}s")

        # Q3: 3-Hop Filtered
        def q3_3hop_filtered():
            return session.run("MATCH (a:User {id: 100})-[:FOLLOWS]->(b:User)-[:FOLLOWS]->(c:User)-[:FOLLOWS]->(d:User) WHERE d.age > 30 RETURN d.name, d.attr_1").data()
        q3_stats = measure_execution(q3_3hop_filtered)
        print(f"[Neo4j Q3 - Retrieval Time (3-Hop Filtered)]: {q3_stats['execution_time_sec']}s")

        # Q4: Complex Aggregation
        def q4_complex_agg():
            return session.run("MATCH (a:User {id: 100})-[:FOLLOWS]->(b:User)-[:FOLLOWS]->(c:User) RETURN c.name, COUNT(c) AS degree ORDER BY degree DESC LIMIT 10").data()
        q4_stats = measure_execution(q4_complex_agg)
        print(f"[Neo4j Q4 - Retrieval Time (Complex Aggregation)]: {q4_stats['execution_time_sec']}s")

    driver.close()

if __name__ == "__main__":
    run_neo4j_pipeline()
