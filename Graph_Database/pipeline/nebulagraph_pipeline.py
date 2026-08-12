import csv
import time
from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config
from benchmark import measure_execution

def run_nebulagraph_pipeline():
    config = Config()
    config.max_connection_pool_size = 10
    connection_pool = ConnectionPool()
    
    if not connection_pool.init([('127.0.0.1', 9669)], config):
        print("Failed to connect to NebulaGraph on port 9669.")
        return

    session = connection_pool.get_session('root', 'nebula')

    # Schema setup
    session.execute('DROP SPACE IF EXISTS social_graph_db;')
    time.sleep(3)
    session.execute('CREATE SPACE IF NOT EXISTS social_graph_db(partition_num=1, replica_factor=1, vid_type=INT64);')
    time.sleep(6)  # Asynchronous meta propagation
    session.execute('USE social_graph_db;')

    attr_schema = ", ".join([f"attr_{i} string" for i in range(1, 51)])
    session.execute(f'CREATE TAG IF NOT EXISTS User(name string, age int, {attr_schema});')
    session.execute('CREATE EDGE IF NOT EXISTS FOLLOWS(since int);')
    time.sleep(6)

    def load_all_data():
        # Load Users
        with open('users.csv', mode='r') as f:
            reader = csv.DictReader(f)
            batch = []
            for row in reader:
                uid = row['id']
                name = row['name'].replace('"', '\\"')
                age = row['age']
                attrs = ", ".join([f'"{row[f"attr_{i}"]}"' for i in range(1, 51)])
                batch.append(f'{uid}:("{name}", {age}, {attrs})')
                
                if len(batch) >= 500:
                    stmt = f"INSERT VERTEX User(name, age, {', '.join([f'attr_{i}' for i in range(1, 51)])}) VALUES " + ", ".join(batch) + ";"
                    session.execute(stmt)
                    batch = []
            if batch:
                stmt = f"INSERT VERTEX User(name, age, {', '.join([f'attr_{i}' for i in range(1, 51)])}) VALUES " + ", ".join(batch) + ";"
                session.execute(stmt)

        # Load Edges
        with open('follows.csv', mode='r') as f:
            reader = csv.DictReader(f)
            batch = []
            for row in reader:
                src = row['source_id']
                dst = row['target_id']
                since = row['since']
                batch.append(f'{src} -> {dst}:({since})')
                
                if len(batch) >= 1000:
                    stmt = "INSERT EDGE FOLLOWS(since) VALUES " + ", ".join(batch) + ";"
                    session.execute(stmt)
                    batch = []
            if batch:
                stmt = "INSERT EDGE FOLLOWS(since) VALUES " + ", ".join(batch) + ";"
                session.execute(stmt)

    ingest_stats = measure_execution(load_all_data)
    print(f"[NebulaGraph Ingestion] Time: {ingest_stats['execution_time_sec']}s | RAM: {ingest_stats['memory_used_mb']} MB")

    session.execute('CREATE TAG INDEX IF NOT EXISTS user_id_idx ON User();')
    time.sleep(4)

    # Q1: Point Lookup
    def q1_point_lookup():
        return session.execute('FETCH PROP ON User 100 YIELD vertex() AS u;')
    q1_stats = measure_execution(q1_point_lookup)
    print(f"[NebulaGraph Q1 - Point Lookup]: {q1_stats['execution_time_sec']}s")

    # Q2: 2-Hop Query
    def q2_2hop_query():
        return session.execute('GO 2 STEPS FROM 100 OVER FOLLOWS YIELD $$.User.name AS name;')
    q2_stats = measure_execution(q2_2hop_query)
    print(f"[NebulaGraph Q2 - 2-Hop Query]: {q2_stats['execution_time_sec']}s")

    # Q3: 3-Hop Filtered
    def q3_3hop_filtered():
        return session.execute('GO 3 STEPS FROM 100 OVER FOLLOWS WHERE $$.User.age > 30 YIELD $$.User.name AS name, $$.User.attr_1 AS attr_1;')
    q3_stats = measure_execution(q3_3hop_filtered)
    print(f"[NebulaGraph Q3 - 3-Hop Filtered]: {q3_stats['execution_time_sec']}s")

    # Q4: Complex Aggregation
    def q4_complex_agg():
        return session.execute('GO 2 STEPS FROM 100 OVER FOLLOWS YIELD $$.User.name AS name | GROUP BY $-.name YIELD $-.name AS name, COUNT(*) AS degree | ORDER BY $-.degree DESC | LIMIT 10;')
    q4_stats = measure_execution(q4_complex_agg)
    print(f"[NebulaGraph Q4 - Complex Aggregation]: {q4_stats['execution_time_sec']}s")

    session.release()

if __name__ == "__main__":
    run_nebulagraph_pipeline()
