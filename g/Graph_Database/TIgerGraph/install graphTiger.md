Since you're using **Ubuntu 24.04** and your laptop is old, there are two ways to install TigerGraph.

## Option 1: TigerGraph Docker (Recommended)

TigerGraph officially recommends Docker.

### Step 1: Install Docker

```bash
sudo apt update
sudo apt install docker.io -y
```

Start Docker:

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

Verify:

```bash
docker --version
```

---

### Step 2: Pull TigerGraph

```bash
docker pull tigergraph/tigergraph
```

---

### Step 3: Run TigerGraph

```bash
docker run -d \
  --name tigergraph \
  -p 9000:9000 \
  -p 14240:14240 \
  tigergraph/tigergraph
```

---

### Step 4: Open Browser

```
http://localhost:14240
```

This opens **GraphStudio**.

---

## Option 2: TigerGraph Cloud (No Installation)

TigerGraph also offers a cloud service.

1. Visit:

   * [TigerGraph Cloud](https://www.tigergraph.com/cloud/?utm_source=chatgpt.com)
2. Sign up.
3. Create a free/trial instance (availability may vary).
4. Open GraphStudio in your browser.

---

## Official Documentation

* [TigerGraph Documentation](https://docs.tigergraph.com/?utm_source=chatgpt.com)
* [TigerGraph Docker Guide](https://docs.tigergraph.com/tigergraph-server/current/installation/docker/?utm_source=chatgpt.com)

---

## ⚠️ For your laptop

You mentioned earlier that your laptop **struggles with Docker**, which is why you installed Ubuntu. Keep in mind that:

* **TigerGraph is resource-intensive.**
* It generally works best with **at least 8 GB RAM** (16 GB recommended for a smoother experience).

-----------------------------------------------
Excellent! 🎉 Docker is working, and **TigerGraph has been downloaded successfully**.

Now let's run the container.

## Step 1: Start TigerGraph

```bash
sudo docker run -d \
  --name tigergraph \
  -p 9000:9000 \
  -p 14240:14240 \
  tigergraph/tigergraph
```

Check if it's running:

```bash
sudo docker ps
```

You should see a container named **tigergraph**.

---

## Step 2: Enter the container

```bash
sudo docker exec -it tigergraph bash
```

You'll get a prompt like:

```text
root@xxxxxxxx:/#
```

---

## Step 3: Check TigerGraph status

Inside the container, run:

```bash
gadmin status
```

If it's not started, run:

```bash
gadmin start
```

Wait 1–2 minutes, then check again:

```bash
gadmin status
```

---

## Step 4: Open GraphStudio

On your Ubuntu machine, open your browser and visit:

```text
http://localhost:14240
```

or, if that doesn't work:

```text
http://127.0.0.1:14240
```

---

## Step 5: Login

The default credentials are commonly:

```text
Username: tigergraph
Password: tigergraph
```

If those don't work, let me know the image version and we'll check the initialized credentials.

---

## Step 6: Verify the container logs

If GraphStudio doesn't open, run:

```bash
sudo docker logs tigergraph
```

---

### Let's do this step by step.

Run these commands:

```bash
sudo docker run -d \
  --name tigergraph \
  -p 9000:9000 \
  -p 14240:14240 \
  tigergraph/tigergraph

sudo docker ps
```

Then paste the output. We'll verify the container is healthy before opening GraphStudio.
