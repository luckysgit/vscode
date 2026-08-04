import csv
from arango import ArangoClient
from benchmark import measure_execution

def run_arango_pipeline():
    client = ArangoClient(hosts='http://localhost:8529')
    db = client.db('_system', username='root', password='')

    # Reset Graph
    if db.has_graph('social_graph'):
        db.delete_graph('social_graph', drop_collections=True)
        
    graph = db.create_graph('social_graph')
    users = graph.create_vertex_collection('users')
    follows = graph.create_edge_definition(
        edge_collection='follows',
        from_vertex_collections=['users'],
        to_vertex_collections=['users']
    )

    users.add_persistent_index(fields=['id'])

    def load_all_data():
        user_docs = []
        with open('users.csv', mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                user_docs.append({
                    '_key': str(row['id']),
                    'id': int(row['id']),
                    'name': row['name'],
                    'age': int(row['age'])
                })
        users.insert_many(user_docs)

        edge_docs = []
        with open('follows.csv', mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                edge_docs.append({
                    '_from': f"users/{row['source_id']}",
                    '_to': f"users/{row['target_id']}",
                    'since': int(row['since'])
                })
        follows.insert_many(edge_docs)

    ingest_stats = measure_execution(load_all_data)
    print(f"[ArangoDB Ingestion] Time: {ingest_stats['execution_time_sec']}s | RAM: {ingest_stats['memory_used_mb']} MB")

    def run_2hop_query():
        aql_query = """
        FOR v, e, p IN 2..2 OUTBOUND 'users/100' GRAPH 'social_graph'
            RETURN v.name
        """
        return list(db.aql.execute(aql_query))

    query_stats = measure_execution(run_2hop_query)
    print(f"[ArangoDB 2-Hop Query] Time: {query_stats['execution_time_sec']}s")

if __name__ == "__main__":
    run_arango_pipeline()
