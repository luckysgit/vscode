Here is an architectural breakdown of the five major Graph Neural Network (GNN [Graph Neural Network]) paradigms: **GCN**, **GraphSAGE**, **GAT**, **GIN**, and **Graph Transformer**.

---

### 1. GCN (Graph Convolutional Network [Graph Convolutional Network])

**Core Idea:** An isotropic, spectral-inspired spatial convolution that updates node embeddings by averaging normalized neighbor features.

```
       (u₁)
         ╲
  (u₂) ── (v) ── (u₃)   ===>  Averages features of u₁, u₂, u₃ + v using
         ╱                    fixed degree-based symmetric weights.
       (u₄)

```

* **Aggregation Mechanism:** Uses fixed, structural normalization based on node degrees. Every neighbor's contribution is scaled inversely by the square root of the product of the node degrees.
* **Mathematical Formula:**

$$H^{(l+1)} = \sigma\left(\widetilde{D}^{-\frac{1}{2}} \widetilde{A} \widetilde{D}^{-\frac{1}{2}} H^{(l)} W^{(l)}\right)$$


$$\mathbf{h}_v^{(l+1)} = \sigma\left( \sum_{u \in \mathcal{N}(v) \cup \{v\}} \frac{1}{\sqrt{\tilde{d}_v \tilde{d}_u}} \mathbf{h}_u^{(l)} W^{(l)} \right)$$



*Where $\widetilde{A} = A + I_N$ (adjacency with self-loops), $\widetilde{D}$ is the diagonal degree matrix, and $W^{(l)}$ is a trainable weight matrix.*
* **Key Properties:**
* **Isotropic:** Treats all incident edges symmetrically based solely on node degrees.
* **Transductive Origin:** Originally designed for full-graph Laplacian operations on a fixed graph structure.
* **Limitation:** Susceptible to over-smoothing when stacked beyond 3–4 layers.



---

### 2. GraphSAGE (Sample and Aggregate [Sample and Aggregate])

**Core Idea:** An inductive framework that enables scalable mini-batch training by sampling a fixed-size local neighborhood and concatenating self-features with aggregated neighborhood features.

```
Step 1: Sample k neighbors randomly ──► Step 2: Aggregate (Mean/Pool/LSTM) ──► Step 3: Concat [h_v || h_N(v)]

```

* **Aggregation Mechanism:** Separates the target node's own state from its neighborhood. It applies a flexible aggregator ($\text{Mean}$, $\text{Max-Pooling}$, or $\text{LSTM}$ [Long Short-Term Memory]) over sampled neighbors, followed by concatenation.
* **Mathematical Formula:**

$$\mathbf{h}_{\mathcal{N}(v)}^{(l+1)} = \text{AGGREGATE}^{(l+1)}\left( \left\{ \mathbf{h}_u^{(l)}, \forall u \in \mathcal{N}_{\text{sampled}}(v) \right\} \right)$$


$$\mathbf{h}_v^{(l+1)} = \sigma\left( W^{(l+1)} \cdot \left[ \mathbf{h}_v^{(l)} \,\Vert{}\, \mathbf{h}_{\mathcal{N}(v)}^{(l+1)} \right] \right)$$


* **Key Properties:**
* **Inductive Generalization:** Can generate embeddings for unseen nodes and new subgraphs at test time without retraining.
* **Scalability:** Neighbor sampling bounds memory consumption, enabling training on massive graphs via mini-batching.
* **Limitation:** Uniform neighbor sampling can miss rare but critical structural paths.



---

### 3. GAT (Graph Attention Network [Graph Attention Network])

**Core Idea:** An anisotropic convolution that dynamically computes attention weights over neighbor edges, learning which neighbors matter more.

```
Node v (h_v) ──┐
               ├──► Attention Coefficient e_vu ──► Softmax (α_vu) ──► Weighted Sum
Node u (h_u) ──┘

```

* **Aggregation Mechanism:** Computes pairwise self-attention coefficients $\alpha_{vu}$ between node $v$ and its neighbors $u \in \mathcal{N}(v)$, using multi-head attention to stabilize learning.
* **Mathematical Formula:**

$$\alpha_{vu} = \frac{\exp\left(\text{LeakyReLU}\left(\mathbf{a}^T \left[ W \mathbf{h}_v \,\Vert{}\, W \mathbf{h}_u \right]\right)\right)}{\sum_{k \in \mathcal{N}(v)} \exp\left(\text{LeakyReLU}\left(\mathbf{a}^T \left[ W \mathbf{h}_v \,\Vert{}\, W \mathbf{h}_k \right]\right)\right)}$$


$$\mathbf{h}_v^{(l+1)} = \sigma\left( \frac{1}{K} \sum_{k=1}^K \sum_{u \in \mathcal{N}(v)} \alpha_{vu}^k W^k \mathbf{h}_u^{(l)} \right)$$


* **Key Properties:**
* **Anisotropic:** Assigns dynamic, data-driven edge importance rather than relying on static graph degrees.
* **Edge Interpretability:** Learned attention coefficients highlight high-impact connections.
* **Limitation:** Computationally more expensive than GCN ($\mathcal{O}(\vert{}\mathcal{V}\vert{}F^2 + \vert{}\mathcal{E}\vert{}F)$).



---

### 4. GIN (Graph Isomorphism Network [Graph Isomorphism Network])

**Core Idea:** A maximally expressive spatial GNN designed to match the power of the 1-WL (1-Weisfeiler-Lehman [1-Weisfeiler-Lehman]) graph isomorphism test for distinguishing non-isomorphic graph structures.

```
       (u₁)
         ╲           Sum Aggregator (Injective)
  (u₂) ── (v)  ===>  h_sum = ∑ h_u
         ╱           h_v^(l+1) = MLP( (1 + ε) · h_v + h_sum )
       (u₃)

```

* **Aggregation Mechanism:** Replaces mean/max aggregators with an **injective sum aggregation** and a universal multi-layer perceptron (MLP [Multi-Layer Perceptron]). Mean and max aggregators lose structural multiset information (e.g., distinguishing between 2 identical neighbors vs. 10 identical neighbors), whereas sum preserves it.
* **Mathematical Formula:**

$$\mathbf{h}_v^{(l+1)} = \text{MLP}^{(l+1)}\left( \left(1 + \epsilon^{(l+1)}\right) \mathbf{h}_v^{(l)} + \sum_{u \in \mathcal{N}(v)} \mathbf{h}_u^{(l)} \right)$$



*Where $\epsilon$ is a learnable or fixed scalar parameter.*
* **Key Properties:**
* **Theoretical Upper Bound:** Provably the most expressive message-passing architecture within the 1-WL framework.
* **Graph-Level Superiority:** Highly effective for whole-graph classification (e.g., molecular property prediction, bio-informatics).
* **Limitation:** Sensitive to degree variations and graph scale when node feature diversity is low.



---

### 5. Graph Transformer (Graph Transformer [Graph Transformer])

**Core Idea:** Replaces local $k$-hop message passing with **global, all-to-all Self-Attention**, enhanced with spatial, structural, and positional graph encodings.

```
[ Traditional GNN (Local MPNN) ]              [ Graph Transformer (Global Attention) ]
    (1) ─── (2) ─── (3) ─── (4)                    (1) ◄───────────────► (4)
     └─ Step 1   └─ Step 2  (3 hops)                 └── Direct Attention in 1 step ──┘

```

* **Aggregation Mechanism:** Every node attends to every other node in the graph ($\mathcal{O}(N^2)$ global connectivity). Graph topology is injected into the attention matrix via biases:
1. **Laplacian PE (Positional Encodings [Positional Encodings]):** Injects spectral coordinate embeddings.
2. **Spatial Distance Bias:** Adds a penalty/bias proportional to the Shortest Path Distance ($\text{SPD}$) between node $i$ and node $j$.
3. **Edge Feature Bias:** Directly embeds edge properties along the path into the attention computation.


* **Mathematical Formula:**

$$A_{ij} = \frac{\left(\mathbf{h}_i W_Q\right)\left(\mathbf{h}_j W_K\right)^T}{\sqrt{d_k}} + b_{\text{SPD}(i,j)} + c_{e_{ij}}$$


$$\mathbf{h}_i^{(l+1)} = \text{Softmax}_j\left(A_{ij}\right) \left(\mathbf{h}_j W_V\right)$$


* **Key Properties:**
* **Eliminates Over-Squashing:** Connects distant nodes directly in a single step ($\mathcal{O}(1)$ path length), preventing information bottlenecks.
* **Long-Range Modeling:** Excels at capturing long-distance dependencies across large graphs.
* **Limitation:** Full global self-attention scales quadratically ($\mathcal{O}(N^2)$), requiring sparse attention or linear approximations on large graphs.



---

### Summary Comparison

| Model | Neighborhood Scope | Edge Weights | Expressive Power | Primary Strength |
| --- | --- | --- | --- | --- |
| **GCN** | Local (1-hop) | Static (Degree-normalized) | Sub-1-WL | Lightweight, efficient baseline |
| **GraphSAGE** | Sampled Local ($k$-hop) | Learnable Aggregators | Sub-1-WL | Inductive scaling on massive graphs |
| **GAT** | Local (1-hop) | Dynamic (Learned Attention) | Sub-1-WL | Adaptive edge weighting, interpretability |
| **GIN** | Local (1-hop) | Injective Sum + MLP | **Equal to 1-WL** | Provably maximal spatial expressiveness |
| **Graph Transformer** | **Global (All-to-All)** | Global Attention + Graph Biases | **Beyond 1-WL** | Solves over-squashing & long-range paths |