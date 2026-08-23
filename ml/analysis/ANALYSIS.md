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

