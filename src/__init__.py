"""ScholAR - Autonomous Research Agent

Core package for autonomous research and literature synthesis.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "Autonomous research agent for literature discovery and analysis"

from . import config
from . import models
from . import semantic_scholar
from . import llm_client
from . import agent
from . import pdf_generator
from . import mock_data

__all__ = [
    'config',
    'models',
    'semantic_scholar',
    'llm_client',
    'agent',
    'pdf_generator',
    'mock_data',
]
