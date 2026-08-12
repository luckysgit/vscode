import kuzu
import shutil
import os
from benchmark import measure_execution

def run_kuzu_pipeline():
    if os.path.exists('./kuzu_db'):
        if os.path.isdir('./kuzu_db'):
            shutil.rmtree('./kuzu_db')
        else:
            os.remove('./kuzu_db')
        
    db = kuzu.Database('./kuzu_db')
    conn = kuzu.Connection(db)

    attr_schema = ", ".join([f"attr_{i} STRING" for i in range(1, 51)])
    conn.execute(f"CREATE NODE TABLE User(id INT64, name STRING, age INT64, {attr_schema}, PRIMARY KEY (id))")
    conn.execute("CREATE REL TABLE FOLLOWS(FROM User TO User, since INT64)")

    def load_all_data():
        conn.execute("COPY User FROM 'users.csv'")
        conn.execute("COPY FOLLOWS FROM 'follows.csv'")

    ingest_stats = measure_execution(load_all_data)
    print(f"[KuzuDB Ingestion] Time: {ingest_stats['execution_time_sec']}s | RAM: {ingest_stats['memory_used_mb']} MB")

    # Q1: Point Lookup
    def q1_point_lookup():
        return conn.execute("MATCH (u:User {id: 100}) RETURN u").get_as_df()
    q1_stats = measure_execution(q1_point_lookup)
    print(f"[KuzuDB Q1 - Retrieval Time (Point Lookup)]: {q1_stats['execution_time_sec']}s")

    # Q2: 2-Hop Traversal
    def q2_2hop_query():
        return conn.execute("MATCH (a:User {id: 100})-[:FOLLOWS]->(b:User)-[:FOLLOWS]->(c:User) RETURN c.name").get_as_df()
    q2_stats = measure_execution(q2_2hop_query)
    print(f"[KuzuDB Q2 - Retrieval Time (2-Hop Query)]: {q2_stats['execution_time_sec']}s")

    # Q3: 3-Hop Traversal + Filter
    def q3_3hop_filtered():
        return conn.execute("MATCH (a:User {id: 100})-[:FOLLOWS]->(b:User)-[:FOLLOWS]->(c:User)-[:FOLLOWS]->(d:User) WHERE d.age > 30 RETURN d.name, d.attr_1").get_as_df()
    q3_stats = measure_execution(q3_3hop_filtered)
    print(f"[KuzuDB Q3 - Retrieval Time (3-Hop Filtered)]: {q3_stats['execution_time_sec']}s")

    # Q4: Complex Aggregation
    def q4_complex_agg():
        return conn.execute("MATCH (a:User {id: 100})-[:FOLLOWS]->(b:User)-[:FOLLOWS]->(c:User) RETURN c.name, COUNT(*) AS degree ORDER BY degree DESC LIMIT 10").get_as_df()
    q4_stats = measure_execution(q4_complex_agg)
    print(f"[KuzuDB Q4 - Retrieval Time (Complex Aggregation)]: {q4_stats['execution_time_sec']}s")

if __name__ == "__main__":
    run_kuzu_pipeline()

