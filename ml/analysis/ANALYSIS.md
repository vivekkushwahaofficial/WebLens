# WebLens Dataset Analysis

## Dataset

Source:

Kaggle Malicious URLs Dataset

File:

`ml/data/raw/malicious_phish.csv`

Rows:

651,191

Columns:

- `url`
- `type`

Classes:

- benign
- defacement
- phishing
- malware

## Class Distribution

| Class | Count | Percentage |
|---|---:|---:|
| benign | 428,103 | 65.74% |
| defacement | 96,457 | 14.81% |
| phishing | 94,111 | 14.45% |
| malware | 32,520 | 4.99% |

## Data Quality

- Missing URLs: 0
- Missing labels: 0
- Empty URLs: 0
- Whitespace anomalies: 7
- Duplicate rows: 10,066
- Duplicate URLs: 10,072
- Unique URLs: 641,119
- Conflicting URL labels: 6

## Domain Analysis

- Unique hostnames: 196,513
- URLs with extracted hostname: 651,161
- URLs without extracted hostname: 30
- Hostnames appearing more than once: 45,177
- Hostnames appearing in multiple classes: 2,855

## Domain Concentration

| Class | Unique Hostnames | Top 10 Concentration | Top 100 Concentration |
|---|---:|---:|---:|
| benign | 134,063 | 11.752% | 25.728% |
| defacement | 2,122 | 1.649% | 11.167% |
| malware | 7,364 | 34.056% | 52.749% |
| phishing | 55,824 | 8.577% | 15.607% |

## Important Findings

### 1. URL structural features are useful

URL length, character counts, delimiters, protocol indicators, IP address indicators, and suspicious keyword patterns show different distributions between classes.

### 2. Hostname identity should not be used as a primary baseline feature

2,855 hostnames occur across multiple classes.

The malware class is also highly concentrated in a small number of hostnames.

Using raw hostname identity could cause the model to memorize domains rather than learn generalizable URL characteristics.

### 3. Domain-aware evaluation should be investigated

Random URL-level splitting may allow URLs from the same domain to appear in both training and testing.

This can lead to overly optimistic evaluation.

### 4. Class imbalance must be considered

The benign class represents 65.74% of the dataset while malware represents only 4.99%.

Accuracy alone is therefore insufficient.

Evaluation should include:

- Accuracy
- Precision
- Recall
- F1-score
- Macro F1
- Confusion matrix

## Initial Cleaning Policy

1. Keep the raw dataset unchanged.
2. Normalize leading/trailing whitespace during preprocessing.
3. Remove exact duplicate rows.
4. Remove the six URL groups with conflicting labels rather than arbitrarily assigning a label.
5. Do not use raw hostname identity as a baseline predictive feature.
6. Investigate domain-aware evaluation before final model selection.

## Initial Feature Direction

Focus on explainable URL lexical and structural features:

- URL length
- digit count
- letter count
- special character count
- dot count
- hyphen count
- slash count
- query indicators
- parameter indicators
- `@` count
- percent encoding
- IP address indicator
- HTTP/HTTPS indicators
- suspicious keyword indicators


## Baseline Model Results

### Random URL-Level Split

Random Forest using the initial 27 lexical and structural features:

| Metric | Score |
|---|---:|
| Accuracy | 0.9138 |
| Macro Precision | 0.8768 |
| Macro Recall | 0.9092 |
| Macro F1 | 0.8901 |

### Strict Domain-Aware Split

Random Forest using the initial 27 features and testing only on unseen hostnames:

| Metric | Score |
|---|---:|
| Accuracy | 0.8717 |
| Macro Precision | 0.7924 |
| Macro Recall | 0.8114 |
| Macro F1 | 0.7931 |

This demonstrates that URL-level random splitting produces more optimistic results because
hostnames can occur in both training and testing sets.

## Enhanced Feature Results

The enhanced feature set contains 46 features:

- 27 lexical and structural URL features
- 19 hostname, path, query, entropy, and structural component features

Under the same strict domain-aware split:

| Metric | 27 Features | 46 Features |
|---|---:|---:|
| Accuracy | 0.8717 | 0.9031 |
| Macro Precision | 0.7924 | 0.8477 |
| Macro Recall | 0.8114 | 0.8682 |
| Macro F1 | 0.7931 | 0.8524 |

The enhanced feature set improves Macro F1 from 0.7931 to 0.8524.

Per-class F1 scores for the enhanced model:

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| benign | 0.98 | 0.91 | 0.94 |
| defacement | 0.88 | 0.96 | 0.92 |
| malware | 0.87 | 0.73 | 0.79 |
| phishing | 0.66 | 0.87 | 0.75 |

## Feature Importance

Random Forest feature importance under the strict domain-aware training split shows that
structural URL characteristics dominate the model.

Top features:

| Rank | Feature | Importance |
|---:|---|---:|
| 1 | has_http | 11.189% |
| 2 | slash_count | 7.507% |
| 3 | special_char_count | 5.712% |
| 4 | path_length | 5.416% |
| 5 | hostname_entropy | 5.282% |
| 6 | digit_count | 4.760% |
| 7 | hostname_digit_count | 4.277% |
| 8 | subdomain_count | 4.215% |
| 9 | has_ip_address | 4.212% |
| 10 | path_entropy | 3.816% |

Individual suspicious keyword indicators have relatively low Random Forest importance compared
with structural features.

Therefore, WebLens should prioritize explainable lexical and structural URL characteristics
rather than relying primarily on suspicious keyword matching.

## Current ML Baseline

The current WebLens baseline is:

- 46 explainable URL features
- Random Forest classifier
- `n_estimators=200`
- `random_state=42`
- `class_weight="balanced"`
- strict domain-aware evaluation
- zero shared hostnames between training and testing

Current benchmark:

**Macro F1: 0.8524**
**Accuracy: 0.9031**
