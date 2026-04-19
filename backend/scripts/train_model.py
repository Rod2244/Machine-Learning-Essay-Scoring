"""
Train TF-IDF + Logistic Regression model for essay scoring
This is a beginner-friendly approach that works well for essay classification/regression
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score, r2_score
import joblib
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config


class EssayScorer:
    """
    TF-IDF based essay scoring model
    Approach: Extract text features → Predict score category
    """
    
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=config.MAX_FEATURES,
            min_df=5,
            max_df=0.8,
            ngram_range=(1, 2),  # Use both unigrams and bigrams
            lowercase=True,
            stop_words='english'
        )
        self.model = LogisticRegression(
            max_iter=1000,
            random_state=config.RANDOM_STATE
        )
        self.is_trained = False
    
    def prepare_data(self, df, text_column='text', score_column='score'):
        """Prepare and clean essay data"""
        print("📊 Preparing data...")
        
        # Remove null values
        df = df.dropna(subset=[text_column, score_column])
        
        # Convert scores to categories (0-100 → 0-5 scale)
        if df[score_column].max() > 10:
            df['score_category'] = pd.cut(df[score_column], 
                                         bins=[0, 20, 40, 60, 80, 100],
                                         labels=[0, 1, 2, 3, 4])
        else:
            df['score_category'] = df[score_column].astype(int)
        
        print(f"✓ Data prepared: {len(df)} essays")
        print(f"  Score distribution:\n{df['score_category'].value_counts().sort_index()}")
        
        return df
    
    def train(self, X_train, y_train):
        """Train the model"""
        print("\n🤖 Training model...")
        
        # Vectorize text
        X_train_vec = self.tfidf_vectorizer.fit_transform(X_train)
        
        # Train model
        self.model.fit(X_train_vec, y_train)
        self.is_trained = True
        
        print("✓ Model trained successfully")
    
    def evaluate(self, X_test, y_test):
        """Evaluate model on test set"""
        if not self.is_trained:
            print("❌ Model not trained yet!")
            return None
        
        print("\n📈 Evaluating model...")
        
        X_test_vec = self.tfidf_vectorizer.transform(X_test)
        y_pred = self.model.predict(X_test_vec)
        
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"✓ Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        
        return {
            'accuracy': accuracy,
            'predictions': y_pred
        }
    
    def predict(self, essay_text):
        """Predict score for a single essay"""
        if not self.is_trained:
            return None
        
        X = self.tfidf_vectorizer.transform([essay_text])
        score_category = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        
        # Convert category back to score (0-5 → 0-100)
        predicted_score = int(score_category * 20)
        confidence = float(max(probabilities))
        
        return {
            'score': predicted_score,
            'category': int(score_category),
            'confidence': confidence,
            'probabilities': probabilities.tolist()
        }
    
    def save(self, filepath):
        """Save model and vectorizer to disk"""
        model_data = {
            'tfidf_vectorizer': self.tfidf_vectorizer,
            'model': self.model
        }
        joblib.dump(model_data, filepath)
        print(f"\n💾 Model saved to: {filepath}")
    
    @staticmethod
    def load(filepath):
        """Load model and vectorizer from disk"""
        model_data = joblib.load(filepath)
        scorer = EssayScorer()
        scorer.tfidf_vectorizer = model_data['tfidf_vectorizer']
        scorer.model = model_data['model']
        scorer.is_trained = True
        print(f"✓ Model loaded from: {filepath}")
        return scorer


def load_dataset(filepath):
    """Load dataset based on file format"""
    if filepath.endswith('.tsv'):
        return pd.read_csv(filepath, sep='\t')
    elif filepath.endswith('.csv'):
        return pd.read_csv(filepath)
    elif filepath.endswith('.xlsx'):
        return pd.read_excel(filepath)
    else:
        raise ValueError(f"Unsupported file format: {filepath}")


def main():
    print("=" * 60)
    print("🎓 Essay Scoring Model Training")
    print("=" * 60)
    
    # Create models directory
    os.makedirs(config.MODELS_DIR, exist_ok=True)
    
    # Find training data
    data_dir = config.DATA_DIR
    training_file = None
    
    print(f"\n🔍 Looking for training data in {data_dir}...")
    
    # Check for common filenames
    for filename in ['sample_training_data.csv', 'training_set_rel3.tsv', 'train.csv', 'TRAINING.tsv']:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            training_file = filepath
            print(f"✓ Found: {filename}")
            break
    
    if not training_file:
        print(f"❌ No training data found in {data_dir}")
        print("\nPlease run: python scripts/download_datasets.py")
        return False
    
    try:
        # Load data
        df = load_dataset(training_file)
        print(f"\n✓ Loaded {len(df)} essays from {os.path.basename(training_file)}")
        print(f"Columns: {list(df.columns)}")
        
        # Initialize model
        scorer = EssayScorer()
        
        # Find text and score columns
        text_col = None
        score_col = None
        
        for col in df.columns:
            if col.lower() in ['essay', 'text', 'content']:
                text_col = col
            elif col.lower() in ['score', 'label', 'rating']:
                score_col = col
        
        if not text_col or not score_col:
            print(f"❌ Could not identify text/score columns")
            print(f"Available columns: {list(df.columns)}")
            return False
        
        # Prepare data
        df = scorer.prepare_data(df, text_column=text_col, score_column=score_col)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            df[text_col].astype(str),
            df['score_category'],
            test_size=config.TEST_SIZE,
            random_state=config.RANDOM_STATE
        )
        
        # Train model
        scorer.train(X_train, y_train)
        
        # Evaluate
        results = scorer.evaluate(X_test, y_test)
        
        # Save model
        model_path = os.path.join(config.MODELS_DIR, 'essay_scorer.pkl')
        scorer.save(model_path)
        
        # Test prediction
        print("\n🧪 Test Prediction:")
        sample_essay = X_test.iloc[0][:200]
        prediction = scorer.predict(sample_essay)
        print(f"Sample essay: {sample_essay}...")
        print(f"Predicted score: {prediction['score']}/100 (confidence: {prediction['confidence']:.2%})")
        
        print("\n" + "=" * 60)
        print("✓ Training complete!")
        print(f"Model saved to: {model_path}")
        print("\nNext: Run 'python app.py' to start the API server")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during training: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
