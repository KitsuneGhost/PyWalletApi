from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import Optional


@dataclass
class DepositDTO:
    wallet_id: int
    amount: Decimal


@dataclass
class WithdrawDTO:
    wallet_id: int
    amount: Decimal


@dataclass
class TransferDTO:
    amount: Decimal
    from_wallet_id: Optional[int]
    to_wallet_id: Optional[int]


@dataclass
class TransactionResponseDTO:
    id: int
    type: str
    amount: Decimal
    timestamp: datetime
    user_id: int
    from_wallet_id: Optional[int]
    to_wallet_id: Optional[int]
