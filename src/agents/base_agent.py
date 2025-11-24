"""
Base Agent class for all banking agents using Google Generative AI.
"""

import os
import json
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import csv

import google.generativeai as genai


class BaseAgent(ABC):
    """Base class for all banking agents."""

    def __init__(self, agent_name: str, model_name: str = "gemini-2.5-flash"):
        """
        Initialize the agent with Google Generative AI.

        Args:
            agent_name: Name of the agent
            model_name: Name of the Google model to use
        """
        self.agent_name = agent_name
        self.model_name = model_name
        self.conversation_history = []

        # Initialize Google Generative AI
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY environment variable not set. "
                "Please set it to your Google API key."
            )
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        pass

    def send_message(self, user_message: str) -> str:
        """
        Send a message to the agent and get a response.

        Args:
            user_message: The user's message

        Returns:
            The agent's response
        """
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_message})

        # Build the conversation with system prompt
        messages = []

        # Add system prompt as first message
        system_prompt = self.get_system_prompt()
        messages.append(
            {
                "role": "user",
                "content": f"[SYSTEM PROMPT]\n{system_prompt}\n\n[USER MESSAGE]\n{user_message}",
            }
        )

        # Add conversation history (simplified for API)
        for msg in self.conversation_history[:-1]:  # Exclude the one we just added
            role = "user" if msg["role"] == "user" else "model"
            messages[-1][
                "content"
            ] += f"\n\n[PREVIOUS MESSAGE]\n{msg['content']}"

        try:
            # Send to Google Generative AI
            response = self.model.generate_content(messages[-1]["content"])
            assistant_message = response.text

            # Add assistant response to history
            self.conversation_history.append(
                {"role": "assistant", "content": assistant_message}
            )

            return assistant_message
        except Exception as e:
            error_message = f"Error calling Google Generative AI: {str(e)}"
            return error_message

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []

    @staticmethod
    def read_csv(filepath: str) -> List[Dict[str, Any]]:
        """
        Read a CSV file and return as list of dictionaries.

        Args:
            filepath: Path to the CSV file

        Returns:
            List of dictionaries representing rows
        """
        try:
            data = []
            with open(filepath, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(row)
            return data
        except Exception as e:
            raise Exception(f"Error reading CSV file {filepath}: {str(e)}")

    @staticmethod
    def write_csv(filepath: str, data: List[Dict[str, Any]], headers: List[str]):
        """
        Write data to a CSV file.

        Args:
            filepath: Path to the CSV file
            data: List of dictionaries to write
            headers: Column headers
        """
        try:
            with open(filepath, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data)
        except Exception as e:
            raise Exception(f"Error writing CSV file {filepath}: {str(e)}")

    @staticmethod
    def append_csv(filepath: str, row: Dict[str, Any]):
        """
        Append a row to a CSV file.

        Args:
            filepath: Path to the CSV file
            row: Dictionary representing the row to append
        """
        try:
            # Check if file exists and has content
            file_exists = os.path.isfile(filepath) and os.path.getsize(filepath) > 0

            with open(filepath, "a", newline="", encoding="utf-8") as file:
                if file_exists:
                    # File has content, just append
                    writer = csv.DictWriter(file, fieldnames=row.keys())
                    writer.writerow(row)
                else:
                    # File is empty or doesn't exist, write header and row
                    writer = csv.DictWriter(file, fieldnames=row.keys())
                    writer.writeheader()
                    writer.writerow(row)
        except Exception as e:
            raise Exception(f"Error appending to CSV file {filepath}: {str(e)}")

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history."""
        return self.conversation_history
