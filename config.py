import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY", "")

# Model aliases — Haiku for cheap generation/triage, Sonnet for analysis, Opus for high-risk review
HAIKU = "claude-haiku-4-5-20251001"
SONNET = "claude-sonnet-4-6"
OPUS = "claude-opus-4-8"

DEFAULT_MODEL = SONNET
TRIAGE_MODEL = HAIKU
HIGH_RISK_MODEL = OPUS

# Temperature budget: analysis calls must stay at or below this value
MAX_ANALYSIS_TEMPERATURE = 0.2
