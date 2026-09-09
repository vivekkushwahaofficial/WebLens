# WebLens

> **Machine-learning powered malicious URL detection and early-warning system.**

WebLens is a defensive cybersecurity project that analyzes URLs using machine learning and provides a structured risk assessment through a FastAPI backend and Chrome extension.

The system is designed to help identify potentially malicious URLs, including **phishing, malware, and defacement**, before users interact with them.

---

## ✨ Features

* 🔍 URL-based malicious URL detection
* 🤖 Machine-learning classification
* 🛡️ Risk assessment and verdict generation
* 💡 Human-readable detection reasons
* ⚡ FastAPI REST API
* 🌐 Chrome browser extension
* 🧪 Automated API and ML tests
* 📊 Domain-aware ML evaluation
* 🔬 Dataset remediation and error analysis
* 📐 Feature-schema validation

---

## 🏗️ How It Works

```text
Browser / User
      │
      ▼
Chrome Extension
      │
      ▼
FastAPI Backend
      │
      ▼
URL Feature Extraction
      │
      ▼
ML Model
      │
      ▼
Prediction + Confidence
      │
      ▼
Risk Assessment
      │
      ▼
Warning / Analysis Result
```

---

## 🧰 Tech Stack

| Area            | Technology            |
| --------------- | --------------------- |
| Backend         | Python                |
| API             | FastAPI + Uvicorn     |
| ML              | Scikit-learn          |
| Data Processing | Pandas + NumPy        |
| Model Storage   | Joblib                |
| Validation      | Pydantic              |
| Testing         | Pytest                |
| Extension       | TypeScript            |
| Browser         | Chrome Extension APIs |
| Version Control | Git + GitHub          |

---

## 📁 Project Structure

```text
WebLens/
├── apps/
│   ├── api/
│   │   └── app/
│   │       ├── routes/
│   │       ├── services/
│   │       └── main.py
│   │
│   └── extension/
│
├── ml/
│   ├── data/
│   ├── features/
│   ├── inference/
│   ├── preprocessing/
│   ├── training/
│   └── models/
│
├── docs/
├── tests/
├── LICENSE
└── README.md
```

---

# 🚀 Quick Start

## 1. Clone

```bash
git clone https://github.com/vivekkushwahaofficial/WebLens.git
cd WebLens
```

## 2. Create Python Environment

### Windows

```bash
python -m venv apps/api/.venv
apps/api/.venv/Scripts/activate
```

### Linux / macOS

```bash
python3 -m venv apps/api/.venv
source apps/api/.venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r apps/api/requirements.txt
```

---

# ⚡ Run the API

From the project root:

### Windows

```bash
set PYTHONPATH=apps/api;.
python -m uvicorn app.main:app --reload
```

### Linux / macOS

```bash
PYTHONPATH=apps/api:. python -m uvicorn app.main:app --reload
```

The API runs at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 🔎 API

### Health Check

```http
GET /api/v1/health
```

Example:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

Response:

```json
{
  "status": "ok"
}
```

### Analyze URL

```http
POST /api/v1/analyze
```

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"https://example.com\"}"
```

The response contains the analyzed URL, risk score, verdict, confidence, and detection reasons.

---

# 🤖 Machine Learning

WebLens currently uses a **Random Forest classifier** with **48 URL-derived features**.

The classifier predicts four classes:

```text
benign
defacement
malware
phishing
```

### Current Evaluation

The remediated dataset contains **641,152 URLs**.

| Metric          |  Score |
| --------------- | -----: |
| Accuracy        | 91.68% |
| Macro Precision | 88.78% |
| Macro Recall    | 91.08% |
| Macro F1        | 89.65% |

Evaluation uses an **unseen-domain split**, with no shared domains between the training and testing sets.

> These are measured evaluation results, not a guarantee of real-world detection performance.

---

# 🧪 Testing

Run the test suite:

```bash
pytest
```

API tests:

```bash
pytest apps/api
```

ML tests:

```bash
pytest ml
```

For the Chrome extension:

```bash
cd apps/extension
npm install
npm run typecheck
npm run build
```

---

# 🧠 ML Inference

The inference module can also be executed independently:

```bash
PYTHONPATH=. python ml/inference/predictor.py
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH="."
python ml/inference/predictor.py
```

Model artifacts are stored locally under:

```text
ml/models/
```

Large datasets and `.joblib` model artifacts are intentionally excluded from Git.

---

# 🤝 Contributing

Contributions are welcome!

### 1. Fork the repository

### 2. Clone your fork

```bash
git clone https://github.com/<your-username>/WebLens.git
cd WebLens
```

### 3. Create a branch

```bash
git checkout -b feature/your-feature
```

Examples:

```text
feature/ml-improvement
feature/api-improvement
feature/extension-warning
fix/url-validation
docs/readme-update
```

### 4. Make your changes

Keep changes focused and avoid unrelated modifications.

### 5. Test your changes

```bash
pytest
```

For extension changes:

```bash
npm run typecheck
npm run build
```

### 6. Commit and push

```bash
git add <specific-files>
git commit -m "feat: describe your change"
git push origin feature/your-feature
```

Then open a Pull Request.

---

# 🔐 Responsible Use

WebLens is intended for **defensive security, research, and educational purposes**.

Do not use the project to facilitate:

* Phishing
* Credential theft
* Malware distribution
* Unauthorized access
* Attacks against systems without permission

Only test systems and URLs that you are authorized to analyze.

---

# 📄 License

WebLens is released under the **Apache License 2.0**.

See [`LICENSE`](LICENSE) for the complete license.

## ⭐ Contributing to WebLens

If you find a bug, have an idea, improve the ML pipeline, or want to improve the browser extension, contributions are welcome.

**Build safer browsing with WebLens.**
