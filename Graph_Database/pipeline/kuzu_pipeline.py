import kuzu
import os
from benchmark import measure_execution

def run_kuzudb_pipeline():
    # 1. Setup DB
    if os.path.exists("./kuzu_db"):
        os.system("rm -rf ./kuzu_db")
    
    db = kuzu.Database("./kuzu_db")
    conn = kuzu.Connection(db)

    # 2. Schema Creation
    conn.execute("CREATE NODE TABLE User(id INT64, name STRING, age INT64, PRIMARY KEY (id))")
    conn.execute("CREATE REL TABLE Follows(FROM User TO User, since INT64)")

    # 3. Bulk Ingestion Function
    def load_data():
        conn.execute("COPY User FROM 'users.csv'")
        conn.execute("COPY Follows FROM 'follows.csv'")

    # 4. Measure Ingestion
    ingest_stats = measure_execution(load_data)
    print(f"[KuzuDB Ingestion] Time: {ingest_stats['execution_time_sec']}s | RAM: {ingest_stats['memory_used_mb']} MB")

    # 5. Measure Read Traversal Query (2-Hop Traversal)
    def run_2hop_query():
        query = "MATCH (a:User {id: 100})-[:Follows]->(b:User)-[:Follows]->(c:User) RETURN c.name"
        return conn.execute(query)

    query_stats = measure_execution(run_2hop_query)
    print(f"[KuzuDB 2-Hop Query] Time: {query_stats['execution_time_sec']}s")

if __name__ == "__main__":
    run_kuzudb_pipeline()