"""
Triagem (Triage) Agent - Client authentication and routing.

This agent authenticates clients and directs them to the appropriate agent.
"""

import os
from datetime import datetime
from typing import Optional, Dict, Any
from .base_agent import BaseAgent


class TriagemAgent(BaseAgent):
    """Agent responsible for client triage and routing."""

    def __init__(self):
        """Initialize the Triagem Agent."""
        super().__init__("Triagem Agent")
        self.client_data = None
        self.authentication_attempts = 0
        self.max_attempts = 3
        self.is_authenticated = False
        self.clients_file = os.path.join(
            os.path.dirname(__file__), "..", "data", "clientes.csv"
        )

    def get_system_prompt(self) -> str:
        """Get the system prompt for the Triagem Agent."""
        return """Você é um agente de triagem bancário do Banco Ágil. Seu objetivo é:
1. Saudar o cliente de maneira amigável e profissional
2. Solicitar APENAS o CPF do cliente sem pontuações
3. Solicitar APENAS a data de nascimento do cliente
4. Validar os dados contra a base de clientes
5. Se autenticado, identificar o assunto e indicar o próximo agente
6. Se não autenticado, informar o erro e permitir até 2 novas tentativas

Mantenha um tom respeitoso, objetivo e evite repetições desnecessárias.
Sempre valide os dados antes de prosseguir."""

    def authenticate_client(self, cpf: str, data_nascimento: str) -> bool:
        """
        Authenticate a client against the database.

        Args:
            cpf: Client's CPF (number only, without punctuation)
            data_nascimento: Client's birth date (YYYY-MM-DD format)

        Returns:
            True if authentication is successful, False otherwise
        """
        try:
            clients = self.read_csv(self.clients_file)
            for client in clients:
                if client["cpf"] == cpf and client["data_nascimento"] == data_nascimento:
                    self.client_data = client
                    self.is_authenticated = True
                    return True
            return False
        except Exception as e:
            print(f"Error authenticating client: {str(e)}")
            return False

    def get_authenticated_client(self) -> Optional[Dict[str, Any]]:
        """Get the authenticated client data."""
        if self.is_authenticated:
            return self.client_data
        return None

    def get_authentication_attempts(self) -> int:
        """Get the number of authentication attempts."""
        return self.authentication_attempts

    def increment_attempts(self):
        """Increment authentication attempts."""
        self.authentication_attempts += 1

    def reset(self):
        """Reset the agent for a new client."""
        self.client_data = None
        self.authentication_attempts = 0
        self.is_authenticated = False
        self.clear_history()

    def is_max_attempts_reached(self) -> bool:
        """Check if maximum authentication attempts have been reached."""
        return self.authentication_attempts >= self.max_attempts
