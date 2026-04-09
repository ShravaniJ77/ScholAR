"""Configuration and constants for ScholAR."""

import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
SEMANTIC_SCHOLAR_API_KEY = "SqzhPnriBw42PJL25moSY9xejhtsHjHw45z7AHbP"
OPENROUTER_API_KEY = "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"

# API Endpoints
SEMANTIC_SCHOLAR_BASE = "https://api.semanticscholar.org/graph/v1"
OPENROUTER_BASE = "https://openrouter.ai/api/v1"

# Model Configuration
FAST_MODEL = "google/gemma-4-31b-it:free"  # Free tier fast/accurate model
SMART_MODEL = "google/gemma-4-31b-it:free"  # Free tier smart model

# Agent Configuration
MAX_PAPERS_PER_SEARCH = 50  # Increased from 20
SATURATION_THRESHOLD = 0.95  # Increased from 0.85 (95% before stopping)
MIN_PAPERS_FOR_SATURATION_CHECK = 10
RECURSIVE_SEARCH_MAX_DEPTH = 5  # Increased from 3 to allow more iterations
CONFIDENCE_THRESHOLD = 0.8

# Batch sizes
BATCH_SIZE = 5

# Timeouts
API_TIMEOUT = 30
LLM_TIMEOUT = 60
