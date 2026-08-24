
## The Complete GNN Learning Roadmap

```
Level 1: Prerequisites & Foundations
├── 1.1 Graph Theory Fundamentals
├── 1.2 Linear Algebra & Spectral Basics
└── 1.3 Machine Learning Foundations

Level 2: Core GNN Mechanics
├── 2.1 The Message Passing Framework (MPNN)
├── 2.2 Classic Spatial Architectures
└── 2.3 Classic Spectral Architectures

Level 3: Operational Mechanics & Training
├── 3.1 Downstream Tasks & Readout Functions
├── 3.2 Graph Pooling (Coarsening)
└── 3.3 Theoretical & Practical Challenges

Level 4: Advanced Architectures & Scaling
├── 4.1 Scaling to Massive Graphs
├── 4.2 Beyond 1-WL Expressive Power
├── 4.3 Specialized Graph Data Models
└── 4.4 Graph Transformers & Self-Supervised Learning

Level 5: Practical Tooling & Real-World Systems
├── 5.1 Libraries & Benchmarks
└── 5.2 Production Deployment Domains

```

---

## Level 1: Prerequisites & Foundations

### 1.1 Graph Theory Fundamentals

* **1.1.1 Graph Types & Taxonomy**
* Undirected vs. Directed Graphs
* Homogeneous vs. Heterogeneous Graphs
* Bipartite Graphs & Knowledge Graphs


* **1.1.2 Matrix Representations of Graphs**
* Adjacency Matrix ($A \in \mathbb{R}^{N \times N}$)
* Node Feature Matrix ($X \in \mathbb{R}^{N \times d}$)
* Degree Matrix ($D$) and Incidence Matrix
* Edge Indices and Edge Feature Tensors ($E$)


* **1.1.3 Graph Properties**
* Homophily vs. Heterophily (Assortativity)
* Node Centrality (Degree, Betweenness, Eigenvector)
* Clustering Coefficients & Connectivity



### 1.2 Linear Algebra & Spectral Basics

* **1.2.1 Graph Laplacians**
* Unnormalized Laplacian: $L = D - A$
* Symmetric Normalized Laplacian: $L_{sym} = D^{-\frac{1}{2}} L D^{-\frac{1}{2}} = I - D^{-\frac{1}{2}} A D^{-\frac{1}{2}}$
* Random Walk Laplacian: $L_{rw} = D^{-1} L$


* **1.2.2 Eigen-Decomposition & Spectral Theory**
* Eigenvalues ($\lambda$) and Eigenvectors ($U$) of the Graph Laplacian
* Smoothness of signals on graphs
* Graph Fourier Transform ($\hat{x} = U^T x$)



### 1.3 Machine Learning Foundations

* **1.3.1 Core Deep Learning**
* Multi-Layer Perceptrons (MLPs), Convolutions (CNNs), and Self-Attention (Transformers)


* **1.3.2 Structural Symmetries**
* Permutation Invariance: $f(P \cdot X, P \cdot A \cdot P^T) = f(X, A)$
* Permutation Equivariance: $f(P \cdot X, P \cdot A \cdot P^T) = P \cdot f(X, A)$



---

## Level 2: Core GNN Mechanics

### 2.1 The Message-Passing Paradigm (MPNN)

* **2.1.1 The Tripartite Operational Step**
* **Message:** $m_{u \to v}^{(l)} = \text{MSG}\left(h_u^{(l-1)}, h_v^{(l-1)}, e_{uv}\right)$
* **Aggregation:** $m_v^{(l)} = \text{AGG}\left(\{ m_{u \to v}^{(l)} \mid u \in \mathcal{N}(v) \}\right)$
* **Update:** $h_v^{(l)} = \text{UPDATE}\left(h_v^{(l-1)}, m_v^{(l)}\right)$


* **2.1.2 Permutation Invariant Aggregators**
* Sum Aggregator (preserves multiset counts)
* Mean Aggregator (captures feature distribution)
* Max Aggregator (captures extreme values/salient features)


* **2.1.3 Neighborhood Expansion & Receptive Fields**
* 1-hop vs. $k$-hop computational graphs



### 2.2 Classic Spatial GNN Architectures

* **2.2.1 Graph Convolutional Network (GCN)**
* Symmetric degree normalization ($\tilde{D}^{-\frac{1}{2}} \tilde{A} \tilde{D}^{-\frac{1}{2}}$)
* Renormalization trick & self-loop addition


* **2.2.2 Graph Attention Network (GAT / GATv2)**
* Dynamic edge weighting using self-attention ($\alpha_{ij}$)
* Multi-head attention mechanisms on graph neighborhoods


* **2.2.3 GraphSAGE (Sample and Aggregate)**
* Inductive learning on unseen graphs
* Uniform neighborhood sampling
* Aggregator variations (LSTM, Pooling, Mean)


* **2.2.4 Graph Isomorphism Network (GIN)**
* Injective multiset aggregation
* Reaching the theoretical upper bound of the 1-WL graph isomorphism test



### 2.3 Classic Spectral GNN Architectures

* **2.3.1 Spectral Graph Convolutions**
* Filtering graph signals in the spectral domain ($g_\theta \star x = U g_\theta U^T x$)


* **2.3.2 ChebNet**
* Truncated Chebyshev polynomial approximation to avoid expensive $O(N^3)$ eigen-decomposition


* **2.3.3 Derivation of GCN from ChebNet**
* First-order local approximation simplifying spectral theory into 1-hop spatial convolutions



---

## Level 3: Operational Mechanics & Training

### 3.1 Downstream Tasks & Formulations

* **3.1.1 Node-Level Tasks** (e.g., Fraud detection, user profiling)
* Softmax / BCE heads over final node embeddings $h_v^{(L)}$


* **3.1.2 Link-Level Tasks** (e.g., Recommender systems, Knowledge Graph completion)
* Edge scoring functions: Inner product $h_u^T h_v$, Bilinear forms $h_u^T W h_v$, MLPs
* Negative sampling strategies


* **3.1.3 Graph-Level Tasks** (e.g., Molecule toxicity prediction, protein classification)
* Readout / Global Pooling functions



### 3.2 Graph Pooling (Hierarchical Representation Learning)

* **3.2.1 Global Pooling**
* `Global Sum`, `Global Mean`, `Global Max`


* **3.2.2 Hierarchical Node Reduction / Coarsening**
* **DiffPool:** Differentiable soft cluster assignment matrices
* **Top-$k$ Pooling / SAGPool:** Self-attention based node selection and graph reduction



### 3.3 Theoretical & Practical Training Challenges

* **3.3.1 Over-smoothing**
* Node representations collapse into uniform vectors when stacking too many layers ($L > 4$)
* *Mitigations:* Residual connections, Initial Residuals (GCNII), Jumping Knowledge (JK-Net)


* **3.3.2 Over-squashing & Structural Bottlenecks**
* Exponential information compression from $k$-hop neighborhoods into fixed-size vectors
* *Mitigations:* Ricci curvature re-wiring, Fully Connected Layers / Global Nodes


* **3.3.3 Heterophily Handling**
* When connected nodes belong to different categories (violating standard GCN smooth assumptions)
* *Mitigations:* Separating ego-embedding from neighbor-embeddings, non-local aggregations



---

## Level 4: Advanced Architectures & Scaling

### 4.1 Scaling GNNs to Industrial Web-Scale Graphs

* **4.1.1 Node & Layer Sampling Methods**
* **GraphSAGE:** Fixed-size node neighborhood sampling
* **FastGCN:** Layer-wise importance sampling


* **4.1.2 Graph Subgraph Partitioning Methods**
* **Cluster-GCN:** Clustering graphs into sub-communities via METIS
* **GraphSAINT:** Random-walk based subgraph extraction


* **4.1.3 Decoupled / Linear GNNs**
* **SGC (Simple Graph Convolution):** Removing non-linearities between layers
* **SIGN & APPNP:** Pre-computing feature propagation matrices before neural network layers



### 4.2 Expressive Power Beyond 1-WL

* **4.2.1 Weisfeiler-Lehman (WL) Hierarchy**
* Understanding $1\text{-WL} \le 2\text{-WL} = 3\text{-WL} < k\text{-WL}$ limits


* **4.2.2 Subgraph GNNs & Distance Encodings**
* Ego-network decomposition & relative distance features


* **4.2.3 High-Order Topological Networks**
* Simplicial Complexes & Cellular Complexes (calculating features over edges, triangles, and rings)



### 4.3 Specialized Graph Structure Paradigms

* **4.3.1 Heterogeneous Graph Neural Networks**
* Relational GCN (R-GCN) for multiple edge types
* Heterogeneous Attention Network (HAN) using Meta-paths
* Heterogeneous Graph Transformer (HGT)


* **4.3.2 Dynamic & Temporal Graph Networks**
* Continuous-Time Dynamic Graphs (TGN, DyREP)
* Discrete-Time Dynamic Graphs (EvolveGCN, ST-GCN)


* **4.3.3 Geometric & Equivariant GNNs**
* $E(n)$ and $SE(3)$ Equivariant Networks (EGNN, SchNet) for 3D atomic structures and molecular docking



### 4.4 Graph Transformers & Self-Supervised Frontiers

* **4.4.1 Positional & Structural Encodings (PE / SE)**
* Laplacian Positional Encodings (LapPE)
* Random Walk Structural Encodings (RWSE)


* **4.4.2 Global Graph Transformers**
* **Graphormer / GPS Architecture:** Combining local message passing with global full-graph multi-head self-attention


* **4.4.3 Self-Supervised Learning & Graph RAG**
* Graph Contrastive Learning (GraphCL) & Masked Autoencoders (GraphMAE)
* Knowledge Graphs integrated with Large Language Models (Graph RAG)



---

## Level 5: Practical Tooling & Real-World Systems

### 5.1 Libraries & Benchmarks

* **5.1.1 Frameworks:** PyTorch Geometric (PyG), Deep Graph Library (DGL)
* **5.1.2 Standard Datasets:** Cora, Citeseer, PubMed, TU Datasets
* **5.1.3 Industrial Benchmarks:** Open Graph Benchmark (OGB & OGB-LSC)

### 5.2 Key Industry Applications

* **5.2.1 Life Sciences:** Drug discovery, molecular property prediction, protein folding (AlphaFold)
* **5.2.2 Recommender Systems:** PinSage (Pinterest), User-item graph filtering
* **5.2.3 Financial Intelligence:** Anti-Money Laundering (AML), fraud ring detection
* **5.2.4 Physical Simulations:** Particle dynamics, traffic forecasting (Google Maps ETA)

---