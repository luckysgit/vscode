-----------------------------------------------------------------------------

# Creating Nodes & Relationships Across Graph Query Languages

Below are code examples for creating two nodes (`Person` and `Company`) and a `WORKS_AT` relationship between them across the major graph query languages.

---

## 1. Cypher / openCypher
*(Used by: Neo4j, FalkorDB, Memgraph, KuzuDB, TuGraph, Amazon Neptune)*

```cypher
// Create Person node, Company node, and the WORKS_AT relationship
CREATE (p:Person {name: 'Alice', age: 30})
CREATE (c:Company {name: 'Acme Corp'})
CREATE (p)-[:WORKS_AT {role: 'Engineer'}]->(c);

```

---

## 2. AQL (ArangoDB Query Language)

*(Used by: ArangoDB)*

> **Note:** ArangoDB stores nodes in **Document Collections** and relationships in **Edge Collections**.

```aql
// 1. Insert Person Node
INSERT { _key: "alice", name: "Alice", age: 30 } 
INTO Persons

// 2. Insert Company Node
INSERT { _key: "acme", name: "Acme Corp" } 
INTO Companies

// 3. Insert Relationship (Edge connecting the documents via _id)
INSERT { 
  _from: "Persons/alice", 
  _to: "Companies/acme", 
  role: "Engineer" 
} 
INTO WorksAt

```

---

## 3. Gremlin

*(Used by: Amazon Neptune)*

```groovy
// Add Person node, Company node, and connect them with an edge
g.addV('Person').property('name', 'Alice').property('age', 30).as('p')
 .addV('Company').property('name', 'Acme Corp').as('c')
 .addE('WORKS_AT').from('p').to('c').property('role', 'Engineer')

```

---

## 4. SPARQL

*(Used by: Amazon Neptune)*

```sparql
PREFIX ex: [http://example.org/](http://example.org/)
PREFIX rdf: [http://www.w3.org/1999/02/22-rdf-syntax-ns#](http://www.w3.org/1999/02/22-rdf-syntax-ns#)

INSERT DATA {
  # Create Alice (Person)
  ex:Alice rdf:type ex:Person ;
           ex:name "Alice" ;
           ex:age 30 .

  # Create Acme Corp (Company)
  ex:AcmeCorp rdf:type ex:Company ;
              ex:name "Acme Corp" .

  # Create Relationship
  ex:Alice ex:worksAt ex:AcmeCorp .
}

```

---

## 5. GSQL

*(Used by: TigerGraph)*

```gsql
# Insert vertices (nodes) and edges (relationships)
INSERT INTO Person VALUES ("p1", "Alice", 30);
INSERT INTO Company VALUES ("c1", "Acme Corp");
INSERT INTO WORKS_AT VALUES ("p1" Person, "c1" Company, "Engineer");

```

---

## 6. DQL (Dgraph Query Language)

*(Used by: Dgraph)*

```json
{
  "set": [
    {
      "uid": "_:alice",
      "dgraph.type": "Person",
      "name": "Alice",
      "age": 30,
      "works_at": {
        "uid": "_:acme",
        "dgraph.type": "Company",
        "name": "Acme Corp"
      }
    }
  ]
}

```

---

## 7. nGQL (NebulaGraph Query Language)

*(Used by: NebulaGraph)*

```ngql
-- 1. Insert Vertices (Nodes)
INSERT VERTEX Person(name, age) VALUES "person1":("Alice", 30);
INSERT VERTEX Company(name) VALUES "company1":("Acme Corp");

-- 2. Insert Edge (Relationship)
INSERT EDGE WORKS_AT(role) VALUES "person1" -> "company1":("Engineer");

