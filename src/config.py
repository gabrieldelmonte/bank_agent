"""
Configuration module for Bank Agent System.

Contains all configuration constants and settings.
"""

import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Data directory
DATA_DIR = PROJECT_ROOT / "data"

# Files
CLIENTES_CSV = DATA_DIR / "clientes.csv"
SCORE_LIMITE_CSV = DATA_DIR / "score_limite.csv"
SOLICITACOES_CSV = DATA_DIR / "solicitacoes_aumento_limite.csv"

# Agent configuration
MAX_AUTHENTICATION_ATTEMPTS = 3
DEFAULT_MODEL = "gemini-2.5-flash"

# Credit score weights
PESO_RENDA = 30
PESO_EMPREGO = {
    "formal": 300,
    "autônomo": 200,
    "desempregado": 0,
}
PESO_DEPENDENTES = {
    0: 100,
    1: 80,
    2: 60,
    "3+": 30,
}
PESO_DIVIDAS = {
    "sim": -100,
    "não": 100,
}

# Score bounds
MIN_SCORE = 0
MAX_SCORE = 1000

# Currency exchange
EXCHANGE_RATE_API = "https://api.exchangerate-api.com/v4/latest/"

# Common currencies
COMMON_CURRENCIES = {
    "USD": "Dólar Americano",
    "EUR": "Euro",
    "GBP": "Libra Esterlina",
    "JPY": "Iene Japonês",
    "AUD": "Dólar Australiano",
    "CAD": "Dólar Canadense",
    "CHF": "Franco Suíço",
    "CNY": "Yuan Chinês",
    "INR": "Rúpia Indiana",
    "BRL": "Real Brasileiro",
}
