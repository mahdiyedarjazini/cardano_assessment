from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class TransactionType(str, Enum):
    BUY = "Buy"
    SELL = "Sell"


class Currency(str, Enum):
    USD = "USD"  # United States Dollar
    EUR = "EUR"  # Euro
    GBP = "GBP"  # British Pound
    INR = "INR"  # Indian Rupee
    CHF = "CHF"  # Swiss Franc


class TransactionInput(BaseModel):
    """Model for a single transaction from the input dataset."""
    transaction_uti: str
    isin: str = Field(max_length=12, min_length=12)
    national: float
    national_currency: List[Currency]
    transaction_type: List[TransactionType]
    transaction_datetime: datetime
    rate: float
    lei: str = Field(max_length=20, min_length=20)


class ExternalData(BaseModel):
    """Model for the response from external API."""
    data: List[Dict[str, Any]]


class EnrichedTransaction(BaseModel):
    """Model for an enriched transaction with additional data."""
    transaction_uti: str
    isin: str = Field(max_length=12, min_length=12)
    national: float
    national_currency: List[Currency]
    transaction_type: List[TransactionType]
    transaction_datetime: str
    rate: float
    lei: str = Field(max_length=20, min_length=20)
    legal_name: str
    bic: List[str]
    transaction_costs: float
    country: Optional[str] = None
