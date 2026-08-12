The problem is that you're in the **Linux bash shell**, not the **TigerGraph GSQL shell**.

When you typed:

```bash
CREATE VERTEX Employee (...)
```

Bash tried to execute it as a Linux command, which is why you got:

```text
bash: syntax error near unexpected token '('
```

## Step 1: Start GSQL

Inside the container, run:

```bash
gsql
```

If TigerGraph is running, you'll see something like:

```text
GSQL >
```

Only there can you execute GSQL commands.

---

## Step 2: If `gsql` doesn't work

Run:

```bash
gadmin status
```

If the services are not running, start them:

```bash
gadmin start
```

Wait 1–2 minutes, then check again:

```bash
gadmin status
```

---

## Step 3: Create the schema

After you see:

```text
GSQL >
```

Run:

```gsql
CREATE VERTEX Employee (
  PRIMARY_ID id STRING,
  name STRING,
  position STRING,
  department STRING,
  age INT
)
```

Then:

```gsql
CREATE DIRECTED EDGE Friend (
  FROM Employee,
  TO Employee
)
```

Then:

```gsql
CREATE GRAPH CompanyGraph(Employee, Friend)
```

---

### First, tell me the output of these commands:

```bash
gadmin status

gsql
```

This will confirm whether the TigerGraph services are running and whether you're in the correct shell.


### TigerGraph

- Docker image installed successfully.
- GSQL could not be used because the downloaded image requires a valid TigerGraph license.
- Therefore, practical execution and screenshots could not be completed locally.