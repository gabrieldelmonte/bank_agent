"""
Utility functions for Bank Agent System.

Contains helper functions for validation and data processing.
"""

import re
from datetime import datetime


def validate_cpf(cpf: str) -> bool:
    """
    Validate CPF format.

    Args:
        cpf: CPF string

    Returns:
        True if valid format, False otherwise
    """
    # Remove any non-digit characters
    cpf = re.sub(r"\D", "", cpf)

    # Check length
    if len(cpf) != 11:
        return False

    # Check if all digits are the same
    if len(set(cpf)) == 1:
        return False

    return True


def validate_date(date_str: str, format_str: str = "%Y-%m-%d") -> bool:
    """
    Validate date format.

    Args:
        date_str: Date string
        format_str: Expected format (default: YYYY-MM-DD)

    Returns:
        True if valid, False otherwise
    """
    try:
        datetime.strptime(date_str, format_str)
        return True
    except ValueError:
        return False


def format_currency(value: float) -> str:
    """
    Format value as Brazilian currency.

    Args:
        value: Numeric value

    Returns:
        Formatted currency string
    """
    return f"R$ {value:,.2f}".replace(",", ".")


def parse_currency(value_str: str) -> float:
    """
    Parse Brazilian currency format to float.

    Args:
        value_str: Currency string

    Returns:
        Float value
    """
    # Remove R$, spaces, and dots
    cleaned = value_str.replace("R$", "").replace(" ", "").replace(".", "")
    # Replace comma with dot
    cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def get_employment_type_pt(emp_type: str) -> str:
    """
    Get Portuguese name for employment type.

    Args:
        emp_type: Employment type

    Returns:
        Portuguese employment type name
    """
    types = {
        "formal": "Formal",
        "autônomo": "Autônomo",
        "desempregado": "Desempregado",
    }
    return types.get(emp_type.lower(), emp_type)


def get_debt_status_pt(has_debt: str) -> str:
    """
    Get Portuguese name for debt status.

    Args:
        has_debt: Debt status

    Returns:
        Portuguese debt status
    """
    return "Sim" if has_debt.lower() in ["sim", "yes", "true"] else "Não"


def calculate_age(birth_date: str) -> int:
    """
    Calculate age from birth date.

    Args:
        birth_date: Birth date in YYYY-MM-DD format

    Returns:
        Age in years
    """
    try:
        birth = datetime.strptime(birth_date, "%Y-%m-%d")
        today = datetime.now()
        age = today.year - birth.year - (
            (today.month, today.day) < (birth.month, birth.day)
        )
        return age
    except ValueError:
        return None
