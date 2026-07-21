Great! Let's move to **TuGraph**.

Since you've already installed Docker and successfully ran Nebula Graph, TuGraph will be much easier.

---

# Step 1: Pull the TuGraph Image

```bash
sudo docker pull tugraph/tugraph-runtime-centos7:latest
```

Check if the image is downloaded:

```bash
sudo docker images
```

---

# Step 2: Run TuGraph

```bash
sudo docker run -d \
  --name tugraph \
  -p 7070:7070 \
  -p 7687:7687 \
  tugraph/tugraph-runtime-centos7:latest
```

Check the container:

```bash
sudo docker ps
```

---

# Step 3: Check Logs

```bash
sudo docker logs tugraph
```

Wait until you see something similar to:

```
Server started
HTTP server started
Bolt server started
```

---

# Step 4: Open TuGraph Browser

Open your browser:

```
http://localhost:7070
```

Login with the default credentials (if unchanged):

```
Username: admin
Password: 73@TuGraph
```

If those don't work, we'll inspect the logs or reset the password.

---

# Step 5: Run Cypher

TuGraph supports **Cypher**, so you can execute queries in the browser just like Neo4j.

---

## If Port 7070 Doesn't Open

Run:

```bash
sudo docker ps
```

Then:

```bash
sudo docker logs tugraph
```

---

## Visualization

✅ Yes, TuGraph provides a **web UI** where you can:

* Execute Cypher queries
* Browse nodes and edges
* Visualize the graph
* Export results
* Take screenshots for your comparison report

---

## If the Docker Image Fails

There are two official images:

```bash
tugraph/tugraph-runtime-centos7:latest
```

or

```bash
tugraph/tugraph-db:latest
```

We'll use whichever works with your system.

---

### We'll proceed like we did for Nebula Graph:

1. ✅ Install
2. ✅ Start Docker container
3. ✅ Open Web UI
4. ✅ Create Employee graph
5. ✅ Run Cypher queries
6. ✅ Visualize graph
7. ✅ Prepare your comparison screenshots

**Run Step 1 (`docker pull tugraph/tugraph-runtime-centos7:latest`) and share the output.** If that image isn't available or fails, I'll provide the correct current image.
