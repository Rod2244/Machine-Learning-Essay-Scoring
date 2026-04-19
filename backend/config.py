import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', False)
    PORT = int(os.getenv('PORT', 5000))
    
    # Kaggle credentials
    KAGGLE_USERNAME = os.getenv('KAGGLE_USERNAME')
    KAGGLE_KEY = os.getenv('KAGGLE_KEY')
    
    # Dataset paths
    DATASET_1 = os.getenv('DATASET_1', 'c/competitions/asap-aes/data')
    DATASET_2 = os.getenv('DATASET_2', 'c/competitions/learning-agency-lab-automated-essay-scoring-2/data')
    
    # Project paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    MODELS_DIR = os.path.join(BASE_DIR, 'models')
    SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')
    
    # Model training config
    TEST_SIZE = 0.2
    RANDOM_STATE = 42
    MAX_FEATURES = 5000
    
config = Config()
