import csv
from neo4j import GraphDatabase, basic_auth
from benchmark import measure_execution

def run_tugraph_pipeline():
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("admin", "73@TuGraph"))
    with driver.session(database="default") as session:
        # Clear graph data/schema if existing
        try:
            session.run("CALL db.dropDB()")
        except Exception:
            pass

        # Create Vertex Label: 'User' with primary key 'id' and attributes (id, name, age)
        session.run("CALL db.createVertexLabel('User', 'id', 'id', 'INT64', false, 'name', 'STRING', false, 'age', 'INT32', false)")
        
        # Create Edge Label: 'FOLLOWS' with empty constraints '[]' and attribute 'since' (INT32, optional=true)
        session.run("CALL db.createEdgeLabel('FOLLOWS', '[]', 'since', 'INT32', true)")

        def load_all_data():
            # Load Users
            with open('users.csv', mode='r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    session.run(
                        "CREATE (u:User {id: $id, name: $name, age: $age})",
                        id=int(row['id']), name=row['name'], age=int(row['age'])
                    )

            # Load Edges
            with open('follows.csv', mode='r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    session.run(
                        """
                        MATCH (u1:User {id: $src}), (u2:User {id: $dst})
                        CREATE (u1)-[:FOLLOWS {since: $since}]->(u2)
                        """,
                        src=int(row['source_id']), dst=int(row['target_id']), since=int(row['since'])
                    )

        ingest_stats = measure_execution(load_all_data)
        print(f"[TuGraph Ingestion] Time: {ingest_stats['execution_time_sec']}s | RAM: {ingest_stats['memory_used_mb']} MB")

        # Q1: Point Lookup
        def q1_point_lookup():
            return session.run("MATCH (u:User {id: 100}) RETURN u").data()
        q1_stats = measure_execution(q1_point_lookup)
        print(f"[TuGraph Q1 - Point Lookup]: {q1_stats['execution_time_sec']}s")

        # Q2: 2-Hop Traversal
        def q2_2hop_query():
            return session.run("MATCH (a:User {id: 100})-[:FOLLOWS]->(b:User)-[:FOLLOWS]->(c:User) RETURN c.name").data()
        q2_stats = measure_execution(q2_2hop_query)
        print(f"[TuGraph Q2 - 2-Hop Query]: {q2_stats['execution_time_sec']}s")

        # Q3: 3-Hop Filtered
        def q3_3hop_filtered():
            return session.run("MATCH (a:User {id: 100})-[:FOLLOWS]->(b:User)-[:FOLLOWS]->(c:User)-[:FOLLOWS]->(d:User) WHERE d.age > 30 RETURN d.name").data()
        q3_stats = measure_execution(q3_3hop_filtered)
        print(f"[TuGraph Q3 - 3-Hop Filtered]: {q3_stats['execution_time_sec']}s")

        # Q4: Complex Aggregation
        def q4_complex_agg():
            return session.run("MATCH (a:User {id: 100})-[:FOLLOWS]->(b:User)-[:FOLLOWS]->(c:User) RETURN c.name AS name, COUNT(*) AS degree ORDER BY degree DESC LIMIT 10").data()
        q4_stats = measure_execution(q4_complex_agg)
        print(f"[TuGraph Q4 - Complex Aggregation]: {q4_stats['execution_time_sec']}s")

    driver.close()

if __name__ == "__main__":
    run_tugraph_pipeline()
