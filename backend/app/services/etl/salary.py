import re
from dataclasses import dataclass


@dataclass(frozen=True)
class NormalizedSalary:
    minimum: float | None
    maximum: float | None
    currency: str | None


_CURRENCY_MARKERS = {
    "$": "USD",
    "usd": "USD",
    "₱": "PHP",
    "php": "PHP",
    "aud": "AUD",
    "eur": "EUR",
    "gbp": "GBP",
}


def _detect_currency(value: str) -> str | None:
    lowered = value.lower()
    for marker, currency in _CURRENCY_MARKERS.items():
        if marker in lowered:
            return currency
    return None


def _parse_amount(token: str) -> float:
    token = token.replace(",", "").strip().lower()
    multiplier = 1000 if token.endswith("k") else 1
    if token.endswith("k"):
        token = token[:-1]
    return float(token) * multiplier


def normalize_salary(value: str | None) -> NormalizedSalary:
    if not value:
        return NormalizedSalary(None, None, None)

    matches = re.findall(r"(?:[$₱]\s*)?(\d[\d,]*(?:\.\d+)?\s*k?)", value, flags=re.I)
    amounts = [_parse_amount(match) for match in matches]
    currency = _detect_currency(value)

    if not amounts:
        return NormalizedSalary(None, None, currency)
    if len(amounts) == 1:
        return NormalizedSalary(amounts[0], amounts[0], currency)
    return NormalizedSalary(min(amounts), max(amounts), currency)
