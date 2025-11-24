"""
Crédito (Credit) Agent - Credit limit management and requests.

This agent handles credit inquiries and increase requests.
"""

import os
import csv
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent


class CreditoAgent(BaseAgent):
    """Agent responsible for credit management."""

    def __init__(self):
        """Initialize the Crédito Agent."""
        super().__init__("Crédito Agent")
        self.client_data = None
        self.data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        self.clients_file = os.path.join(self.data_dir, "clientes.csv")
        self.score_limite_file = os.path.join(self.data_dir, "score_limite.csv")
        self.requests_file = os.path.join(
            self.data_dir, "solicitacoes_aumento_limite.csv"
        )

    def get_system_prompt(self) -> str:
        """Get the system prompt for the Crédito Agent."""
        return """Você é um agente de crédito do Banco Ágil. Seu objetivo é:
1. Consultar e informar o limite de crédito disponível do cliente
2. Processar solicitações de aumento de limite
3. Validar a solicitação contra o score e tabela de limites
4. Se rejeitado, oferecer redirecionamento para entrevista de crédito
5. Manter o cliente informado sobre o status de sua solicitação

Mantenha um tom profissional e confiante. Sempre explique as decisões de aprovação ou rejeição."""

    def set_client(self, client_data: Dict[str, Any]):
        """
        Set the current client data.

        Args:
            client_data: Dictionary with client information
        """
        self.client_data = client_data

    def get_client_credit_limit(self) -> str:
        """
        Get the client's current credit limit.

        Returns:
            Formatted string with credit limit information
        """
        if not self.client_data:
            return "Erro: Cliente não autenticado."

        try:
            limite = float(self.client_data.get("limite_credito", 0))
            nome = self.client_data.get("nome", "Cliente")
            return (
                f"O cliente {nome} possui um limite de crédito de R$ {limite:.2f}."
            )
        except Exception as e:
            return f"Erro ao obter limite de crédito: {str(e)}"

    def get_score_limits(self) -> Dict[str, Any]:
        """
        Get the score limits from the score_limite.csv file.

        Returns:
            Dictionary mapping scores to maximum limits
        """
        try:
            limits = {}
            data = self.read_csv(self.score_limite_file)
            for row in data:
                min_score = int(row["score_minimo"])
                max_score = int(row["score_maximo"])
                max_limit = float(row["limite_maximo"])
                limits[(min_score, max_score)] = max_limit
            return limits
        except Exception as e:
            print(f"Error reading score limits: {str(e)}")
            return {}

    def check_limit_approval(self, requested_limit: float) -> tuple[bool, str]:
        """
        Check if the requested limit is approved based on client's score.

        Args:
            requested_limit: The requested credit limit

        Returns:
            Tuple of (is_approved, reason)
        """
        if not self.client_data:
            return False, "Cliente não autenticado."

        try:
            current_score = float(self.client_data.get("score_credito", 0))
            score_limits = self.get_score_limits()

            # Find the appropriate limit for the client's score
            max_allowed_limit = None
            for (min_score, max_score), limit in score_limits.items():
                if min_score <= current_score <= max_score:
                    max_allowed_limit = limit
                    break

            if max_allowed_limit is None:
                return False, f"Score inválido: {current_score}"

            if requested_limit <= max_allowed_limit:
                return True, f"Limite solicitado dentro do permitido para score {current_score}"
            else:
                return (
                    False,
                    f"Limite solicitado (R$ {requested_limit:.2f}) excede o máximo permitido (R$ {max_allowed_limit:.2f}) para score {current_score}",
                )
        except Exception as e:
            return False, f"Erro ao verificar aprovação: {str(e)}"

    def create_limit_increase_request(self, requested_limit: float) -> Dict[str, Any]:
        """
        Create a limit increase request and check for approval.

        Args:
            requested_limit: The requested credit limit

        Returns:
            Dictionary with request information
        """
        if not self.client_data:
            return {"status": "erro", "mensagem": "Cliente não autenticado."}

        try:
            current_score = float(self.client_data.get("score_credito", 0))
            current_limit = float(self.client_data.get("limite_credito", 0))
            cpf = self.client_data.get("cpf", "")

            # Check approval
            is_approved, reason = self.check_limit_approval(requested_limit)
            status = "aprovado" if is_approved else "rejeitado"

            # Create request record
            request_record = {
                "cpf_cliente": cpf,
                "data_hora_solicitacao": datetime.now(timezone.utc).isoformat(),
                "limite_atual": str(current_limit),
                "novo_limite_solicitado": str(requested_limit),
                "status_pedido": status,
            }

            # Append to CSV
            self.append_csv(self.requests_file, request_record)

            # If approved, update client's limit in clientes.csv
            if is_approved:
                self._update_client_limit(cpf, requested_limit)
                self.client_data["limite_credito"] = str(requested_limit)

            return {
                "status": status,
                "mensagem": reason,
                "request": request_record,
            }
        except Exception as e:
            return {"status": "erro", "mensagem": f"Erro ao criar solicitação: {str(e)}"}

    def _update_client_limit(self, cpf: str, new_limit: float):
        """
        Update a client's credit limit in the database.

        Args:
            cpf: Client's CPF
            new_limit: New credit limit
        """
        try:
            clients = self.read_csv(self.clients_file)
            for client in clients:
                if client["cpf"] == cpf:
                    client["limite_credito"] = str(new_limit)
                    break

            # Write back to file
            headers = list(clients[0].keys()) if clients else []
            self.write_csv(self.clients_file, clients, headers)
        except Exception as e:
            print(f"Error updating client limit: {str(e)}")

    def should_offer_interview(self, request_result: Dict[str, Any]) -> bool:
        """
        Check if the agent should offer an interview to improve score.

        Args:
            request_result: Result from create_limit_increase_request

        Returns:
            True if request was rejected and interview should be offered
        """
        return request_result.get("status") == "rejeitado"
