def generate_reasons(
    *,
    url_length: int,
    uses_ip_address: bool,
    has_suspicious_keyword: bool,
) -> list[str]:
    """Generate human-readable reasons for the initial assessment."""

    reasons: list[str] = []

    if url_length > 100:
        reasons.append("Unusually long URL")

    if uses_ip_address:
        reasons.append("URL uses an IP address instead of a domain name")

    if has_suspicious_keyword:
        reasons.append("URL contains potentially suspicious keywords")

    if not reasons:
        reasons.append(
            "No significant suspicious URL patterns detected"
        )

    return reasons