Unlike Neo4j, **NebulaGraph does not have an official VS Code extension for writing and executing nGQL queries**. The common workflow is:

* **VS Code** → Write `.ngql` or `.sql` query files.
* **Nebula Console** → Execute the queries.
* **Nebula Studio** → Visualize and manage the graph.
* **Python/Java SDKs** → Run queries from your application. ([docs.nebula-graph.io][1])

---

# Option 1: VS Code + Nebula Console (Recommended)

## Step 1. Install Docker Desktop

Install Docker Desktop if you don't already have it.

---

## Step 2. Start NebulaGraph

Create a folder:

```text
nebula-learning/
```

Inside it:

```text
nebula-learning/
│
├── queries/
├── datasets/
├── scripts/
└── docker-compose.yml
```

Download the official Docker Compose configuration or use the quick-start deployment from the NebulaGraph documentation. ([docs.nebula-graph.io][1])

Then start NebulaGraph:

```bash
docker compose up -d
```

This starts:

* Meta Service
* Graph Service
* Storage Service
* Nebula Console

([docs.nebula-graph.io][1])

---

## Step 3. Install VS Code Extensions

There isn't an official nGQL extension, but these are useful:

* SQL Language Support (syntax highlighting)
* Docker
* YAML
* Markdown
* GitLens (optional)

---

## Step 4. Create Query Files

Example:

```text
queries/
│
├── 01_create_space.ngql
├── 02_create_schema.ngql
├── 03_insert_data.ngql
├── 04_match.ngql
├── 05_go_queries.ngql
├── 06_lookup.ngql
└── 07_indexes.ngql
```

Example file:

```sql
CREATE SPACE demo(
    partition_num = 10,
    replica_factor = 1,
    vid_type = FIXED_STRING(32)
);

USE demo;

CREATE TAG Person(
    name string,
    age int
);

CREATE EDGE Friend(
    since int
);
```

---

## Step 5. Connect Using Nebula Console

Run:

```bash
docker exec -it nebula-console nebula-console \
-u root \
-p nebula \
--address graphd
```

(or connect to `127.0.0.1:9669` if you're using a local installation). ([docs.nebula-graph.io][1])

Now execute:

```sql
SOURCE queries/01_create_space.ngql
```

or simply copy and paste queries from VS Code into the console.

---

## Step 6. Install Nebula Studio (Optional)

Nebula Studio provides:

* Graph visualization
* Query editor
* Schema browser
* Import tools
* User management

Connect it to:

```text
Host: localhost
Port: 9669

Username: root
Password: nebula
```

---

# Option 2: VS Code + Python

Install the client:

```bash
pip install nebula3-python
```

Example:

```python
from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config

config = Config()
pool = ConnectionPool()

pool.init([("127.0.0.1", 9669)], config)

session = pool.get_session("root", "nebula")

result = session.execute("SHOW SPACES;")

print(result)

session.release()
pool.close()
```

This lets you keep all your code in VS Code while executing nGQL programmatically.

---

# Recommended Folder Structure

```text
NebulaGraph-Learning/
│
├── queries/
│   ├── 01_spaces.ngql
│   ├── 02_tags.ngql
│   ├── 03_edges.ngql
│   ├── 04_insert.ngql
│   ├── 05_fetch.ngql
│   ├── 06_lookup.ngql
│   ├── 07_match.ngql
│   ├── 08_go.ngql
│   ├── 09_update.ngql
│   ├── 10_indexes.ngql
│   └── 11_profile.ngql
│
├── datasets/
│   ├── people.csv
│   └── movies.csv
│
├── python/
│   ├── connect.py
│   ├── insert.py
│   └── query.py
│
├── notes/
│   └── roadmap.md
│
└── docker-compose.yml
```

This setup is close to the experience of working with SQL files in VS Code: you author your `.ngql` scripts in the editor, run them via **Nebula Console** or a client SDK, and use **Nebula Studio** for visualization and administration.

[1]: https://docs.nebula-graph.io/3.8.0/2.quick-start/1.quick-start-workflow/?utm_source=chatgpt.com "Deploy NebulaGraph using Docker - NebulaGraph Database Manual"
