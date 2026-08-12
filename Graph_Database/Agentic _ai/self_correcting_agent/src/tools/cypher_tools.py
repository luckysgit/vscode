from src.database.neo4j_client import db_client

def graph_cypher_traversal(entity_name: str) -> str:
    try:
        with db_client.driver.session() as session:
            res = session.run("""
            MATCH (d:Document)-[:BELONGS_TO]->(c:Category)
            WHERE toLower(d.text) CONTAINS toLower($entity) OR toLower(c.name) CONTAINS toLower($entity)
            RETURN d.text AS doc, c.name AS category
            """, entity=entity_name)
            results = [f"Doc: {r['doc']} | Category: {r['category']}" for r in res]
            return "\n".join(results) if results else f"NO GRAPH MATCHES for '{entity_name}'. FALLBACK REQUIRED: Call 'vector_index_search'."
    except Exception as e:
        return f"Database error: {str(e)}"
