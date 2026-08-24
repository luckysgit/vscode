| Architecture Family | Primary Data Modality | Key Mechanism / Innovation | Dominant Use Cases |
| --- | --- | --- | --- |
| **Perceptron / MLP / FNN** | Tabular, Structured, Dense | Fixed non-linear activations on nodes via matrix dot-products | Baselines, classification, regression |
| **Radial Basis Function (RBFN)** | Tabular, Function Approximations | Distance-based Gaussian kernel activations around centroids | Curve fitting, non-linear system control |
| **Hopfield / Boltzmann / EBM** | Associative Memory, Binary/Spin States | Energy surface minimization & attractor convergence dynamics | Pattern completion, associative memory |
| **Self-Organizing Maps (SOM)** | High-Dimensional Features | Competitive unsupervised learning preserving topological neighborhoods | Unsupervised clustering, data visualization |
| **CNN (ResNet, ConvNeXt)** | Spatial 2D/3D (Images, Video) | Convolutional kernels, translation invariance & parameter sharing | Computer vision, object detection, segmentation |
| **Capsule Networks (CapsNet)** | Spatial / Hierarchical Vision | Vector capsules & dynamic routing preserving spatial pose/hierarchy | Viewpoint-invariant image classification |
| **RNN / LSTM / GRU** | 1D Sequential, Time Series | Recurrent hidden states with input/forget/output gating loops | Time-series forecasting, audio modeling |
| **Echo State Networks (ESN / Reservoir)** | Dynamic Time Series | Untrained fixed recurrent reservoir with trainable linear readout | Low-cost chaotic time-series forecasting |
| **Transformer (Encoder / Decoder)** | Text, Code, Multimodal | Scaled dot-product self-attention & multi-head routing | LLMs, foundational models, translation |
| **Vision Transformer (ViT / Swin)** | Visual Patches, 2D/3D Images | Patch tokenization with global/windowed self-attention | SOTA computer vision, segmentation |
| **Multi-Head Latent Attention (MLA)** | Long-Context Text, Code | Low-rank joint compression of Keys & Values during generation | Massive KV-cache reduction in frontier LLMs |
| **Autoencoder (AE / VAE / VQ-VAE)** | Latent Codes, Audio, Images | Encoder-decoder bottleneck compression & discrete codebooks | Representation learning, anomaly detection, neural codecs |
| **Generative Adversarial Net (GAN)** | High-Fidelity Synthesis | Minimax game between a Generator and Discriminator | Image-to-image translation, style transfer |
| **Graph Neural Network (GNN / GAT)** | Relational Graphs, Non-Euclidean | Neighborhood message passing & topological feature aggregation | Molecular chemistry, drug discovery, fraud detection |
| **Graph Transformer** | Complex Graph Structures | Global node attention combined with structural/positional encodings | Molecular property prediction, protein folding |
| **Diffusion & Flow Matching** | Generative Visual, Video, Audio | Iterative score matching, ODE-based rectified flow velocity integration | SOTA text-to-image (Flux), video generation |
| **Diffusion Transformers (DiT)** | Multimodal Generative Tokens | Replaces standard U-Net backbones with Transformer blocks for diffusion | Scalable high-fidelity text-to-image/video generation |
| **State Space Models (SSMs / Mamba)** | Long Sequences, Genomics, Audio | Continuous dynamical system discretization with selective gating | Linear $\mathcal{O}(N)$ sequence modeling |
| **Hybrid Attention-SSM (Jamba / Samba)** | Ultra-Long Context Text | Interleaves Transformer attention layers with Mamba SSM layers | Combines exact retrieval precision with linear throughput |
| **xLSTM ($sLSTM$ / $mLSTM$)** | Sequences, Financial Streams | Exponential gating stabilization with matrix-valued memory storage | Scalable non-transformer recurrent modeling |
| **Liquid Neural Networks (LNN / CfC)** | Continuous Streams, Robotics | Adaptive, dynamic time-constants via closed-form differential equations | Autonomous navigation, edge robotics |
| **Kolmogorov-Arnold Network (KAN)** | Scientific Data, Symbolic Functions | Learnable B-spline univariate activations placed directly on network edges | Interpretable AI, symbolic regression, physics discovery |
| **Neural ODEs / Normalizing Flows** | Irregular Time Series, Continuous Densities | Continuous-depth layer integration via adaptive numerical ODE solvers | Trajectory modeling, continuous generative flows |
| **Neural Operators (FNO / DeepONet)** | Continuous Partial Differential Equations | Infinite-dimensional mapping between function spaces via Fourier transforms | Zero-shot climate modeling, aerodynamic simulation |
| **Physics-Informed NNs (PINNs)** | Physical Systems, Engineering | Enforces conservation laws & PDEs directly inside backpropagation loss | Fluid dynamics, material stress analysis |
| **Neural Radiance Fields (NeRF / 3DGS)** | Spatial 3D / Novel Viewpoints | Coordinate MLP implicit fields & 3D Gaussian primitive rasterization | Real-time 3D scene capture, VR reconstruction |
| **Spiking Neural Network (SNN)** | Event-Driven Neuromorphic Data | Discrete, temporal binary spike trains mimicking biological action potentials | Ultra-low-power edge processors (Loihi, BrainScaleS) |
| **World Models & JEPA (I-JEPA / V-JEPA)** | Video, Embodied Perception, Agents | Self-supervised prediction in abstract latent space (no pixel reconstruction) | Autonomous robotics, agent planning |
| **HyperNetworks** | Meta-Learning, Neural Compression | A primary network generating the dynamic weight matrices for a secondary network | Fast domain adaptation, personalized models |
| **Test-Time Training (TTT / TTT-Linear)** | Ultra-Long Sequences ($>2\text{M}$ tokens) | Replaces hidden state with a neural network updated via test-time gradient descent | Linear-complexity sequence modeling with expressive memory |
| **Titans (Neural Long-Term Memory)** | Massive Context Sequences | Combines core short-term attention with an adaptive neural long-term memory module | Long-horizon reasoning, continual context retention |
| **Mixture of Experts (MoE / Fine-Grained MoE)** | Sparse Multimodal / Language | Top-$k$ conditional gating routing tokens to specialized feedforward sub-networks | Massive parameter scaling with low compute overhead |
| **1-Bit / Ternary Networks (BitNet b1.58)** | Low-Bit Quantized Language/Edge | Replaces FP16 matrix multiplications with ternary $\{-1, 0, 1\}$ integer additions | Ultra-efficient CPU/NPU inference without GPU multipliers |
| **Multi-Token Prediction Architectures (MTP)** | Autoregressive Text / Code | Multi-head decoder paths predicting $n$ future tokens simultaneously per step | Faster training signal efficiency and speculative decoding |
| **Continuous-Time Diffusion / Rectified Flow** | Continuous Vector Trajectories | Straightens probability flow paths between noise and data distributions | Sub-step high-speed image & video generation |
| **Geometric Deep Learning / Equivariant NNs** | 3D Molecular, Atomic, Manifolds | Incorporates group symmetry constraints (SO(3), SE(3), E(n) equivariance) | Crystal structure prediction, material discovery |
| **Optoelectronic / Photonic Neural Networks** | Optical Waveguide Data | Performs linear matrix multiplications via light interference at the speed of light | Sub-nanosecond latency, zero-thermal compute hardware |