import ipaddress
from dataclasses import dataclass
from urllib.parse import urlparse

from app.services.risk_assessment import RiskAssessment, assess_risk


SUSPICIOUS_KEYWORDS = (
    "login",
    "verify",
    "account",
    "password",
    "secure",
    "update",
)


@dataclass(frozen=True)
class URLFeatures:
    """Basic URL signals used by the initial analyzer."""

    url_length: int
    uses_ip_address: bool
    has_suspicious_keyword: bool


def _uses_ip_address(hostname: str | None) -> bool:
    """Return True when the hostname is an IPv4 or IPv6 address."""

    if not hostname:
        return False

    try:
        ipaddress.ip_address(hostname)
        return True
    except ValueError:
        return False


def _has_suspicious_keyword(url: str) -> bool:
    """Check for a small initial set of suspicious URL keywords."""

    normalized_url = url.lower()

    return any(
        keyword in normalized_url
        for keyword in SUSPICIOUS_KEYWORDS
    )


def extract_features(url: str) -> URLFeatures:
    """Extract the initial URL features."""

    parsed_url = urlparse(url)

    return URLFeatures(
        url_length=len(url),
        uses_ip_address=_uses_ip_address(parsed_url.hostname),
        has_suspicious_keyword=_has_suspicious_keyword(url),
    )


def analyze_url(url: str) -> tuple[URLFeatures, RiskAssessment]:
    """Extract URL features and calculate the initial risk."""

    features = extract_features(url)

    assessment = assess_risk(
        url_length=features.url_length,
        uses_ip_address=features.uses_ip_address,
        has_suspicious_keyword=features.has_suspicious_keyword,
    )

    return features, assessment