"""
Câmbio (Exchange) Agent - Currency exchange and quotation.

This agent handles currency exchange inquiries and quotations.
"""

import os
import requests
from typing import Dict, Any, Optional
from .base_agent import BaseAgent


class CambioAgent(BaseAgent):
    """Agent responsible for currency exchange operations."""

    def __init__(self):
        """Initialize the Câmbio Agent."""
        super().__init__("Câmbio Agent")
        self.api_key = os.getenv("TAVILY_API_KEY")

    def get_system_prompt(self) -> str:
        """Get the system prompt for the Câmbio Agent."""
        return """Você é um agente de câmbio do Banco Ágil. Seu objetivo é:
1. Consultar cotações de moedas em tempo real
2. Apresentar a cotação atual de forma clara
3. Fornecer informações úteis sobre câmbio
4. Encerrar o atendimento de forma amigável

Mantenha um tom profissional e informativo. Sempre cite a fonte e hora da cotação."""

    def get_exchange_rate(self, from_currency: str = "USD", to_currency: str = "BRL") -> Optional[Dict[str, Any]]:
        """
        Get the current exchange rate between two currencies.

        Args:
            from_currency: Source currency code (default: USD)
            to_currency: Target currency code (default: BRL)

        Returns:
            Dictionary with exchange rate information or None if failed
        """
        try:
            # Try using a free API (Open Exchange Rates, Fixer.io, or ExchangeRate-API)
            # Using exchangerate-api.com free tier
            url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                if to_currency in data.get("rates", {}):
                    rate = data["rates"][to_currency]
                    return {
                        "from": from_currency,
                        "to": to_currency,
                        "rate": rate,
                        "timestamp": data.get("time_last_updated", "N/A"),
                        "source": "exchangerate-api.com",
                    }
        except requests.exceptions.RequestException as e:
            print(f"Error fetching exchange rate: {str(e)}")

        return None

    def format_exchange_response(self, exchange_data: Dict[str, Any]) -> str:
        """
        Format exchange rate data into a friendly message.

        Args:
            exchange_data: Exchange rate information

        Returns:
            Formatted message
        """
        if not exchange_data:
            return "Desculpe, não consegui obter a cotação no momento. Tente novamente mais tarde."

        from_curr = exchange_data.get("from", "")
        to_curr = exchange_data.get("to", "")
        rate = exchange_data.get("rate", 0)
        timestamp = exchange_data.get("timestamp", "N/A")
        source = exchange_data.get("source", "fonte externa")

        return (
            f"A cotação atual é:\n"
            f"1 {from_curr} = {rate:.2f} {to_curr}\n"
            f"Fonte: {source}\n"
            f"Última atualização: {timestamp}\n"
            f"Obrigado por usar o Banco Ágil!"
        )

    def get_common_currencies(self) -> Dict[str, str]:
        """
        Get a dictionary of common currency codes and names.

        Returns:
            Dictionary mapping currency codes to names
        """
        return {
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
