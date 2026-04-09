"""Fallback/Demo mode with mock data for when LLM is rate-limited."""

MOCK_CONCEPTS = {
    "transformer": [
        "Attention Mechanism",
        "Multi-Head Attention",
        "Positional Encoding",
        "Feed-Forward Networks",
        "Layer Normalization"
    ],
    "retrieval augmented": [
        "Vector Database",
        "Semantic Search",
        "Text Embedding",
        "Retrieval Pipeline",
        "Context Augmentation"
    ],
    "federated learning": [
        "Distributed Training",
        "Privacy Preservation",
        "Model Aggregation",
        "Communication Efficiency",
        "Data Heterogeneity"
    ],
    "quantum computing": [
        "Quantum Gates",
        "Superposition",
        "Entanglement",
        "Quantum Circuits",
        "Error Correction"
    ],
    "graph neural": [
        "Graph Convolution",
        "Node Embeddings",
        "Message Passing",
        "Graph Attention",
        "Spectral Methods"
    ]
}

MOCK_CONCLUSIONS = {
    "Attention is All You Need": "Transformer architecture achieving SOTA on translation tasks with parallel computation.",
    "RoBERTa: A Robustly Optimized BERT": "Improved BERT pretraining achieves better downstream task performance.",
    "BERT: Pre-training of Deep": "Self-supervised learning on large corpora improves transfer learning capabilities.",
    "GPT: Language Models are Unsupervised": "Large-scale unsupervised language modeling enables few-shot learning.",
    "Vision Transformer": "Pure transformer architecture applied to vision tasks matches/exceeds CNN performance.",
}

MOCK_CONTRADICTIONS = [
    {
        "theme": "Model Size Efficiency",
        "paper_a": "Attention is All You Need",
        "claim_a": "Larger models with more parameters achieve better performance",
        "paper_b": "DistilBERT: Smaller Model Faster",
        "claim_b": "Smaller distilled models can match performance with lower latency"
    },
    {
        "theme": "Positional Encoding Methods",
        "paper_a": "Attention is All You Need",
        "claim_a": "Absolute positional encoding is sufficient",
        "paper_b": "RoFormer",
        "claim_b": "Relative positional encoding captures relationships better"
    },
    {
        "theme": "Fine-tuning vs Few-shot",
        "paper_a": "BERT: Pre-training",
        "claim_a": "Task-specific fine-tuning is necessary",
        "paper_b": "Language Models are Few-shot Learners",
        "claim_b": "Large models can learn from prompts without fine-tuning"
    }
]

MOCK_REPORT = """
# Literature Review: Transformer Models

## 1. Introduction & Methodological Trends

The field of Transformer-based neural networks has evolved significantly since the introduction of the Attention Mechanism in 2017. Key methodological trends include:

- **Model Size Scaling**: Progressive increase from 110M (BERT) to 70B+ parameters (LLaMA, Claude)
- **Architectural Innovations**: Addition of memory mechanisms, sparse attention, and positional encoding variants
- **Training Paradigm Shifts**: From supervised fine-tuning to in-context learning and prompt-based approaches
- **Efficiency Focus**: Knowledge distillation, quantization, and pruning to reduce computational costs

## 2. Key Debates & Contradictions

### Debate 1: Model Size vs Efficiency
- **Position A**: Larger models inherently capture more knowledge (GPT-3, Claude)
- **Position B**: Well-optimized smaller models can match performance with less compute (DistilBERT, MobileBERT)
- **Resolution**: Both are valid depending on use case. Large models excel at few-shot learning; small models optimize for inference.

### Debate 2: Fixed vs Learned Positional Encoding
- **Position A**: Sinusoidal positional encoding captures relationship distances well
- **Position B**: Learnable positional embeddings adapt to specific tasks
- **Resolution**: Relative positional encodings (RoFormer, ALiBi) show superior generalization

### Debate 3: Supervised Fine-tuning vs In-Context Learning
- **Position A**: Task-specific fine-tuning is essential for performance (BERT era)
- **Position B**: Large models can learn from context without updating parameters (GPT-3+)
- **Resolution**: Scale is key. Larger models enable in-context learning; smaller models benefit from fine-tuning

## 3. Research Gaps & Next Frontiers

### Gap 1: Interpretability of Attention Distributions
- **Current Status**: Limited understanding of which attention heads capture meaningful relationships
- **Proposed Approach**: Systematic study of attention pattern specialization across layers and heads
- **Impact**: Could lead to more efficient architectures through learned pruning

### Gap 2: Efficiency-Performance Tradeoff
- **Current Status**: No theoretical framework for optimal model-size-to-performance mapping
- **Proposed Approach**: Systematic analysis across diverse tasks and compute budgets
- **Impact**: Enable faster deployment on resource-constrained devices

### Gap 3: Robustness to Distribution Shift
- **Current Status**: Transformers are brittle to adversarial examples and out-of-distribution inputs
- **Proposed Approach**: Incorporate uncertainty quantification and robust pretraining objectives
- **Impact**: Enable deployment in safety-critical domains

## 4. Limitations and Blind Spots (Critical Analysis)

The current consensus overlooks several important factors:

1. **Environmental Impact**: Training and inference costs are rarely discussed relative to model scales
2. **Data Quality Bias**: Heavy reliance on Web-scale data introduces demographic and cultural biases
3. **Context Window Limitations**: Models struggle with truly long-range dependencies despite theoretical ability
4. **Theoretical Understanding**: Lacking principled understanding of *why* attention works so well
5. **Domain Generalization**: Strong performance on NLP doesn't guarantee success in other modalities

## 5. Next Steps Research Proposal

### Proposed Investigation: "Adaptive Transformers for Resource-Constrained Environments"

**Research Question**: Can we develop a framework for automatically determining optimal Transformer configurations (size, depth, width) for a given compute budget and task?

**Methodology**:
1. Create a diverse benchmark of 50+ NLP and multimodal tasks
2. Train Transformers with varying configurations using budget constraints
3. Build a predictive model mapping task characteristics + budget → optimal config
4. Validate on held-out tasks

**Expected Outcomes**:
- Universal scaling laws for Transformers
- Automated architecture search for resource-constrained deployment
- 40-60% reduction in computational requirements for target performance levels

**Budget Justification**:
- GPU-hours for benchmark training: ~500K GPU-hours
- Personnel: 2-3 researchers for 18 months
- Estimated cost: $400K-600K

**Impact**:
- Enable Transformer deployment on edge devices
- Reduce carbon footprint of model deployment
- Create reproducible framework for industry resource planning

---

*This review covers 47 papers published between 2017-2025 across ArXiv, papers with 50+ citations.*
"""

MOCK_GRANT_PROPOSAL = """
## Grant Proposal: Advancing Transformer Efficiency

### Executive Summary
This proposal seeks funding to investigate the theoretical underpinnings of Transformer efficiency and develop practical frameworks for deploying these models in resource-constrained environments.

### Research Objectives
1. Establish universal scaling laws for Transformers across task domains
2. Develop automated methods for selecting optimal model configurations
3. Create practical tools for practitioners to make deployment decisions

### Timeline & Milestones
- Months 1-3: Benchmark construction and baseline experiments
- Months 4-9: Large-scale training experiments
- Months 10-15: Framework development and validation
- Months 16-18: Publication and tool release

### Expected Impact
- Democratize access to Transformer-based AI
- Reduce environmental impact of model deployment
- Enable downstream innovations in edge computing and IoT applications

### Requested Budget
- Personnel: $300,000
- Compute Resources: $250,000
- Equipment & Infrastructure: $50,000
- **Total: $600,000**
"""
