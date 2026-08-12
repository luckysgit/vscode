import csv
import pyTigerGraph as tg
from benchmark import measure_execution

def run_tigergraph_pipeline():
    conn = tg.TigerGraphConnection(
        host="http://127.0.0.1", 
        restppPort="9000", 
        gsPort="14240", 
        username="tigergraph", 
        password="tigergraph"
    )
    
    print(f"[TigerGraph Ping]: {conn.ping()}")

    try:
        print("[TigerGraph] Resetting schema...")
        conn.gsql("DROP ALL")
    except Exception as e:
        print(f"[GSQL Drop Notice]: {e}")

    # Proper GSQL syntax: PRIMARY_ID <attr_name> <data_type>
    schema_gsql = """
    CREATE VERTEX User(PRIMARY_ID id INT, name STRING, age INT)
    CREATE DIRECTED EDGE FOLLOWS(FROM User, TO User, since INT)
    CREATE GRAPH SocialGraph(User, FOLLOWS)
    """
    print("[TigerGraph] Creating Graph Schema...")
    res = conn.gsql(schema_gsql)
    print(f"[GSQL Schema Result]:\n{res}")

    conn.graphname = "SocialGraph"
    try:
        secret = conn.createSecret()
        token = conn.getToken(secret)
        if isinstance(token, tuple):
            token = token[0]
        conn.apiToken = token
    except Exception as e:
        print(f"[Auth Token Notice]: {e}")

    def load_all_data():
        user_rows = []
        with open('users.csv', mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                user_rows.append({
                    "id": int(row['id']), 
                    "name": row['name'], 
                    "age": int(row['age'])
                })
        conn.upsertVertices("User", user_rows)

        edge_rows = []
        with open('follows.csv', mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                edge_rows.append((
                    int(row['source_id']), 
                    int(row['target_id']), 
                    {"since": int(row['since'])}
                ))
        conn.upsertEdges("User", "FOLLOWS", "User", edge_rows)

    ingest_stats = measure_execution(load_all_data)
    print(f"[TigerGraph Ingestion] Time: {ingest_stats['execution_time_sec']}s | RAM: {ingest_stats['memory_used_mb']} MB")

    # Q1: Point Lookup
    def q1_point_lookup():
        return conn.getVerticesById("User", 100)
    q1_stats = measure_execution(q1_point_lookup)
    print(f"[TigerGraph Q1 - Point Lookup]: {q1_stats['execution_time_sec']}s")

    # Q2: 1-Hop Neighbor Lookup
    def q2_neighbors():
        return conn.getNeighbors("User", 100, edgeType="FOLLOWS")
    q2_stats = measure_execution(q2_neighbors)
    print(f"[TigerGraph Q2 - 1-Hop Neighbors]: {q2_stats['execution_time_sec']}s")

if __name__ == "__main__":
    run_tigergraph_pipeline()
