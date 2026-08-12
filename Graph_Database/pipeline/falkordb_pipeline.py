import csv
from falkordb import FalkorDB
from benchmark import measure_execution

def run_falkordb_pipeline():
    db = FalkorDB(host='localhost', port=6379)
    g = db.select_graph('social_graph')

    try:
        g.delete()
    except Exception:
        pass

    g.query("CREATE INDEX FOR (u:User) ON (u.id)")

    def load_users():
        with open('users.csv', mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                props = [f"id: {row['id']}", f"name: '{row['name']}'", f"age: {row['age']}"]
                for i in range(1, 51):
                    props.append(f"attr_{i}: '{row[f'attr_{i}']}'")
                
                query = f"CREATE (:User {{{', '.join(props)}}})"
                g.query(query)

    def load_edges():
        with open('follows.csv', mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                query = f"""
                MATCH (u1:User {{id: {row['source_id']}}}), (u2:User {{id: {row['target_id']}}})
                CREATE (u1)-[:FOLLOWS {{since: {row['since']}}}]->(u2)
                """
                g.query(query)

    def load_all_data():
        load_users()
        load_edges()

    ingest_stats = measure_execution(load_all_data)
    print(f"[FalkorDB Ingestion] Time: {ingest_stats['execution_time_sec']}s | RAM: {ingest_stats['memory_used_mb']} MB")

    # Q1: Easy Point Lookup
    def q1_point_lookup():
        return g.query("MATCH (u:User {id: 100}) RETURN u").result_set
    q1_stats = measure_execution(q1_point_lookup)
    print(f"[FalkorDB Q1 - Retrieval Time (Point Lookup)]: {q1_stats['execution_time_sec']}s")

    # Q2: Moderate 2-Hop Traversal
    def q2_2hop_query():
        return g.query("MATCH (a:User {id: 100})-[:FOLLOWS]->(b:User)-[:FOLLOWS]->(c:User) RETURN c.name").result_set
    q2_stats = measure_execution(q2_2hop_query)
    print(f"[FalkorDB Q2 - Retrieval Time (2-Hop Query)]: {q2_stats['execution_time_sec']}s")

    # Q3: Hard 3-Hop Traversal + Filter
    def q3_3hop_filtered():
        return g.query("MATCH (a:User {id: 100})-[:FOLLOWS]->(b)-[:FOLLOWS]->(c)-[:FOLLOWS]->(d:User) WHERE d.age > 30 RETURN d.name, d.attr_1").result_set
    q3_stats = measure_execution(q3_3hop_filtered)
    print(f"[FalkorDB Q3 - Retrieval Time (3-Hop Filtered)]: {q3_stats['execution_time_sec']}s")

    # Q4: Complex Aggregation
    def q4_complex_agg():
        return g.query("MATCH (a:User {id: 100})-[:FOLLOWS]->(b)-[:FOLLOWS]->(c:User) RETURN c.name, COUNT(c) AS degree ORDER BY degree DESC LIMIT 10").result_set
    q4_stats = measure_execution(q4_complex_agg)
    print(f"[FalkorDB Q4 - Retrieval Time (Complex Aggregation)]: {q4_stats['execution_time_sec']}s")

if __name__ == "__main__":
    run_falkordb_pipeline()
