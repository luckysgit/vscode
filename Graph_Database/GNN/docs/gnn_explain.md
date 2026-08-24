# Graph Neural Networks (GNN) & PyTorch Geometric (PyG): Comprehensive Technical Guide

Graph Representation Learning is designed to apply deep learning to non-Euclidean data structures. Unlike traditional deep learning models that process fixed 1D sequential data (text, audio) or regular 2D grids (images), Graph Neural Networks (GNNs) operate directly on topological structures with arbitrary sizes, irregular connectivity, and permutation symmetries.

---

## 1. Foundations of Graph Representation Learning

### 1.1 Mathematical Graph Representation

A graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ consists of:

* **Node/Vertex Set:** $\mathcal{V} = \{v_1, v_2, \dots, v_N\}$ with count $\vert{}\mathcal{V}\vert{} = N$.
* **Edge Set:** $\mathcal{E} \subseteq \mathcal{V} \times \mathcal{V}$ with count $\vert{}\mathcal{E}\vert{} = M$, where an edge $e_{ij} = (v_i, v_j)$ indicates a relationship from node $v_i$ to $v_j$.
* **Node Feature Matrix:** $X \in \mathbb{R}^{N \times F}$, where row $\mathbf{x}_v \in \mathbb{R}^F$ is the feature vector of node $v$.
* **Edge Feature Matrix:** $E \in \mathbb{R}^{M \times F_e}$, where $\mathbf{e}_{uv} \in \mathbb{R}^{F_e}$ contains attributes of the edge between $u$ and $v$.
* **Adjacency Matrix:** $A \in \{0, 1\}^{N \times N}$, where:

$$A_{uv} = \begin{cases} 1 & \text{if } (u, v) \in \mathcal{E} \\ 0 & \text{otherwise} \end{cases}$$


* **Degree Matrix:** $D \in \mathbb{R}^{N \times N}$, a diagonal matrix where $D_{vv} = \sum_{u} A_{vu} = \text{deg}(v)$ is the number of incident edges on node $v$.

```
Adjacency Matrix (A)           Graph Topology (V, E)
     1   2   3   4
1 [  0   1   1   0  ]               (1) ─────── (2)
2 [  1   0   1   1  ]                │  ╲        │
3 [  1   1   0   0  ]                │   ╲       │
4 [  0   1   0   0  ]               (3)   ───── (4)

```

---

### 1.2 Why Standard Neural Networks Fail on Graphs

```
┌───────────────────────────┬──────────────────────────────────────────────────────────────────────────┐
│ Architecture              │ Structural Failure Mode on Graphs                                        │
├───────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ **Standard MLP**          │ • Requires fixed input dimensions (graphs have variable node counts).    │
│                           │ • Not permutation invariant; changing node indices alters predictions.   │
│                           │ • Ignores relational connectivity and edge attributes entirely.          │
├───────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ **Convolutional (CNN)**   │ • Relies on shift-invariance across rigid, ordered Euclidean grids.      │
│                           │ • No natural "top", "bottom", "left", or "right" neighbors in a graph.  │
│                           │ • Neighborhood degrees vary across nodes (dynamic receptive fields).     │
└───────────────────────────┴──────────────────────────────────────────────────────────────────────────┘

```

#### Permutation Invariance vs. Permutation Equivariance

Let $P \in \{0, 1\}^{N \times N}$ be an arbitrary permutation matrix that reorders the node indexing.

* **Permutation Equivariance (Node-Level):** A node-level function $f(A, X)$ is equivariant if permuting the input graph permutes the output embeddings identically:

$$f(P A P^T, P X) = P f(A, X)$$


* **Permutation Invariance (Graph-Level):** A graph-level function $g(A, X)$ produces an identical scalar or global representation regardless of node ordering:

$$g(P A P^T, P X) = g(A, X)$$



---

## 2. The Message Passing Neural Network (MPNN) Framework

All modern spatial GNN layers operate via the **Message Passing** paradigm. For every layer $l \in \{1, \dots, L\}$, representation vectors $\mathbf{h}_v^{(l)}$ are updated through three deterministic steps:

```
                      Neighborhood: N(v)
                           ┌─────┐
                           │  u₁ │──┐
                           └─────┘  │
                           ┌─────┐  │  1. MESSAGE: m_uv = MSG(h_u, h_v, e_uv)
                           │  u₂ │──┼──────────────────────────────────────┐
                           └─────┘  │                                      │
                           ┌─────┐  │                                      ▼
                           │  u₃ │──┘                              ┌──────────────┐
                           └─────┘                                 │  AGGREGATE   │
                                                                   │ (Sum/Mean/Max│
                                                                   └──────────────┘
                                                                           │
                                                                    M_v    ▼
┌──────────────┐                                                   ┌──────────────┐
│  Target Node │ ─────────────────────────────────────────────────►│    UPDATE    │ ──► h_v^(l)
│    h_v^(l-1) │                                                   │  (MLP/GRU)   │
└──────────────┘                                                   └──────────────┘
                                2. UPDATE: h_v^(l) = UPDATE(h_v^(l-1), M_v)

```

### 2.1 The Three Core Steps

1. **Message Generation:**

$$\mathbf{m}_{uv}^{(l)} = \text{MSG}^{(l)}\left(\mathbf{h}_u^{(l-1)}, \mathbf{h}_v^{(l-1)}, \mathbf{e}_{uv}\right)$$



A parameterized function (often a linear layer or small MLP) that transforms the neighbor's state $\mathbf{h}_u^{(l-1)}$ and optional edge features $\mathbf{e}_{uv}$.
2. **Neighborhood Aggregation:**

$$\mathbf{M}_v^{(l)} = \bigoplus_{u \in \mathcal{N}(v)} \mathbf{m}_{uv}^{(l)}$$



The operator $\bigoplus$ must be a **symmetric, permutation-invariant** function:
* **$\text{SUM}$:** Captures full structural density, node degree, and scale differences.
* **$\text{MEAN}$:** Captures relative property distributions independent of node degree.
* **$\text{MAX}$:** Identifies the single most salient feature in the neighborhood.


3. **Node State Update:**

$$\mathbf{h}_v^{(l)} = \text{UPDATE}^{(l)}\left(\mathbf{h}_v^{(l-1)}, \mathbf{M}_v^{(l)}\right)$$



Combines the target node's prior representation $\mathbf{h}_v^{(l-1)}$ with the aggregated message $\mathbf{M}_v^{(l)}$ using a non-linear transformation (e.g., $\text{ReLU}$, $\text{PReLU}$, or a residual layer).

### 2.2 Receptive Field Expansion

With $L$ message-passing layers, the embedding $\mathbf{h}_v^{(L)}$ of node $v$ incorporates all structural information and features within its **$L$-hop local neighborhood**.

---

## 3. Major GNN Layer Architectures

```
                ┌─────────────────────────────────────────────────────────┐
                │                  GNN LAYER MECHANISMS                   │
                └─────────────────────────────────────────────────────────┘
                                             │
         ┌───────────────────────────────────┼──────────────────────────────────┐
         ▼                                   ▼                                  ▼
 ┌───────────────┐                   ┌───────────────┐                  ┌───────────────┐
 │      GCN      │                   │   GraphSAGE   │                  │      GAT      │
 ├───────────────┤                   ├───────────────┤                  ├───────────────┤
 │ Symmetric     │                   │ Neighborhood  │                  │ Self-Attention│
 │ Normalization │                   │ Sampling &    │                  │ Dynamic Edge  │
 │ Matrix Math   │                   │ Concatenation │                  │ Weighting     │
 └───────────────┘                   └───────────────┘                  └──────────────┘

```

### 3.1 Graph Convolutional Networks (GCN)

* **Introduced by:** Kipf & Welling (ICLR 2017).
* **Concept:** First-order localized spectral approximation of Chebyshev graph convolutions on graphs.
* **Mathematical Formulation (Matrix Form):**

$$H^{(l+1)} = \sigma\left( \widetilde{D}^{-\frac{1}{2}} \widetilde{A} \widetilde{D}^{-\frac{1}{2}} H^{(l)} W^{(l)} \right)$$



Where:
* $\widetilde{A} = A + I_N$ (Adjacency matrix augmented with self-loops).
* $\widetilde{D}_{ii} = \sum_{j} \widetilde{A}_{ij}$ (Augmented diagonal degree matrix).
* $\widetilde{D}^{-\frac{1}{2}} \widetilde{A} \widetilde{D}^{-\frac{1}{2}}$ applies **symmetric normalization**, preventing feature vectors from scaling up exponentially on high-degree hub nodes.
* $W^{(l)} \in \mathbb{R}^{F_{in} \times F_{out}}$ is a trainable weight matrix.
* $\sigma(\cdot)$ is an element-wise activation function ($\text{ReLU}$).


* **Node-wise Formulation:**

$$\mathbf{h}_v^{(l+1)} = \sigma\left( W^{(l)} \sum_{u \in \mathcal{N}(v) \cup \{v\}} \frac{1}{\sqrt{\tilde{d}_v \tilde{d}_u}} \mathbf{h}_u^{(l)} \right)$$



---

### 3.2 GraphSAGE (Sample and Aggregate)

* **Introduced by:** Hamilton, Ying, & Leskovec (NeurIPS 2017).
* **Core Innovation:** **Inductive representation learning**. Instead of computing over the full adjacency matrix (transductive), it samples a fixed number of neighbors ($S_k$) and trains aggregators.
* **Mathematical Formulation:**

$$\mathbf{h}_{\mathcal{N}(v)}^{(l)} = \text{AGGREGATE}_k\left( \left\{ \mathbf{h}_u^{(l-1)}, \forall u \in \mathcal{N}(v) \right\} \right)$$


$$\mathbf{h}_v^{(l)} = \sigma\left( W^{(l)} \cdot \left[ \mathbf{h}_v^{(l-1)} \,\Vert{}\, \mathbf{h}_{\mathcal{N}(v)}^{(l)} \right] \right)$$



Where:
* $\Vert{}$ denotes vector concatenation.
* $\text{AGGREGATE}_k$ can be `MeanAggregator`, `LSTMAggregator`, or `PoolAggregator` ($\max(\sigma(W_{pool}\mathbf{h}_u + b))$).



---

### 3.3 Graph Attention Networks (GAT / GATv2)

* **Introduced by:** Veličković et al. (ICLR 2018).
* **Core Innovation:** Replaces fixed, degree-based weights with **learnable self-attention coefficients**, dynamically assigning importance to different neighbors.

```
       Node u  (h_u) ────────► [ W · h_u ] ──┐
                                             ├──► [ a^T (Wh_v || Wh_u) ] ──► Softmax ──► Attention Weight α_vu
       Node v  (h_v) ────────► [ W · h_v ] ──┘

```

* **Attention Weight Formulation:**

$$\alpha_{vu} = \frac{\exp\left(\text{LeakyReLU}\left(\mathbf{a}^T \left[ W \mathbf{h}_v \,\Vert{}\, W \mathbf{h}_u \right]\right)\right)}{\sum_{k \in \mathcal{N}(v)} \exp\left(\text{LeakyReLU}\left(\mathbf{a}^T \left[ W \mathbf{h}_v \,\Vert{}\, W \mathbf{h}_k \right]\right)\right)}$$


* **Multi-Head Attention Update (with $K$ heads):**

$$\mathbf{h}_v^{(l+1)} = \sigma\left( \frac{1}{K} \sum_{k=1}^K \sum_{u \in \mathcal{N}(v)} \alpha_{vu}^k W^k \mathbf{h}_u^{(l)} \right)$$



---

### Architecture Comparison

| Model | Aggregation Type | Normalization | Inductive? | Edge Feature Support | Complexity per Node |
| --- | --- | --- | --- | --- | --- |
| **GCN** | Sum / Mean | Symmetric $(\sqrt{d_u d_v})^{-1}$ | Limited | Indirect | $\mathcal{O}(\vert{}\mathcal{E}\vert{} \cdot F)$ |
| **GraphSAGE** | Mean / Pool / LSTM | L2 / Batch Normalization | **Yes** | No | $\mathcal{O}\left(\prod_{l=1}^L S_l \cdot F\right)$ |
| **GAT** | Weighted Attention | Softmax coefficients | **Yes** | Yes (via GATv2) | $\mathcal{O}(\vert{}\mathcal{V}\vert{} \cdot F^2 + \vert{}\mathcal{E}\vert{} \cdot F)$ |

---

## 4. Downstream Prediction Tasks & Global Pooling

```
                        ┌───────────────────────────────────────────────┐
                        │              GNN PREDICTION TASKS             │
                        └───────────────────────────────────────────────┘
                                                │
         ┌──────────────────────────────────────┼──────────────────────────────────────┐
         ▼                                      ▼                                      ▼
┌──────────────────┐                  ┌──────────────────┐                  ┌──────────────────┐
│    Node Level    │                  │    Edge Level    │                  │   Graph Level    │
├──────────────────┤                  ├──────────────────┤                  ├──────────────────┤
│ Classify nodes   │                  │ Predict missing  │                  │ Classify/regress │
│ h_v^(L) -> MLP   │                  │ links or weights │                  │ entire topology  │
│ e.g., Fraud ID   │                  │ [h_u || h_v]     │                  │ Pool({h_v})      │
└──────────────────┘                  └──────────────────┘                  └──────────────────┘

```

### 4.1 Node Classification

* Target label $y_v$ exists for individual nodes.
* **Formula:** $\hat{y}_v = \text{Softmax}\left(\text{MLP}\left(\mathbf{h}_v^{(L)}\right)\right)$
* **Applications:** Financial fraud detection, bot account detection, document subject tagging.

### 4.2 Link Prediction / Edge Classification

* Predicts whether an edge $(u, v)$ exists or its scalar value.
* **Formula:** $\hat{y}_{uv} = \sigma\left(\text{MLP}\left(\left[\mathbf{h}_u^{(L)} \,\Vert{}\, \mathbf{h}_v^{(L)}\right]\right)\right) \quad \text{or} \quad \hat{y}_{uv} = \sigma\left(\mathbf{h}_u^{(L)T} \cdot \mathbf{h}_v^{(L)}\right)$
* **Applications:** Recommendation engines, drug-target interaction, knowledge graph completion.

### 4.3 Graph Classification & Regression (Readout Phase)

* Computes a single compact vector $\mathbf{h}_{\mathcal{G}}$ representing the whole graph $\mathcal{G}$.

#### Global Pooling Operations (Readout)

$$\mathbf{h}_{\mathcal{G}} = \text{READOUT}\left(\left\{\mathbf{h}_v^{(L)} \mid v \in \mathcal{V}\right\}\right)$$

1. **Global Mean Pooling (GAP):**

$$\mathbf{h}_{\mathcal{G}} = \frac{1}{N} \sum_{v \in \mathcal{V}} \mathbf{h}_v^{(L)}$$


2. **Global Max Pooling (GMP):**

$$\mathbf{h}_{\mathcal{G}} = \max_{v \in \mathcal{V}} \left(\mathbf{h}_v^{(L)}\right)$$


3. **Multi-scale Pooling (Best Practice):** Concatenating GAP and GMP retains both the overall statistical distribution and extreme property signals:

$$\mathbf{h}_{\mathcal{G}} = \left[ \text{GAP}(\{\mathbf{h}_v\}) \,\Vert{}\, \text{GMP}(\{\mathbf{h}_v\}) \right]$$



---

## 5. PyTorch Geometric (PyG) Core Abstractions

### 5.1 The `torch_geometric.data.Data` Object

A single graph in PyG is encapsulated in a `Data` instance:

* `data.x`: Node feature matrix of shape `[num_nodes, num_node_features]`.
* `data.edge_index`: Graph connectivity in **Coordinate List (COO)** format of shape `[2, num_edges]` with dtype `torch.long`.
* `data.edge_attr`: Edge feature tensor of shape `[num_edges, num_edge_features]`.
* `data.y`: Ground-truth targets of shape `[num_nodes, *]` or `[1, *]`.

```
COO Sparse Edge Representation:

Source Nodes (Row 0): [ 0,  1,  1,  2,  3 ]
Target Nodes (Row 1): [ 1,  0,  2,  1,  0 ]

Shape: [2, num_edges]

```

---

### 5.2 Mini-Batching via Block-Diagonal Adjacency

PyG stacks multiple graphs into a single giant disconnected graph:

```text
Adjacency Matrix Batch (A_batch):
┌──────────┬──────────┬──────────┐
│   A₁     │    0     │    0     │
├──────────┼──────────┼──────────┤
│    0     │   A₂     │    0     │
├──────────┼──────────┼──────────┤
│    0     │    0     │   A₃     │
└──────────┴──────────┴──────────┘

```

* `batch` tensor: Vector of shape `[total_num_nodes]` mapping every node to its graph index:

$$\text{batch} = [0, 0, 0, 1, 1, 2, 2, 2, 2]^T$$


* This design allows parallel matrix operations across GPUs without zero-padding overhead.

---

## 6. End-to-End PyTorch Geometric Implementation Blueprint

The following standalone, production-ready script implements a multi-layer GNN for graph-level property prediction (e.g., molecule regression on ESOL/QM9).

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import Data, DataLoader
from torch_geometric.nn import GCNConv, SAGEConv, global_mean_pool, global_max_pool

# ==============================================================================
# 1. MODEL ARCHITECTURE DEFINITION
# ==============================================================================
class AdvancedGraphRegressor(torch.nn.Module):
    """
    Multi-layer Graph Neural Network architecture featuring:
    - SAGEConv layers for inductive representation learning
    - Non-linear activations with Dropout regularization
    - Dual Readout (Mean + Max Global Pooling)
    - Multi-Layer Perceptron (MLP) prediction head
    """
    def __init__(self, num_node_features: int, hidden_dim: int = 64, output_dim: int = 1):
        super(AdvancedGraphRegressor, self).__init__()
        
        # Message Passing Convolutional Layers
        self.conv1 = SAGEConv(num_node_features, hidden_dim)
        self.conv2 = SAGEConv(hidden_dim, hidden_dim)
        self.conv3 = SAGEConv(hidden_dim, hidden_dim)
        
        # Batch Normalization Layers for stabilized gradient flow
        self.bn1 = nn.BatchNorm1d(hidden_dim)
        self.bn2 = nn.BatchNorm1d(hidden_dim)
        self.bn3 = nn.BatchNorm1d(hidden_dim)
        
        # Linear MLP Head (hidden_dim * 2 due to GAP + GMP concatenation)
        self.fc1 = nn.Linear(hidden_dim * 2, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, output_dim)
        
        self.dropout = nn.Dropout(p=0.2)

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor, batch: torch.Tensor) -> torch.Tensor:
        # --- Layer 1 ---
        h = self.conv1(x, edge_index)
        h = self.bn1(h)
        h = F.relu(h)
        h = self.dropout(h)
        
        # --- Layer 2 ---
        h = self.conv2(h, edge_index)
        h = self.bn2(h)
        h = F.relu(h)
        h = self.dropout(h)
        
        # --- Layer 3 ---
        h = self.conv3(h, edge_index)
        h = self.bn3(h)
        h = F.relu(h)
        
        # --- Global Pooling (Readout Phase) ---
        # Aggregate node features into graph-level vector
        h_mean = global_mean_pool(h, batch)  # [batch_size, hidden_dim]
        h_max = global_max_pool(h, batch)    # [batch_size, hidden_dim]
        h_graph = torch.cat([h_mean, h_max], dim=1)  # [batch_size, hidden_dim * 2]
        
        # --- Prediction MLP ---
        out = F.relu(self.fc1(h_graph))
        out = self.dropout(out)
        out = self.fc2(out)
        return out


# ==============================================================================
# 2. SYNTHETIC DATA GENERATION & PIPELINE DEMONSTRATION
# ==============================================================================
def generate_synthetic_molecular_dataset(num_graphs: int = 128):
    """Creates synthetic molecules (random graphs) for demonstration."""
    dataset = []
    for _ in range(num_graphs):
        num_nodes = torch.randint(8, 24, (1,)).item()
        
        # Node attributes (e.g., 9 chemical atom properties)
        x = torch.randn((num_nodes, 9), dtype=torch.float)
        
        # Generate random undirected COO edges
        num_edges = torch.randint(num_nodes, num_nodes * 2, (1,)).item()
        src = torch.randint(0, num_nodes, (num_edges,))
        dst = torch.randint(0, num_nodes, (num_edges,))
        
        # Ensure undirected graph
        edge_index = torch.stack([torch.cat([src, dst]), torch.cat([dst, src])], dim=0)
        
        # Target continuous scalar value (e.g., solubility score)
        y = torch.tensor([[torch.randn(1).item()]], dtype=torch.float)
        
        data = Data(x=x, edge_index=edge_index, y=y)
        dataset.append(data)
    return dataset


# ==============================================================================
# 3. TRAINING & EVALUATION LOOP
# ==============================================================================
if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Executing GNN Pipeline on Device: {device}")
    
    # 1. Dataset & DataLoader Setup
    full_dataset = generate_synthetic_molecular_dataset(num_graphs=200)
    train_dataset = full_dataset[:160]
    test_dataset = full_dataset[160:]
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    # 2. Model, Optimizer, Loss Function
    model = AdvancedGraphRegressor(num_node_features=9, hidden_dim=64, output_dim=1).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)
    criterion = nn.MSELoss()
    
    # 3. Training Execution
    model.train()
    print("\nStarting GNN Training...")
    for epoch in range(1, 21):
        total_loss = 0.0
        for batch_data in train_loader:
            batch_data = batch_data.to(device)
            optimizer.zero_grad()
            
            # Forward pass
            predictions = model(batch_data.x, batch_data.edge_index, batch_data.batch)
            loss = criterion(predictions, batch_data.y)
            
            # Backpropagation
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * batch_data.num_graphs
            
        epoch_loss = total_loss / len(train_dataset)
        if epoch % 5 == 0 or epoch == 1:
            print(f"Epoch [{epoch:02d}/20] | Train Loss (MSE): {epoch_loss:.4f}")
            
    # 4. Evaluation
    model.eval()
    test_loss = 0.0
    with torch.no_grad():
        for batch_data in test_loader:
            batch_data = batch_data.to(device)
            preds = model(batch_data.x, batch_data.edge_index, batch_data.batch)
            loss = criterion(preds, batch_data.y)
            test_loss += loss.item() * batch_data.num_graphs
            
    print(f"\nFinal Test Set MSE Loss: {test_loss / len(test_dataset):.4f}")

```

---

## 7. Diagnostics & Advanced Engineering Considerations

```
┌───────────────────────────┬──────────────────────────────────────────────────────────────────────────┐
│ Phenomenon                │ Root Cause & Mitigation Strategy                                         │
├───────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ **Over-smoothing**        │ • **Cause:** Stacking too many layers ($L > 4$) causes all node vectors  │
│                           │   to converge to a uniform average due to repeated averaging.            │
│                           │ • **Remedy:** Use residual skip connections, Jump Knowledge Networks     │
│                           │   (`JumpingKnowledge`), LayerNorm, or keep layers between 2–4.           │
├───────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ **Over-squashing**        │ • **Cause:** Exponentially growing neighborhood information compressed   │
│                           │   into a fixed-size vector bottleneck during multi-hop message passing.  │
│                           │ • **Remedy:** Graph rewiring, Edge Dropout, or Graph Transformer layers. │
├───────────────────────────┼──────────────────────────────────────────────────────────────────────────┤
│ **Scalability to Big Data**│ • **Cause:** Full-graph training cannot fit into single-GPU memory.     │
│                           │ • **Remedy:** Subgraph sampling algorithms (`NeighborLoader`,            │
│                           │   `ClusterGCN`, `GraphSAINT`).                                           │
└───────────────────────────┴──────────────────────────────────────────────────────────────────────────┘

```

---

### Summary Checklist for GNN Projects

1. **Define the Task:** Identify if the problem is **Node-level** (no pooling needed), **Edge-level** (pairwise embedding computation), or **Graph-level** (global pooling required).
2. **Choose the Message Passing Layer:**
* Baseline Homogeneous Graphs: `GCNConv`.
* Inductive / Large-scale Data: `SAGEConv`.
* Edge Features / Attention Weights: `GATv2Conv`.


3. **Prevent Over-smoothing:** Restrict layer depth to 2–4 message-passing steps unless using explicit residual connections.
4. **Pool Strategically:** Combine mean pooling and max pooling to capture both background graph statistics and outlier signals.