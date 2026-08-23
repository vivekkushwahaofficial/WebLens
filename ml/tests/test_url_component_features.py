from ml.features.url_component_features import (
    extract_url_component_features,
)


def test_hostname_features():
    url = "https://login.example.com/account"

    features = extract_url_component_features(url)

    assert features["hostname_length"] == len("login.example.com")
    assert features["subdomain_count"] == 1
    assert features["hostname_digit_count"] == 0
    assert features["hostname_hyphen_count"] == 0


def test_path_features():
    url = "https://example.com/user/account/login"

    features = extract_url_component_features(url)

    assert features["path_length"] == len(
        "/user/account/login"
    )
    assert features["path_depth"] == 3
    assert features["path_digit_count"] == 0


def test_query_features():
    url = "https://example.com/login?id=123&user=test"

    features = extract_url_component_features(url)

    assert features["has_query"] == 1
    assert features["query_parameter_count"] == 2
    assert features["query_digit_count"] == 3


def test_fragment_detection():
    url = "https://example.com/page#login"

    features = extract_url_component_features(url)

    assert features["has_fragment"] == 1


def test_url_without_scheme():
    url = "example.com/user/login"

    features = extract_url_component_features(url)

    assert features["hostname_length"] == len("example.com")
    assert features["path_depth"] == 2


def test_empty_url():
    features = extract_url_component_features("")

    assert features["hostname_length"] == 0
    assert features["path_length"] == 0
    assert features["query_length"] == 0
    assert features["hostname_entropy"] == 0


def test_malformed_url_does_not_crash():
    url = "http://[invalid-ipv6-host"

    features = extract_url_component_features(url)

    assert features["hostname_length"] == 0
    assert features["path_length"] == 0
    assert features["query_length"] == 0


def test_malformed_port_does_not_crash():
    url = "http://example.com:invalid-port/path"

    features = extract_url_component_features(url)

    assert features["has_port"] == 0
