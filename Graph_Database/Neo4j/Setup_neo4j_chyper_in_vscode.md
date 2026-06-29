You have two options for using Neo4j in VS Code:

## Option 1: Neo4j VS Code Extension (Recommended)

Install the official Neo4j extension in VS Code. It provides:

* Cypher syntax highlighting
* Auto-completion
* Query execution
* Connection management
* Query result visualization
* Linting and error checking for Cypher files ([marketplace.visualstudio.com][1])

### Step 1: Install Neo4j

Either:

* Download and install [Neo4j Desktop](https://neo4j.com/download/?utm_source=chatgpt.com)
* Or create a free cloud database using [Neo4j AuraDB](https://neo4j.com/cloud/aura/?utm_source=chatgpt.com)

### Step 2: Install VS Code Extension

Open VS Code:

```text
Extensions (Ctrl+Shift+X)
```

Search:

```text
Neo4j
```

Install:

```text
Neo4j for VS Code
```

Or see the extension page:

[Neo4j for VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=neo4j-extensions.neo4j-for-vscode&utm_source=chatgpt.com)

### Step 3: Create a Cypher File

Create:

```text
practice.cypher
```

Example:

```cypher
CREATE (p:Person {name:'John', age:25});

MATCH (p:Person)
RETURN p;
```

The extension recognizes `.cypher` files automatically. ([marketplace.visualstudio.com][1])

### Step 4: Connect to Database

Open Command Palette:

```text
Ctrl + Shift + P
```

Run:

```text
Neo4j: Add Connection
```

Enter:

```text
URI: bolt://localhost:7687

Username: neo4j

Password: your_password
```

For AuraDB:

```text
neo4j+s://xxxxxxxx.databases.neo4j.io
```

The extension supports managing and switching connections directly inside VS Code. ([Graph Database & Analytics][2])

### Step 5: Run Queries

Execute query:

```text
Ctrl + Enter
```

Run selected/all queries:

```text
Ctrl + Alt + Enter
```

Results appear inside VS Code. ([marketplace.visualstudio.com][1])

---

## Option 2: Neo4j Docker + VS Code

If you're comfortable with Docker:

```bash
docker run \
--name neo4j \
-p7474:7474 \
-p7687:7687 \
-e NEO4J_AUTH=neo4j/password \
neo4j
```

Open:

```text
http://localhost:7474
```

Then connect VS Code extension to:

```text
bolt://localhost:7687
```

---

## Recommended Folder Structure

```text
neo4j-learning/
│
├── queries/
│   ├── create.cypher
│   ├── match.cypher
│   ├── relationships.cypher
│   ├── aggregation.cypher
│   └── optimization.cypher
│
├── datasets/
│   ├── people.csv
│   └── movies.csv
│
└── notes/
    └── cypher-roadmap.md
```

## First Queries to Practice

```cypher
CREATE (:Person {name:'Alice'});
```

```cypher
MATCH (p:Person)
RETURN p;
```

```cypher
MATCH (p:Person)
WHERE p.name = 'Alice'
RETURN p;
```

```cypher
CREATE
(a:Person {name:'Alice'}),
(b:
```

[1]: https://marketplace.visualstudio.com/items?itemName=neo4j-extensions.neo4j-for-vscode&utm_source=chatgpt.com "Neo4j for VS Code - Visual Studio Marketplace"
[2]: https://neo4j.com/developer-blog/run-cypher-without-leaving-your-ide-with-neo4j-vscode-extension/?utm_source=chatgpt.com "Run Cypher in Your IDE with Neo4j VSCode Extension"
