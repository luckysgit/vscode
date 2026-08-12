import csv
from arango import ArangoClient
from benchmark import measure_execution

def run_arango_pipeline():
    client = ArangoClient(hosts='http://localhost:8529')
    sys_db = client.db('_system', username='root', password='')

    if sys_db.has_database('social_graph_db'):
        sys_db.delete_database('social_graph_db')
    sys_db.create_database('social_graph_db')

    db = client.db('social_graph_db', username='root', password='')

    users = db.create_collection('User')
    # Updated index method to resolve DeprecationWarning
    users.add_index({'type': 'persistent', 'fields': ['id'], 'unique': True})
    follows = db.create_collection('FOLLOWS', edge=True)

    def load_all_data():
        user_batch = []
        with open('users.csv', mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                doc = {'_key': str(row['id']), 'id': int(row['id']), 'name': row['name'], 'age': int(row['age'])}
                for i in range(1, 51):
                    doc[f'attr_{i}'] = row[f'attr_{i}']
                user_batch.append(doc)
                if len(user_batch) >= 1000:
                    users.insert_many(user_batch)
                    user_batch = []
            if user_batch:
                users.insert_many(user_batch)

        edge_batch = []
        with open('follows.csv', mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                edge = {'_from': f"User/{row['source_id']}", '_to': f"User/{row['target_id']}", 'since': int(row['since'])}
                edge_batch.append(edge)
                if len(edge_batch) >= 1000:
                    follows.insert_many(edge_batch)
                    edge_batch = []
            if edge_batch:
                follows.insert_many(edge_batch)

    ingest_stats = measure_execution(load_all_data)
    print(f"[ArangoDB Ingestion] Time: {ingest_stats['execution_time_sec']}s | RAM: {ingest_stats['memory_used_mb']} MB")

    # Q1: Easy Point Lookup
    def q1_point_lookup():
        aql = "FOR u IN User FILTER u.id == 100 RETURN u"
        return list(db.aql.execute(aql))
    q1_stats = measure_execution(q1_point_lookup)
    print(f"[ArangoDB Q1 - Point Lookup] Time: {q1_stats['execution_time_sec']}s")

    # Q2: Moderate 2-Hop Traversal
    def q2_2hop_query():
        aql = "FOR u IN User FILTER u.id == 100 FOR b IN 1..1 OUTBOUND u FOLLOWS FOR c IN 1..1 OUTBOUND b FOLLOWS RETURN c.name"
        return list(db.aql.execute(aql))
    q2_stats = measure_execution(q2_2hop_query)
    print(f"[ArangoDB Q2 - 2-Hop Query] Time: {q2_stats['execution_time_sec']}s")

    # Q3: Hard 3-Hop Traversal + Attribute Filter
    def q3_3hop_filtered():
        aql = "FOR u IN User FILTER u.id == 100 FOR b IN 1..1 OUTBOUND u FOLLOWS FOR c IN 1..1 OUTBOUND b FOLLOWS FOR d IN 1..1 OUTBOUND c FOLLOWS FILTER d.age > 30 RETURN {name: d.name, attr_1: d.attr_1}"
        return list(db.aql.execute(aql))
    q3_stats = measure_execution(q3_3hop_filtered)
    print(f"[ArangoDB Q3 - 3-Hop Filtered] Time: {q3_stats['execution_time_sec']}s")

    # Q4: Complex Aggregation
    def q4_complex_agg():
        aql = "FOR u IN User FILTER u.id == 100 FOR b IN 1..1 OUTBOUND u FOLLOWS FOR c IN 1..1 OUTBOUND b FOLLOWS COLLECT name = c.name WITH COUNT INTO degree SORT degree DESC LIMIT 10 RETURN {name: name, degree: degree}"
        return list(db.aql.execute(aql))
    q4_stats = measure_execution(q4_complex_agg)
    print(f"[ArangoDB Q4 - Complex Aggregation] Time: {q4_stats['execution_time_sec']}s")

if __name__ == "__main__":
    run_arango_pipeline()
