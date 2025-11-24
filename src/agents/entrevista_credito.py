"""
Entrevista de Crédito (Credit Interview) Agent - Score recalculation.

This agent conducts financial interviews and recalculates credit scores.
"""

import os
from typing import Dict, Any, Optional
from .base_agent import BaseAgent


class EntrevistaCreditoAgent(BaseAgent):
    """Agent responsible for credit interviews and score recalculation."""

    def __init__(self):
        """Initialize the Entrevista Crédito Agent."""
        super().__init__("Entrevista Crédito Agent")
        self.client_data = None
        self.interview_data = {
            "renda_mensal": None,
            "tipo_emprego": None,
            "despesas_fixas": None,
            "numero_dependentes": None,
            "dividas_ativas": None,
        }
        self.clients_file = os.path.join(
            os.path.dirname(__file__), "..", "data", "clientes.csv"
        )

    def get_system_prompt(self) -> str:
        """Get the system prompt for the Entrevista Crédito Agent."""
        return """Você é um agente de entrevista de crédito do Banco Ágil. Seu objetivo é:
1. Conduzir uma entrevista conversacional estruturada
2. Coletar dados financeiros do cliente:
   - Renda mensal
   - Tipo de emprego (formal, autônomo, desempregado)
   - Despesas fixas mensais
   - Número de dependentes
   - Existência de dívidas ativas
3. Calcular um novo score de crédito
4. Atualizar o score na base de dados
5. Redirecionar o cliente de volta ao agente de crédito

Mantenha um tom empático e compreensivo. Explique a importância dos dados coletados."""

    def set_client(self, client_data: Dict[str, Any]):
        """
        Set the current client data.

        Args:
            client_data: Dictionary with client information
        """
        self.client_data = client_data
        self.reset_interview_data()

    def reset_interview_data(self):
        """Reset interview data for a new interview."""
        self.interview_data = {
            "renda_mensal": None,
            "tipo_emprego": None,
            "despesas_fixas": None,
            "numero_dependentes": None,
            "dividas_ativas": None,
        }

    def set_interview_data(self, key: str, value: Any):
        """
        Set a piece of interview data.

        Args:
            key: The key for the data
            value: The value
        """
        if key in self.interview_data:
            self.interview_data[key] = value

    def is_interview_complete(self) -> bool:
        """Check if all required interview data has been collected."""
        return all(v is not None for v in self.interview_data.values())

    def calculate_new_score(self) -> int:
        """
        Calculate a new credit score based on collected data.

        Returns:
            New credit score (0-1000)
        """
        if not self.is_interview_complete():
            return None

        try:
            # Weights
            peso_renda = 30
            peso_emprego = {"formal": 300, "autônomo": 200, "desempregado": 0}
            peso_dependentes = {0: 100, 1: 80, 2: 60, "3+": 30}
            peso_dividas = {"sim": -100, "não": 100}

            # Extract data
            renda_mensal = float(self.interview_data["renda_mensal"])
            tipo_emprego = self.interview_data["tipo_emprego"].lower()
            despesas_fixas = float(self.interview_data["despesas_fixas"])
            numero_dependentes = int(self.interview_data["numero_dependentes"])
            dividas_ativas = self.interview_data["dividas_ativas"].lower()

            # Normalize dependents to string key if needed
            dependentes_key = (
                "3+" if numero_dependentes >= 3 else numero_dependentes
            )

            # Calculate score components
            renda_component = (
                (renda_mensal / (despesas_fixas + 1)) * peso_renda
            )
            emprego_component = peso_emprego.get(tipo_emprego, 0)
            dependentes_component = peso_dependentes.get(dependentes_key, 0)
            dividas_component = peso_dividas.get(dividas_ativas, 0)

            # Total score
            total_score = (
                renda_component
                + emprego_component
                + dependentes_component
                + dividas_component
            )

            # Clamp between 0 and 1000
            new_score = max(0, min(1000, int(total_score)))
            return new_score
        except Exception as e:
            print(f"Error calculating score: {str(e)}")
            return None

    def update_client_score(self, new_score: int) -> bool:
        """
        Update the client's score in the database.

        Args:
            new_score: The new credit score

        Returns:
            True if update was successful
        """
        if not self.client_data:
            return False

        try:
            cpf = self.client_data.get("cpf", "")
            clients = self.read_csv(self.clients_file)

            for client in clients:
                if client["cpf"] == cpf:
                    client["score_credito"] = str(new_score)
                    break

            # Write back to file
            headers = list(clients[0].keys()) if clients else []
            self.write_csv(self.clients_file, clients, headers)

            # Update local client data
            self.client_data["score_credito"] = str(new_score)
            return True
        except Exception as e:
            print(f"Error updating client score: {str(e)}")
            return False

    def finalize_interview(self) -> Dict[str, Any]:
        """
        Finalize the interview by calculating and updating the score.

        Returns:
            Dictionary with interview results
        """
        if not self.is_interview_complete():
            return {"status": "erro", "mensagem": "Entrevista incompleta."}

        try:
            new_score = self.calculate_new_score()
            if new_score is None:
                return {
                    "status": "erro",
                    "mensagem": "Erro ao calcular score.",
                }

            success = self.update_client_score(new_score)
            if not success:
                return {
                    "status": "erro",
                    "mensagem": "Erro ao atualizar score na base de dados.",
                }

            return {
                "status": "sucesso",
                "mensagem": f"Score atualizado com sucesso! Novo score: {new_score}",
                "novo_score": new_score,
            }
        except Exception as e:
            return {"status": "erro", "mensagem": f"Erro ao finalizar entrevista: {str(e)}"}
