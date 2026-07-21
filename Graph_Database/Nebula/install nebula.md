# Nebula Graph Setup Using Docker (Ubuntu)

## Prerequisites

- Ubuntu 20.04/22.04/24.04
- Docker installed
- Docker Compose installed

Verify installation:

```bash
docker --version
docker compose version
```

---

# Step 1: Create a Working Directory

```bash
mkdir ~/nebula
cd ~/nebula
```

---

# Step 2: Download the Official Docker Compose File

```bash
wget https://raw.githubusercontent.com/vesoft-inc/nebula-docker-compose/master/docker-compose-lite.yaml
```

---

# Step 3: Start Nebula Graph

```bash
sudo docker compose -f docker-compose-lite.yaml up -d
```

This downloads and starts:

- nebula-metad
- nebula-storaged
- nebula-graphd
- nebula-console

---

# Step 4: Check Running Containers

```bash
sudo docker ps
```

Expected output:

```
nebula-metad
nebula-storaged
nebula-graphd
nebula-console
```

---

# Step 5: Enter the Nebula Console

```bash
sudo docker exec -it nebula-console bash
```

---

# Step 6: Connect to Nebula Graph

```bash
nebula-console -addr graphd -port 9669 -u root -p nebula
```

Default credentials:

Username:

```
root
```

Password:

```
nebula
```

---

# Step 7: Verify Installation

```ngql
SHOW HOSTS;
```

If the services are running correctly, you'll see the status of the Meta, Storage, and Graph services.

---

# Step 8: Create a Space

```ngql
CREATE SPACE company(
    partition_num=5,
    replica_factor=1,
    vid_type=FIXED_STRING(20)
);
```

Use the space:

```ngql
USE company;
```

---

# Step 9: Create Employee Tag

```ngql
CREATE TAG Employee(
    name string,
    position string,
    department string,
    age int
);
```

---

# Step 10: Create Friend Edge

```ngql
CREATE EDGE Friend();
```

---

# Step 11: Insert Employees

```ngql
INSERT VERTEX Employee(name,position,department,age)
VALUES
"E1":("Alice","Developer","IT",25),
"E2":("Bob","Data Analyst","IT",27),
"E3":("Charlie","HR Manager","HR",35);
```

---

# Step 12: Create Relationships

```ngql
INSERT EDGE Friend()
VALUES
"E1"->"E2":(),
"E2"->"E3":();
```

---

# Step 13: Query Data

Show employees:

```ngql
MATCH (v:Employee)
RETURN v;
```

Show friendships:

```ngql
MATCH (v1)-[:Friend]->(v2)
RETURN v1,v2;
```

---

# Step 14: Stop Nebula Graph

```bash
sudo docker compose down
```

---

# Step 15: Start Again

```bash
sudo docker compose up -d
```

---

# Optional: Install NebulaGraph Studio (Visualization)

Run:

```bash
sudo docker run -d \
--name nebula-studio \
-p 7001:7001 \
vesoft/nebula-graph-studio:latest
```

Open:

```
http://localhost:7001
```

Connect using:

- Host: graphd
- Port: 9669
- Username: root
- Password: nebula

---

# Components

| Component | Purpose |
|----------|---------|
| nebula-metad | Metadata Service |
| nebula-storaged | Stores graph data |
| nebula-graphd | Query Service |
| nebula-console | Command Line Interface |
| NebulaGraph Studio | Web-based Visualization |


Now pull the corrected images and start the containers again.

### 1. Pull the images

```bash
sudo docker compose -f docker-compose-lite.yaml pull
```

If this completes successfully, continue.

---

### 2. Start Nebula Graph

```bash
sudo docker compose -f docker-compose-lite.yaml up -d
```

---

### 3. Check all containers

```bash
sudo docker ps
```

You should see something like:

```
nebula-metad0-1      Up (healthy)
nebula-storaged0-1   Up (healthy)
nebula-graphd-1      Up (healthy)
nebula-storage-activator-1
```

The important thing is **no `Restarting (139)`**.

---

### 4. Check the health

```bash
sudo docker ps --format "table {{.Names}}\t{{.Status}}"
```

---

### 5. If everything is healthy

Run:

```bash
sudo docker exec -it nebula-graphd-1 bash
```

Inside the container:

```bash
which nebula-console
```

If it returns a path, then run:

```bash
nebula-console -addr=127.0.0.1 -port=9669 -u=root -p=nebula
```

If `nebula-console` is not found, we'll use the dedicated console container instead.

---

## Please paste the outputs of only these two commands:

```bash
sudo docker compose -f docker-compose-lite.yaml pull
```

and

```bash
sudo docker ps --format "table {{.Names}}\t{{.Status}}"
```

From there, we'll connect to Nebula Graph and create your Employee graph.

# Problems Faced & Solutions

| Problem | Solution |
|---------|----------|
| Docker daemon was not running. | Started the Docker service using `sudo systemctl start docker`. |
| Permission denied while using Docker. | Added the user to the Docker group using `sudo usermod -aG docker $USER` and logged in again. |
| Docker was using the wrong context (`desktop-linux`). | Switched to the default Docker context using `docker context use default`. |
| Docker credential error (`docker-credential-desktop`). | Removed the old Docker Desktop configuration and created a new `~/.docker/config.json`. |
| Downloaded the wrong KuzuDB binary (`aarch64`) on an x86_64 machine. | Verified the system architecture using `uname -m` and downloaded the correct `x86_64` binary. |
| TigerGraph GSQL showed **"License is invalid"**. | Could not proceed with the Community Docker image. Switched focus to other graph databases. |
| Nebula Graph `metad` container kept restarting (`Restarting (139)`). | Replaced unstable `nightly` Docker images with the stable `v3.8.0` images. |
| `docker compose` showed **"no configuration file provided"**. | Used the correct compose file: `docker-compose-lite.yaml`. |
| `nebula-console` always connected to `127.0.0.1`. | Bypassed the container entrypoint and connected using a separate Nebula Console container. |
| `which` command was unavailable inside the container. | Used `find` and directly launched the required container instead. |
| Old laptop (Intel i5, limited RAM) could not efficiently run multiple graph databases simultaneously. | Installed Ubuntu in a dual-boot setup to reduce resource usage and improve Docker performance. |
| Several graph databases did not provide a free cloud environment. | Installed and tested them locally using Docker on Ubuntu. |

## Lessons Learned

- Verify the CPU architecture before downloading binaries.
- Prefer stable Docker image versions instead of `nightly` releases.
- Always verify Docker contexts and permissions before troubleshooting containers.
- Docker Compose file names must be specified if they are not named `docker-compose.yml`.
- Some graph databases provide only CLI tools, while others include browser-based visualization.
- Reading container logs (`docker logs`) is essential for diagnosing startup failures.