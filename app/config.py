import os
from openai import OpenAI

# API key can be fixed here or read from an environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or "SUA-CHAVE-AQUI"

client = OpenAI(api_key=OPENAI_API_KEY)

# Fine-tuned legal model (set the ID if available)
FINE_TUNED_LEGAL_MODEL_ID = None  # ex: "ft:gpt-4o-mini-2024-07-18:personal::XXXXX"

# Base model for fallback and non-legal agents
BASE_MODEL_ID = "gpt-4o-mini"

# Model that the Legal Agent will use
LEGAL_MODEL_ID = FINE_TUNED_LEGAL_MODEL_ID or BASE_MODEL_ID
