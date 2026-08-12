import csv
from falkordb import FalkorDB
from benchmark import measure_execution

def run_falkordb_pipeline():
    db = FalkorDB(host='localhost', port=6379)
    g = db.select_graph('social_graph')
    
    # 1. Clean Graph & Setup Index
    try:
        g.delete()
    except Exception:
        pass

    g = db.select_graph('social_graph')
    try:
        g.query("CREATE INDEX FOR (u:User) ON (u.id)")
    except Exception:
        pass

    # 2. Ingest Nodes and Edges in Batches
    def load_all_data():
        # Batch Users
        users_batch = []
        with open('users.csv', mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                users_batch.append(f"({row['name']}_node:User {{id: {row['id']}, name: '{row['name']}', age: {row['age']}}})")
                if len(users_batch) >= 500:
                    g.query("CREATE " + ", ".join(users_batch))
                    users_batch = []
            if users_batch:
                g.query("CREATE " + ", ".join(users_batch))

        # Batch Edges via Parameterized Query
        with open('follows.csv', mode='r') as f:
            reader = csv.DictReader(f)
            edge_batch = []
            for row in reader:
                edge_batch.append({"s": int(row['source_id']), "t": int(row['target_id']), "since": int(row['since'])})
                if len(edge_batch) >= 500:
                    query = """
                    UNWIND $batch AS row
                    MATCH (u1:User {id: row.s}), (u2:User {id: row.t})
                    CREATE (u1)-[:FOLLOWS {since: row.since}]->(u2)
                    """
                    g.query(query, {"batch": edge_batch})
                    edge_batch = []
            if edge_batch:
                query = """
                UNWIND $batch AS row
                MATCH (u1:User {id: row.s}), (u2:User {id: row.t})
                CREATE (u1)-[:FOLLOWS {since: row.since}]->(u2)
                """
                g.query(query, {"batch": edge_batch})

    ingest_stats = measure_execution(load_all_data)
    print(f"[FalkorDB Ingestion] Time: {ingest_stats['execution_time_sec']}s | RAM: {ingest_stats['memory_used_mb']} MB")

    # 3. Measure 2-Hop Traversal Query
    def run_2hop_query():
        query = "MATCH (a:User {id: 100})-[:FOLLOWS]->(b:User)-[:FOLLOWS]->(c:User) RETURN c.name"
        return g.query(query).result_set

    query_stats = measure_execution(run_2hop_query)
    print(f"[FalkorDB 2-Hop Query] Time: {query_stats['execution_time_sec']}s")

if __name__ == "__main__":
    run_falkordb_pipeline()
