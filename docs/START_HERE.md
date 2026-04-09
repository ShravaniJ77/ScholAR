# 🚀 ScholAR - Quick Start Guide

## One-Minute Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
streamlit run streamlit_app.py
```

**OR (Windows):**
```bash
Double-click: run.bat
```

### 3. Open Browser
Go to: **http://localhost:8501**

---

## 📋 What to Do First

1. **Enter a research topic** (e.g., "Retrieval Augmented Generation")
2. **Click "Start Research"** button
3. **Watch the Agent Think** - See real-time decision logs
4. **Explore Results** in tabs:
   - 🧠 Agent Thought Log - See all AI decisions
   - 📊 Contradiction Matrix - Research debates
   - 🕸️ Knowledge Graph - Paper relationships
   - 📑 Final Report - Comprehensive analysis
   - 📚 Sources - All papers analyzed

---

## 💡 Recommended Topics

**Try these to see ScholAR in action:**

- "Transformer Models in NLP"
- "Federated Learning Privacy"
- "Knowledge Graphs and Reasoning"
- "Vision Transformers"
- "Prompt Engineering"
- "Few-Shot Learning"

---

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# How many papers to analyze per search
MAX_PAPERS_PER_SEARCH = 20

# When to stop searching (higher = more thorough)
SATURATION_THRESHOLD = 0.85

# Maximum search iterations
RECURSIVE_SEARCH_MAX_DEPTH = 3
```

---

## 🔧 Troubleshooting

**"ModuleNotFoundError"**
```bash
pip install -r requirements.txt
python -c "import streamlit; print('OK')"
```

**"Rate limit errors"**
- System falls back to demo data automatically
- This is normal with free tier APIs

**"Streamlit not starting"**
```bash
pip install --upgrade streamlit
streamlit run app.py
```

---

## 🏆 Key Features

✨ **Autonomy** - Agent decides what to search and when to stop
✨ **Transparency** - Full thought log shows all decisions  
✨ **Intelligence** - Finds contradictions, gaps, and trends
✨ **Actionable** - Generates grant proposals for next research

---

## 📞 Need Help?

1. Check `README.md` for detailed documentation
2. Review `config.py` for API configuration
3. Run test: `python test_agent.py`

---

**Made for Hackathon - Autonomous Research Discovery**
