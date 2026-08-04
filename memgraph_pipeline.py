import mgclient
from benchmark import measure_execution

def run_memgraph_pipeline():
    conn = mgclient.connect(host='127.0.0.1', port=7687)
    conn.autocommit = True
    cursor = conn.cursor()

    # 1. Clean existing database
    cursor.execute("MATCH (n) DETACH DELETE n;")

    # 2. Create Index on User(id)
    try:
        cursor.execute("CREATE INDEX ON :User(id);")
    except Exception as e:
        print(f"Index note: {e}")

    conn.autocommit = False

    # 3. Load Users
    def load_users():
        query = """
        LOAD CSV FROM 'file:///users.csv' WITH HEADER AS row
        CREATE (:User {id: ToInteger(row.id), name: row.name, age: ToInteger(row.age)});
        """
        cursor.execute(query)
        conn.commit()

    # 4. Load Edges
    def load_edges():
        query = """
        LOAD CSV FROM 'file:///follows.csv' WITH HEADER AS row
        MATCH (u1:User {id: ToInteger(row.source_id)}), (u2:User {id: ToInteger(row.target_id)})
        CREATE (u1)-[:FOLLOWS {since: ToInteger(row.since)}]->(u2);
        """
        cursor.execute(query)
        conn.commit()

    # 5. Measure Combined Ingestion
    def load_all_data():
        load_users()
        load_edges()

    ingest_stats = measure_execution(load_all_data)
    print(f"[Memgraph Ingestion] Time: {ingest_stats['execution_time_sec']}s | RAM: {ingest_stats['memory_used_mb']} MB")

    # 6. Measure 2-Hop Traversal Query
    def run_2hop_query():
        query = "MATCH (a:User {id: 100})-[:FOLLOWS]->(b:User)-[:FOLLOWS]->(c:User) RETURN c.name;"
        cursor.execute(query)
        results = cursor.fetchall()
        return results

    query_stats = measure_execution(run_2hop_query)
    print(f"[Memgraph 2-Hop Query] Time: {query_stats['execution_time_sec']}s")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    run_memgraph_pipeline()
