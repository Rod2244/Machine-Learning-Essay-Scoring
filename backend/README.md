# Essay Scoring ML Backend

Python backend for automated essay scoring using TF-IDF + Logistic Regression.

## Setup Instructions

### 1. Get Kaggle API Key

1. Go to https://www.kaggle.com/settings/account
2. Scroll to "API" section and click "Create New API Token"
3. This downloads `kaggle.json` with your credentials

### 2. Create `.env` file

Copy `.env.example` to `.env` and add your Kaggle credentials:

```bash
cp .env.example .env
```

Edit `.env` and add:

```
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_api_key_from_kaggle_json
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or create a virtual environment first:

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Mac/Linux
pip install -r requirements.txt
```

### 4. Download Datasets

```bash
python scripts/download_datasets.py
```

This downloads the two Kaggle essay scoring datasets:

- **The Hewlett Foundation: Automated Essay Scoring**
- **Learning Agency Lab - Automated Essay Scoring 2.0**

### 5. Train the Model

```bash
python scripts/train_model.py
```

This creates `models/essay_scorer.pkl` - the trained model file.

Output will show:

- Dataset loading
- Model training
- Accuracy metrics
- Test prediction

### 6. Start the API Server

```bash
python app.py
```

Server will start on `http://localhost:5000`

## API Endpoints

### Score Single Essay

```http
POST /api/score
Content-Type: application/json

{
    "prompt": "Describe your favorite book",
    "response": "Lorem ipsum dolor sit amet..."
}
```

**Response:**

```json
{
  "success": true,
  "score": 85,
  "category": 4,
  "confidence": 0.92,
  "breakdown": {
    "thesis": 25,
    "evidence": 23,
    "structure": 24,
    "grammar": 20
  },
  "feedback": "Strong essay with good argumentation"
}
```

### Score Multiple Essays

```http
POST /api/batch-score
Content-Type: application/json

{
    "essays": [
        {"response": "First essay text..."},
        {"response": "Second essay text..."}
    ]
}
```

### Get Rubrics

```http
GET /api/rubrics
```

### Health Check

```http
GET /health
```

## Directory Structure

```
backend/
├── app.py                          # Flask API server
├── config.py                       # Configuration
├── requirements.txt                # Python dependencies
├── .env.example                    # Example environment variables
├── .gitignore
├── README.md
├── data/                           # Kaggle datasets (downloaded)
│   ├── training_set_rel3.tsv
│   ├── test_set.tsv
│   └── ...
├── models/                         # Trained ML models
│   └── essay_scorer.pkl
└── scripts/
    ├── download_datasets.py        # Download Kaggle datasets
    └── train_model.py              # Train the ML model
```

## ML Model Details

### Approach: TF-IDF + Logistic Regression

- **Feature Extraction**: TF-IDF vectorization with:
  - Max 5000 features
  - Unigrams + bigrams
  - English stop words removal
- **Model**: Logistic Regression (multi-class classification)
- **Output**: Score category (0-5) → Converted to 0-100 scale

### Why This Approach?

✓ Fast to train and predict
✓ Interpretable results
✓ Good baseline for essay scoring
✓ Works well for beginners
✓ Low computational requirements

### Alternative Models (Future)

- XGBoost with feature engineering
- LSTM/RNN with word embeddings
- BERT fine-tuned for regression
- Ensemble methods

## Troubleshooting

### "Kaggle credentials not configured"

- Check your `.env` file has correct username and key
- Verify the API token from https://www.kaggle.com/settings/account

### "Model not found"

- Run `python scripts/train_model.py` to train the model first

### "No training data found"

- Run `python scripts/download_datasets.py` to download datasets

### Port already in use

- Change PORT in `.env` file (default: 5000)

## Next: Connect to Frontend

Update React frontend to call the API:

```javascript
const response = await fetch("http://localhost:5000/api/score", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    prompt: essayPrompt,
    response: studentResponse,
  }),
});
```
