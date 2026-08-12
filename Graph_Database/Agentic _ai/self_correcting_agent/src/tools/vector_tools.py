from src.database.neo4j_client import db_client

def vector_index_search(query: str) -> str:
    try:
        query_vec = db_client.embedder.encode(query).tolist()
        with db_client.driver.session() as session:
            res = session.run("""
            CALL db.index.vector.queryNodes('document_embeddings', 2, $query_vec)
            YIELD node AS doc, score
            RETURN doc.text AS text, score
            """, query_vec=query_vec)
            results = [f"- {r['text']} (score: {round(r['score'], 2)})" for r in res]
            return "\n".join(results) if results else "No vector matches found."
    except Exception as e:
        return f"Database error: {str(e)}"
