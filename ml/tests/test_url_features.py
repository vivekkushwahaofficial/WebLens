from ml.features.url_features import (
    FEATURE_NAMES,
    extract_url_features,
    features_to_vector,
)


def test_basic_url_features():
    url = "https://example.com/login?id=123"

    features = extract_url_features(url)

    assert features["url_length"] == len(url)
    assert features["digit_count"] == 3
    assert features["dot_count"] == 1
    assert features["slash_count"] == 3
    assert features["question_count"] == 1
    assert features["equals_count"] == 1
    assert features["has_https"] == 1
    assert features["has_http"] == 0
    assert features["has_login"] == 1


def test_suspicious_url_features():
    url = "http://192.168.1.10/verify/account?password=123"

    features = extract_url_features(url)

    assert features["has_http"] == 1
    assert features["has_https"] == 0
    assert features["has_ip_address"] == 1
    assert features["has_verify"] == 1
    assert features["has_account"] == 1
    assert features["has_password"] == 1


def test_clean_url_features():
    url = "example.com/about"

    features = extract_url_features(url)

    assert features["has_http"] == 0
    assert features["has_https"] == 0
    assert features["has_ip_address"] == 0
    assert features["has_login"] == 0
    assert features["has_password"] == 0


def test_whitespace_is_normalized():
    url = "  https://example.com/login  "

    features = extract_url_features(url)

    assert features["url_length"] == len(url.strip())
    assert features["has_https"] == 1
    assert features["has_login"] == 1


def test_feature_schema_has_27_features():
    assert len(FEATURE_NAMES) == 27
    assert len(set(FEATURE_NAMES)) == 27


def test_features_follow_canonical_order():
    url = "https://example.com/login?id=123"

    features = extract_url_features(url)
    vector = features_to_vector(features)

    assert len(vector) == len(FEATURE_NAMES)

    for index, feature_name in enumerate(FEATURE_NAMES):
        assert vector[index] == features[feature_name]


def test_missing_feature_is_rejected():
    features = extract_url_features("example.com")

    del features["url_length"]

    try:
        features_to_vector(features)
        assert False, "Expected ValueError"
    except ValueError as error:
        assert "url_length" in str(error)
