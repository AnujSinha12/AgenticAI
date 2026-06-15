from dataclasses import dataclass

@dataclass
class UserContext:
    base_currency: str = 'USD'
    target_currency: str = 'INR'
    time_range: str = 'last year'