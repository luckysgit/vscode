import csv
import mgclient
from benchmark import measure_execution

def run_memgraph_pipeline():
    conn = mgclient.connect(host='127.0.0.1', port=7688)
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute("MATCH (n) DETACH DELETE n;")
    try:
        cursor.execute("CREATE INDEX ON :User(id);")
    except Exception:
        pass

    conn.autocommit = False

    def load_users():
        with open('users.csv', mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                props = [f"id: {row['id']}", f"name: '{row['name']}'", f"age: {row['age']}"]
                for i in range(1, 51):
                    props.append(f"attr_{i}: '{row[f'attr_{i}']}'")
                cursor.execute(f"CREATE (:User {{{', '.join(props)}}});")
        conn.commit()

    def load_edges():
        with open('follows.csv', mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute(f"MATCH (u1:User {{id: {row['source_id']}}}), (u2:User {{id: {row['target_id']}}}) CREATE (u1)-[:FOLLOWS {{since: {row['since']}}}]->(u2);")
        conn.commit()

    def load_all_data():
        load_users()
        load_edges()

    ingest_stats = measure_execution(load_all_data)
    print(f"[Memgraph Ingestion] Time: {ingest_stats['execution_time_sec']}s | RAM: {ingest_stats['memory_used_mb']} MB")

    # Q1: Point Lookup
    def q1_point_lookup():
        cursor.execute("MATCH (u:User {id: 100}) RETURN u.name;")
        return cursor.fetchall()
    q1_stats = measure_execution(q1_point_lookup)
    print(f"[Memgraph Q1 - Retrieval Time (Point Lookup)]: {q1_stats['execution_time_sec']}s")

    # Q2: 2-Hop Query
    def q2_2hop_query():
        cursor.execute("MATCH (a:User {id: 100})-[:FOLLOWS]->(b:User)-[:FOLLOWS]->(c:User) RETURN c.name;")
        return cursor.fetchall()
    q2_stats = measure_execution(q2_2hop_query)
    print(f"[Memgraph Q2 - Retrieval Time (2-Hop Query)]: {q2_stats['execution_time_sec']}s")

    # Q3: 3-Hop Filtered
    def q3_3hop_filtered():
        cursor.execute("MATCH (a:User {id: 100})-[:FOLLOWS]->(b:User)-[:FOLLOWS]->(c:User)-[:FOLLOWS]->(d:User) WHERE d.age > 30 RETURN d.name, d.attr_1;")
        return cursor.fetchall()
    q3_stats = measure_execution(q3_3hop_filtered)
    print(f"[Memgraph Q3 - Retrieval Time (3-Hop Filtered)]: {q3_stats['execution_time_sec']}s")

    # Q4: Complex Aggregation
    def q4_complex_agg():
        cursor.execute("MATCH (a:User {id: 100})-[:FOLLOWS]->(b:User)-[:FOLLOWS]->(c:User) RETURN c.name, COUNT(c) AS degree ORDER BY degree DESC LIMIT 10;")
        return cursor.fetchall()
    q4_stats = measure_execution(q4_complex_agg)
    print(f"[Memgraph Q4 - Retrieval Time (Complex Aggregation)]: {q4_stats['execution_time_sec']}s")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    run_memgraph_pipeline()
