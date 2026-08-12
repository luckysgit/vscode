I found the problem. ✅

Your laptop is:

```text
Architecture: x86_64 (Intel/AMD)
Ubuntu: 24.04 LTS
```

But you downloaded:

```text
kuzu_cli-linux-aarch64.tar.gz
```

That package is for **ARM CPUs**, so it cannot run on your Intel/AMD laptop.

## 1. Delete the wrong file

```bash
rm kuzu_cli-linux-aarch64.tar.gz
```

## 2. Download the correct version

```bash
cd ~/Downloads
wget https://github.com/kuzudb/kuzu/releases/latest/download/kuzu_cli-linux-x86_64.tar.gz
```

If `wget` is not installed:

```bash
sudo apt update
sudo apt install wget
```

## 3. Extract it

```bash
tar -xzf kuzu_cli-linux-x86_64.tar.gz
```

## 4. Check what was extracted

```bash
ls -lh
```

You should see something like:

```
kuzu
LICENSE
README.md
```

## 5. Make it executable (if needed)

```bash
chmod +x kuzu
```

## 6. Run it

```bash
./kuzu
```

You should see something like:

```
KuzuDB Shell
>
```

---

## If it still doesn't run

Run these commands and paste the output:

```bash
cd ~/Downloads

ls -lh

file kuzu

./kuzu
```

We'll diagnose it from there.

**One more thing:** You previously tried to download the `x86_64` version but got `curl: command not found`. That message is unusual because the second `curl` command worked. If `wget` also fails or the downloaded file isn't correct, we'll investigate that next.


-----------------------------EXAMPLE--------------------------------------------------

Once you start Kuzu, you'll see the prompt:

```text
KuzuDB Shell
>
```

Now you can execute Cypher queries.

---

# Step 1: Create a Database

```cypher
CREATE NODE TABLE Employee(
    id INT64,
    name STRING,
    position STRING,
    department STRING,
    PRIMARY KEY(id)
);
```

---

# Step 2: Insert Employees

```cypher
CREATE (:Employee {
    id:1,
    name:"Alice",
    position:"Software Engineer",
    department:"IT"
});

CREATE (:Employee {
    id:2,
    name:"Bob",
    position:"Data Analyst",
    department:"IT"
});

CREATE (:Employee {
    id:3,
    name:"Charlie",
    position:"HR Manager",
    department:"HR"
});

CREATE (:Employee {
    id:4,
    name:"David",
    position:"Finance Manager",
    department:"Finance"
});

CREATE (:Employee {
    id:5,
    name:"Emma",
    position:"Marketing Executive",
    department:"Marketing"
});
```

---

# Step 3: Create a Relationship Table

```cypher
CREATE REL TABLE FRIEND(
    FROM Employee TO Employee
);
```

---

# Step 4: Add Friend Relationships

```cypher
MATCH (a:Employee {id:1}), (b:Employee {id:2})
CREATE (a)-[:FRIEND]->(b);

MATCH (a:Employee {id:2}), (b:Employee {id:3})
CREATE (a)-[:FRIEND]->(b);

MATCH (a:Employee {id:3}), (b:Employee {id:4})
CREATE (a)-[:FRIEND]->(b);

MATCH (a:Employee {id:4}), (b:Employee {id:5})
CREATE (a)-[:FRIEND]->(b);
```

---

# Step 5: View All Employees

```cypher
MATCH (e:Employee)
RETURN e;
```

Output:

```text
Alice
Bob
Charlie
David
Emma
```

---

# Step 6: Find IT Employees

```cypher
MATCH (e:Employee)
WHERE e.department = "IT"
RETURN e.name, e.position;
```

Output:

```text
Alice   Software Engineer
Bob     Data Analyst
```

---

# Step 7: Show Friends

```cypher
MATCH (a:Employee)-[:FRIEND]->(b:Employee)
RETURN a.name, b.name;
```

Output:

```text
Alice    Bob
Bob      Charlie
Charlie  David
David    Emma
```

---

# Step 8: Find Alice's Friends

```cypher
MATCH (a:Employee {name:"Alice"})-[:FRIEND]->(b)
RETURN b.name;
```

Output:

```text
Bob
```

---

# Step 9: Count Employees

```cypher
MATCH (e:Employee)
RETURN COUNT(e);
```

Output:

```text
5
```

---

## If you get an error saying `CREATE NODE TABLE` is not recognized

Please tell me:

```bash
./kuzu --version
```

or, once inside Kuzu:

```cypher
CALL VERSION();
```

Kuzu's syntax has changed across versions, so I'll provide the exact commands that match your installed version.
