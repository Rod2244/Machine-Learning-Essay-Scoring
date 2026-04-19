"""
Script to download essay scoring datasets from Kaggle using kagglehub
Run this script once to download both datasets into the data/ folder
"""

import os
import sys
import kagglehub
import pandas as pd
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config


def setup_kaggle_credentials():
    """
    Setup Kaggle credentials from environment variables
    """
    kaggle_username = config.KAGGLE_USERNAME
    kaggle_key = config.KAGGLE_KEY
    
    if not kaggle_username or not kaggle_key:
        print("❌ ERROR: Kaggle credentials not configured!")
        print("\nSteps to fix:")
        print("1. Go to https://www.kaggle.com/settings/account")
        print("2. Click 'Create New API Token' to download kaggle.json")
        print("3. Copy KAGGLE_USERNAME and KAGGLE_KEY to .env file")
        print("\nExample .env:")
        print("KAGGLE_USERNAME=your_username")
        print("KAGGLE_KEY=your_api_key")
        return False
    
    # Set environment variables for kagglehub
    os.environ['KAGGLE_USERNAME'] = kaggle_username
    os.environ['KAGGLE_KEY'] = kaggle_key
    
    print(f"✓ Kaggle credentials configured for user: {kaggle_username}")
    return True


def download_hewlett_dataset():
    """Download The Hewlett Foundation: Automated Essay Scoring dataset"""
    print("\n📥 Downloading Hewlett Foundation dataset...")
    try:
        # Try multiple dataset reference formats
        try:
            path = kagglehub.dataset_download("asap-aes/essays")
        except:
            path = kagglehub.dataset_download("nagthakur/asap-aes")
        print(f"✓ Downloaded to: {path}")
        return path
    except Exception as e:
        print(f"⚠️  Could not auto-download: {e}")
        print("\nManual download option:")
        print("1. Go to: https://www.kaggle.com/c/asap-aes/data")
        print("2. Download all files")
        print("3. Extract to: backend/data/hewlett/")
        return None


def download_learning_agency_dataset():
    """Download Learning Agency Lab dataset"""
    print("\n📥 Downloading Learning Agency Lab dataset...")
    try:
        path = kagglehub.dataset_download("c/competitions/learning-agency-lab-automated-essay-scoring-2")
        print(f"✓ Downloaded to: {path}")
        return path
    except Exception as e:
        print(f"⚠️  Could not auto-download: {e}")
        print("\nManual download option:")
        print("1. Go to: https://www.kaggle.com/competitions/learning-agency-lab-automated-essay-scoring-2/data")
        print("2. Download all files")
        print("3. Extract to: backend/data/learning_agency/")
        return None


def generate_sample_data():
    """Generate sample training data if datasets unavailable"""
    print("\n📝 Generating sample training data...")
    
    # Create sample essays with scores
    np.random.seed(42)
    
    sample_essays = {
        "essay": [
            "The environmental crisis is the most pressing issue facing humanity today. Climate change threatens ecosystems, economies, and human societies. We must implement renewable energy solutions, protect forests, and reduce carbon emissions. International cooperation is essential to address this global challenge.",
            "Technology has transformed modern education. Online learning platforms provide access to quality education for students worldwide. However, face-to-face interaction remains important for social development. A balanced approach combining both methods is optimal.",
            "Shakespeare's works explore timeless human themes. His characters face moral dilemmas that resonate across centuries. The complexity of human nature, ambition, and love are universal concerns. These elements ensure his continued relevance.",
            "Social media presents both opportunities and challenges. It enables global communication and community building. Yet it can spread misinformation and cause mental health issues. Responsible use and digital literacy are crucial.",
            "The economic impact of remote work is significant. Companies save on office costs while employees enjoy flexibility. However, collaboration challenges and work-life balance issues emerge. Hybrid models may offer the best solution."
        ] * 100,  # Repeat to create 500 samples
        "score": np.random.randint(60, 100, 500).tolist(),
        "essay_id": list(range(500)),
        "essay_set": np.random.randint(1, 9, 500).tolist()
    }
    
    df = pd.DataFrame(sample_essays)
    
    # Save to CSV
    os.makedirs(config.DATA_DIR, exist_ok=True)
    output_path = os.path.join(config.DATA_DIR, "sample_training_data.csv")
    df.to_csv(output_path, index=False)
    
    print(f"✓ Generated {len(df)} sample essays")
    print(f"✓ Saved to: {output_path}")
    return output_path


def main():
    print("=" * 60)
    print("🚀 Kaggle Essay Scoring Datasets Downloader")
    print("=" * 60)
    
    # Create data directory if it doesn't exist
    os.makedirs(config.DATA_DIR, exist_ok=True)
    
    # Setup credentials
    if not setup_kaggle_credentials():
        print("\n⚠️  Cannot proceed without Kaggle credentials")
        return False
    
    # Download datasets
    hewlett_path = download_hewlett_dataset()
    learning_agency_path = download_learning_agency_dataset()
    
    print("\n" + "=" * 60)
    
    # If downloads failed, generate sample data
    if not hewlett_path and not learning_agency_path:
        print("⚠️  Could not download datasets automatically")
        print("\n📋 Using sample data for training instead...")
        sample_path = generate_sample_data()
        print("\n✓ Sample data generated successfully!")
        print("\nNOTE: This is sample data for testing. For production:")
        print("  1. Download real datasets from Kaggle")
        print("  2. Place in backend/data/ folder")
        print("  3. Update train_model.py to use those files")
        return True
    
    if hewlett_path or learning_agency_path:
        print("✓ Dataset(s) downloaded successfully!")
        if hewlett_path:
            print(f"  📁 Hewlett Foundation: {hewlett_path}")
        if learning_agency_path:
            print(f"  📁 Learning Agency: {learning_agency_path}")
        print("\nNext steps:")
        print("  1. Run: python scripts/train_model.py")
        print("  2. Then: python app.py")
        return True
    else:
        print("❌ Failed to download datasets and generate sample data")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
