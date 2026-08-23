import math
import re
from urllib.parse import parse_qs, urlparse


def _parse_url(url: str):
    """Parse a URL safely while supporting URLs without a scheme."""

    url = str(url).strip()

    if not url:
        return urlparse("")

    if "://" not in url:
        url = "//" + url

    try:
        return urlparse(url)
    except ValueError:
        # Some dataset URLs contain malformed host syntax,
        # such as invalid bracketed IPv6 values.
        # Return an empty parsed URL instead of crashing
        # the entire feature-generation pipeline.
        return urlparse("")


def _entropy(value: str) -> float:
    """Calculate Shannon entropy of a string."""

    if not value:
        return 0.0

    counts = {}

    for character in value:
        counts[character] = counts.get(character, 0) + 1

    length = len(value)

    return -sum(
        (count / length) * math.log2(count / length)
        for count in counts.values()
    )


def _has_valid_port(parsed) -> int:
    """Safely determine whether a parsed URL contains a valid port."""

    try:
        return int(parsed.port is not None)
    except ValueError:
        # Malformed ports exist in the dataset. Treat them as
        # having no valid port instead of crashing preprocessing.
        return 0


def extract_url_component_features(url: str) -> dict[str, float]:
    """
    Extract URL component-level features.

    These features describe the hostname, path, query,
    URL depth, and character entropy.
    """

    url = str(url).strip()

    parsed = _parse_url(url)

    hostname = parsed.hostname or ""
    path = parsed.path or ""
    query = parsed.query or ""

    hostname_parts = [
        part
        for part in hostname.split(".")
        if part
    ]

    query_parameters = parse_qs(
        query,
        keep_blank_values=True,
    )

    features = {
        # Hostname features.
        "hostname_length": len(hostname),
        "hostname_digit_count": len(
            re.findall(r"\d", hostname)
        ),
        "hostname_hyphen_count": hostname.count("-"),
        "hostname_dot_count": hostname.count("."),
        "subdomain_count": max(
            len(hostname_parts) - 2,
            0,
        ),

        # Path features.
        "path_length": len(path),
        "path_digit_count": len(
            re.findall(r"\d", path)
        ),
        "path_special_char_count": len(
            re.findall(r"[^A-Za-z0-9/]", path)
        ),
        "path_depth": len(
            [part for part in path.split("/") if part]
        ),

        # Query features.
        "query_length": len(query),
        "query_parameter_count": len(query_parameters),
        "query_digit_count": len(
            re.findall(r"\d", query)
        ),
        "query_special_char_count": len(
            re.findall(r"[^A-Za-z0-9]", query)
        ),

        # Entropy features.
        "hostname_entropy": _entropy(hostname),
        "path_entropy": _entropy(path),
        "query_entropy": _entropy(query),

        # Structural indicators.
        "has_query": int(bool(query)),
        "has_fragment": int(bool(parsed.fragment)),
        "has_port": _has_valid_port(parsed),
    }

    return features
