"""
Multi-trait essay scoring model training (Feedback Prize 2022 format)

Trains 4 separate XGBRegressor models, one per trait:
  - Content & Ideas   (mapped from 'vocabulary' column)
  - Organization      (mapped from 'cohesion' column)
  - Voice & Style     (mapped from avg of 'syntax' + 'phraseology' columns)
  - Conventions       (mapped from avg of 'grammar' + 'conventions' columns)

Also supports ASAP++ (rater1_trait1..4) and legacy single-score CSV formats.
"""

import os
import sys
import re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import joblib
import warnings
warnings.filterwarnings('ignore')

try:
    import textstat
except ImportError:
    textstat = None

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# Trait definitions
TRAITS = ['content', 'organization', 'voice', 'conventions']

TRAIT_LABELS = {
    'content':      'Content & Ideas',
    'organization': 'Organization',
    'voice':        'Voice & Style',
    'conventions':  'Conventions',
}

TRANSITION_WORDS = {
    'addition':   ['furthermore', 'moreover', 'additionally', 'also', 'besides', 'in addition'],
    'contrast':   ['however', 'nevertheless', 'on the other hand', 'although', 'despite', 'yet'],
    'conclusion': ['therefore', 'thus', 'consequently', 'as a result', 'in conclusion', 'in summary'],
    'sequence':   ['first', 'second', 'third', 'finally', 'next', 'then', 'lastly'],
    'example':    ['for example', 'for instance', 'such as', 'specifically', 'namely'],
}

RARE_WORD_LEN = 8


class EssayScorer:
    """
    Multi-trait XGBoost essay scorer.

    Trains and predicts 4 independent trait scores (0-100):
      content, organization, voice, conventions

    Each trait model uses the shared TF-IDF representation plus
    trait-specific linguistic feature vectors.
    """

    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=500,
            min_df=2,
            max_df=0.85,
            ngram_range=(1, 2),
            lowercase=True,
            stop_words='english',
        )
        self.models = {
            trait: xgb.XGBRegressor(
                n_estimators=300,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                gamma=1,
                min_child_weight=3,
                random_state=config.RANDOM_STATE,
                n_jobs=-1,
                verbosity=0,
            )
            for trait in TRAITS
        }
        self.scalers = {trait: StandardScaler() for trait in TRAITS}
        self.is_trained = False
        self.feature_names = []

    def _base_features(self, text):
        """Shared features used by all trait models (11 features)."""
        if not text or not text.strip():
            return np.zeros(11)
        words = text.split()
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        word_count = max(len(words), 1)
        sentence_count = max(len(sentences), 1)
        avg_word_len = np.mean([len(w) for w in words]) if words else 0
        avg_sent_len = word_count / sentence_count
        vocab_diversity = len(set(w.lower() for w in words)) / word_count
        complex_punct = text.count(';') + text.count(':') + text.count('--')
        comma_count = text.count(',')
        readability = 0.0
        if textstat:
            try:
                readability = min(textstat.flesch_kincaid_grade(text), 20) / 20
            except Exception:
                pass
        contractions = len([w for w in words if "'" in w])
        quotes = text.count('"') + text.count("'")
        return np.array([
            word_count / 1000,
            sentence_count / 50,
            avg_word_len,
            avg_sent_len / 30,
            vocab_diversity,
            complex_punct / sentence_count,
            comma_count / sentence_count,
            readability,
            contractions / max(word_count / 100, 1),
            quotes / max(word_count / 100, 1),
            len(text) / 10000,
        ])

    def _content_features(self, text):
        """Features reflecting content depth and idea development (5 features)."""
        words = text.lower().split()
        word_count = max(len(words), 1)
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        content_words = len([w for w in words if len(w) > 6]) / word_count
        long_words = len([w for w in words if len(w) >= RARE_WORD_LEN]) / word_count
        paragraphs = len([p for p in text.split('\n\n') if p.strip()])
        avg_sent_len = word_count / max(len(sentences), 1)
        vocab_diversity = len(set(words)) / word_count
        return np.array([
            content_words,
            long_words,
            min(paragraphs, 10) / 10,
            avg_sent_len / 40,
            vocab_diversity,
        ])

    def _organization_features(self, text):
        """Features reflecting logical structure and flow (10 features)."""
        text_lower = text.lower()
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        trans_counts = {}
        for cat, words_list in TRANSITION_WORDS.items():
            trans_counts[cat] = sum(1 for w in words_list if w in text_lower)
        total_transitions = sum(trans_counts.values())
        sent_count = max(len(sentences), 1)
        has_intro = int(any(w in text_lower[:300] for w in [
            'introduction', 'this essay', 'i will', 'in this', 'to begin', 'firstly',
        ]))
        has_conclusion = int(any(w in text_lower[-300:] for w in [
            'in conclusion', 'to conclude', 'in summary', 'therefore', 'finally', 'to sum up',
        ]))
        return np.array([
            trans_counts.get('contrast', 0) / sent_count,
            trans_counts.get('addition', 0) / sent_count,
            trans_counts.get('conclusion', 0) / sent_count,
            trans_counts.get('sequence', 0) / sent_count,
            trans_counts.get('example', 0) / sent_count,
            total_transitions / sent_count,
            has_intro,
            has_conclusion,
            min(len(paragraphs), 10) / 10,
            min(len(sentences), 50) / 50,
        ])

    def _voice_features(self, text):
        """Features reflecting style variety and rhetorical sophistication (7 features)."""
        words = text.split()
        word_count = max(len(words), 1)
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        sent_lengths = [len(s.split()) for s in sentences] if sentences else [0]
        sent_len_std = np.std(sent_lengths) / 30 if len(sent_lengths) > 1 else 0
        rhetorical_q = text.count('?') / max(len(sentences), 1)
        exclamations = text.count('!') / max(len(sentences), 1)
        passive = len(re.findall(r'\b(is|are|was|were|been|being)\s+\w+ed\b', text.lower()))
        passive_ratio = passive / max(len(sentences), 1)
        first_person = len(re.findall(r'\b(i|me|my|mine|myself|we|our|us)\b', text.lower())) / word_count
        rare_words = len([w for w in words if len(w) >= RARE_WORD_LEN]) / word_count
        similes = len(re.findall(r'\b(like|as)\s+\w+', text.lower())) / max(len(sentences), 1)
        return np.array([
            sent_len_std,
            rhetorical_q,
            exclamations,
            passive_ratio,
            first_person,
            rare_words,
            similes,
        ])

    def _conventions_features(self, text):
        """Features reflecting grammatical and mechanical accuracy (7 features)."""
        words = text.split()
        word_count = max(len(words), 1)
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        punct_density = len(re.findall(r'[.,;:!?\'"-]', text)) / word_count
        double_punct = min(len(re.findall(r'[.!?,]{2,}', text)), 10) / 10
        cap_errors = sum(1 for s in sentences if s and not s[0].isupper())
        cap_error_rate = cap_errors / max(len(sentences), 1)
        repeated_chars = min(len(re.findall(r'([a-zA-Z])\1{2,}', text)), 10) / 10
        contractions = len([w for w in words if "'" in w]) / word_count
        length_norm = min(word_count, 1000) / 1000
        comma_rate = min(text.count(',') / max(len(sentences), 1), 5) / 5
        return np.array([
            punct_density,
            double_punct,
            cap_error_rate,
            repeated_chars,
            contractions,
            length_norm,
            comma_rate,
        ])

    def _extract_all_features(self, texts, fit_tfidf=False):
        """Return a dict of per-trait feature matrices."""
        texts = list(texts)
        print("  Extracting TF-IDF features...")
        if fit_tfidf:
            tfidf = self.tfidf_vectorizer.fit_transform(texts).toarray()
        else:
            tfidf = self.tfidf_vectorizer.transform(texts).toarray()
        print("  Extracting trait-specific linguistic features...")
        base  = np.array([self._base_features(t) for t in texts])
        cont  = np.array([self._content_features(t) for t in texts])
        org   = np.array([self._organization_features(t) for t in texts])
        voice = np.array([self._voice_features(t) for t in texts])
        conv  = np.array([self._conventions_features(t) for t in texts])
        return {
            'content':      np.hstack([tfidf, base, cont]),
            'organization': np.hstack([tfidf, base, org]),
            'voice':        np.hstack([tfidf, base, voice]),
            'conventions':  np.hstack([tfidf, base, conv]),
        }

    def train(self, X_train, y_train_dict):
        """
        Train one XGBRegressor per trait.
        y_train_dict: dict mapping trait name to Series of 0-100 scores.
        """
        print("\nFitting TF-IDF and extracting features...")
        trait_features = self._extract_all_features(X_train, fit_tfidf=True)
        for trait in TRAITS:
            if trait not in y_train_dict:
                print(f"  Skipping '{TRAIT_LABELS[trait]}' (no labels)")
                continue
            print(f"\nTraining '{TRAIT_LABELS[trait]}'...")
            X = self.scalers[trait].fit_transform(trait_features[trait])
            y = y_train_dict[trait].values
            self.models[trait].fit(X, y)
            print(f"  Done.")
        self.is_trained = True
        print("\nAll trait models trained successfully.")

    def evaluate(self, X_test, y_test_dict):
        """Evaluate all trait models and print RMSE / R2 per trait."""
        print("\nEvaluating models on test set...")
        trait_features = self._extract_all_features(X_test, fit_tfidf=False)
        results = {}
        for trait in TRAITS:
            if trait not in y_test_dict:
                continue
            X = self.scalers[trait].transform(trait_features[trait])
            y_pred = self.models[trait].predict(X)
            y_true = y_test_dict[trait].values
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            r2 = r2_score(y_true, y_pred)
            print(f"  {TRAIT_LABELS[trait]:20s}  RMSE: {rmse:6.2f}   R2: {r2:.4f}")
            results[trait] = {'rmse': rmse, 'r2': r2}
        return results

    def predict(self, essay_text, prompt=''):
        """
        Predict all 4 trait scores for a single essay (0-100 scale).

        Returns dict with keys:
          score, score_content, score_organization, score_voice,
          score_conventions, confidence
        """
        if not self.is_trained:
            return None
        trait_features = self._extract_all_features([essay_text], fit_tfidf=False)
        scores = {}
        for trait in TRAITS:
            X = self.scalers[trait].transform(trait_features[trait])
            raw = float(self.models[trait].predict(X)[0])
            scores[trait] = max(0.0, min(100.0, raw))
        overall = float(np.mean(list(scores.values())))
        return {
            'score':              overall,
            'score_content':      scores['content'],
            'score_organization': scores['organization'],
            'score_voice':        scores['voice'],
            'score_conventions':  scores['conventions'],
            'confidence':         0.85,
        }

    def save(self, filepath):
        """Save all trait models, vectorizer, and scalers to a single .pkl file."""
        model_data = {
            'tfidf_vectorizer': self.tfidf_vectorizer,
            'scalers':          self.scalers,
            'models':           self.models,
            'feature_names':    self.feature_names,
            'multi_trait':      True,
        }
        joblib.dump(model_data, filepath)
        print(f"\nModel saved to: {filepath}")

    @staticmethod
    def load(filepath):
        """Load a saved multi-trait EssayScorer from disk."""
        model_data = joblib.load(filepath)
        scorer = EssayScorer()
        scorer.tfidf_vectorizer = model_data['tfidf_vectorizer']
        scorer.models           = model_data['models']
        scorer.scalers          = model_data['scalers']
        scorer.feature_names    = model_data.get('feature_names', [])
        scorer.is_trained       = True
        print(f"Multi-trait model loaded from: {filepath}")
        return scorer


def load_dataset(filepath):
    """Load dataset from CSV, TSV, or Excel."""
    if filepath.endswith('.tsv'):
        return pd.read_csv(filepath, sep='\t')
    elif filepath.endswith('.csv'):
        return pd.read_csv(filepath)
    elif filepath.endswith('.xlsx'):
        return pd.read_excel(filepath)
    else:
        raise ValueError(f"Unsupported file format: {filepath}")


def normalize_to_100(df, cols):
    """Scale each column to 0-100 range."""
    for col in cols:
        col_min = df[col].min()
        col_max = df[col].max()
        if col_max > col_min:
            df[col] = (df[col] - col_min) / (col_max - col_min) * 100.0
        else:
            df[col] = 50.0
    return df


def detect_dataset_format(df):
    """
    Detect dataset format from column names.
    Returns a mapping dict or None.
    """
    cols_lower = [c.lower() for c in df.columns]
    col_map = {c.lower(): c for c in df.columns}

    # PERSUADE 2.0 (discourse-level, needs deduplication)
    if all(c in cols_lower for c in ['essay_id', 'full_text', 'holistic_essay_score', 'discourse_type', 'discourse_effectiveness']):
        print("Detected: PERSUADE 2.0 format")
        return {
            'text':   col_map['full_text'],
            'format': 'persuade_2',
        }

    # Feedback Prize 2022
    if all(c in cols_lower for c in ['full_text', 'cohesion', 'vocabulary', 'grammar', 'conventions']):
        print("Detected: Feedback Prize 2022 format")
        syntax_col = col_map.get('syntax') or col_map.get('phraseology') or col_map['vocabulary']
        phras_col  = col_map.get('phraseology') or col_map.get('syntax') or col_map['vocabulary']
        return {
            'text':              col_map['full_text'],
            'content':           col_map['vocabulary'],
            'organization':      col_map['cohesion'],
            '_voice_a':          syntax_col,
            '_voice_b':          phras_col,
            'voice':             None,
            '_grammar':          col_map['grammar'],
            '_conventions_raw':  col_map['conventions'],
            'conventions':       None,
            'format':            'feedback_prize_2022',
        }

    # ASAP++ (rater1_trait1 ... rater1_trait4)
    trait_cols = sorted([col_map[c] for c in cols_lower if 'trait' in c])
    if 'essay' in cols_lower and trait_cols:
        print(f"Detected: ASAP++ format ({len(trait_cols)} trait columns)")
        return {
            'text':         col_map.get('essay', col_map.get('text')),
            'content':      trait_cols[0] if len(trait_cols) > 0 else None,
            'organization': trait_cols[1] if len(trait_cols) > 1 else None,
            'voice':        trait_cols[2] if len(trait_cols) > 2 else None,
            'conventions':  trait_cols[3] if len(trait_cols) > 3 else None,
            'format':       'asap_plus',
        }

    # Legacy single-score CSV
    text_col  = next((col_map[c] for c in cols_lower if c in ['essay', 'text', 'full_text', 'content']), None)
    score_col = next((col_map[c] for c in cols_lower if c in ['score', 'label', 'rating', 'domain1_score']), None)
    if text_col and score_col:
        print("Detected: Single-score format -- cloning score to all traits")
        return {
            'text': text_col,
            'content': score_col, 'organization': score_col,
            'voice': score_col,   'conventions':  score_col,
            'format': 'single_score',
        }

    return None


def load_persuade2(filepath):
    """
    Load PERSUADE 2.0 and convert to per-trait scored essay DataFrame.

    Derives:
      - content      : avg discourse_effectiveness of Claim + Evidence elements
      - organization : avg discourse_effectiveness of Lead + Concluding Statement elements
      - voice        : holistic_essay_score (mapped 1-6 → 0-100)
      - conventions  : holistic_essay_score (mapped 1-6 → 0-100)

    Returns a DataFrame with columns: full_text, content, organization, voice, conventions
    """
    print("Loading PERSUADE 2.0 (this may take a moment)...")
    df = pd.read_csv(filepath, low_memory=False)
    print(f"  Raw rows: {len(df)}")

    effectiveness_map = {'Effective': 1.0, 'Adequate': 0.6, 'Ineffective': 0.2}

    # Map discourse_effectiveness to numeric
    df['eff_num'] = df['discourse_effectiveness'].map(effectiveness_map)

    # Derive content score (Claim + Evidence)
    content_mask = df['discourse_type'].isin(['Claim', 'Evidence'])
    content_scores = (
        df[content_mask]
        .groupby('essay_id')['eff_num']
        .mean()
        .rename('content_raw')
    )

    # Derive organization score (Lead + Concluding Statement)
    org_mask = df['discourse_type'].isin(['Lead', 'Concluding Statement'])
    org_scores = (
        df[org_mask]
        .groupby('essay_id')['eff_num']
        .mean()
        .rename('org_raw')
    )

    # Deduplicate to essay level
    essays = df.drop_duplicates(subset='essay_id')[['essay_id', 'full_text', 'holistic_essay_score']].copy()
    essays = essays.dropna(subset=['full_text', 'holistic_essay_score'])
    essays['holistic_essay_score'] = pd.to_numeric(essays['holistic_essay_score'], errors='coerce')
    essays = essays.dropna(subset=['holistic_essay_score'])

    # Holistic → 0–100
    essays['holistic_norm'] = (essays['holistic_essay_score'] - 1) / 5.0 * 100.0

    # Join derived trait scores
    essays = essays.join(content_scores, on='essay_id')
    essays = essays.join(org_scores, on='essay_id')

    # Fill missing derived scores with holistic
    essays['content_raw']  = essays['content_raw'].fillna(0.5)  # neutral if no annotations
    essays['org_raw']      = essays['org_raw'].fillna(0.5)

    # Scale derived scores to 0–100
    essays['content']      = essays['content_raw'] * 100.0
    essays['organization'] = essays['org_raw'] * 100.0

    # Voice and Conventions from holistic (no annotation available)
    essays['voice']        = essays['holistic_norm']
    essays['conventions']  = essays['holistic_norm']

    result = essays[['full_text', 'content', 'organization', 'voice', 'conventions']].copy()
    result = result.dropna()
    print(f"  Unique essays after processing: {len(result)}")
    return result


def main():
    print("=" * 60)
    print("Essay Scoring -- Multi-Trait Training")
    print("=" * 60)

    os.makedirs(config.MODELS_DIR, exist_ok=True)
    data_dir = config.DATA_DIR

    print(f"\nLooking for training data in: {data_dir}")

    # ── 1. Load primary dataset (Feedback Prize 2022) ────────────────────────
    training_file = None
    for filename in ['train.csv', 'train.tsv', 'training_set_rel3.tsv', 'sample_training_data.csv', 'TRAINING.tsv']:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            training_file = filepath
            print(f"Found primary dataset: {filename}")
            break

    if not training_file:
        print(f"\nNo training data found in {data_dir}")
        print("\nFor multi-trait scoring, download the Feedback Prize 2022 dataset:")
        print("  https://www.kaggle.com/competitions/feedback-prize-english-language-learning/data")
        print(f"Place train.csv into: {data_dir}")
        return False

    try:
        df = load_dataset(training_file)
        print(f"\nLoaded {len(df)} rows")
        print(f"Columns: {list(df.columns)}")

        col_info = detect_dataset_format(df)
        if not col_info:
            print("Could not detect dataset format. Columns:", list(df.columns))
            return False

        text_col = col_info['text']
        df = df.dropna(subset=[text_col])
        df[text_col] = df[text_col].astype(str)

        # Build per-trait columns for Feedback Prize 2022
        if col_info['format'] == 'feedback_prize_2022':
            df['_voice_col'] = (
                pd.to_numeric(df[col_info['_voice_a']], errors='coerce') +
                pd.to_numeric(df[col_info['_voice_b']], errors='coerce')
            ) / 2
            col_info['voice'] = '_voice_col'
            df['_conv_col'] = (
                pd.to_numeric(df[col_info['_grammar']],         errors='coerce') +
                pd.to_numeric(df[col_info['_conventions_raw']], errors='coerce')
            ) / 2
            col_info['conventions'] = '_conv_col'

        trait_cols = {}
        for trait in TRAITS:
            col = col_info.get(trait)
            if col and col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df = df.dropna(subset=[col])
                trait_cols[trait] = col
            else:
                print(f"  Warning: no column for trait '{trait}' -- skipping")

        if not trait_cols:
            print("No usable trait columns found. Aborting.")
            return False

        df = normalize_to_100(df, list(trait_cols.values()))

        # ── 2. Check for PERSUADE 2.0 and combine ────────────────────────────
        persuade_file = None
        for fname in ['persuade_corpus_2.0_train.csv', 'persuade_train.csv']:
            fpath = os.path.join(data_dir, fname)
            if os.path.exists(fpath):
                persuade_file = fpath
                print(f"\nFound supplemental dataset: {fname}")
                break

        if persuade_file:
            try:
                persuade_df = load_persuade2(persuade_file)
                # Rename to match primary dataset columns
                persuade_df = persuade_df.rename(columns={
                    'full_text':     text_col,
                    'content':      trait_cols.get('content',      'content'),
                    'organization': trait_cols.get('organization', 'organization'),
                    'voice':        trait_cols.get('voice',        'voice'),
                    'conventions':  trait_cols.get('conventions',  'conventions'),
                })
                keep_cols = [text_col] + list(trait_cols.values())
                persuade_df = persuade_df[[c for c in keep_cols if c in persuade_df.columns]]

                before = len(df)
                df = pd.concat([df[keep_cols], persuade_df], ignore_index=True)
                df = df.dropna()
                print(f"  Combined: {before} (Feedback Prize) + {len(persuade_df)} (PERSUADE 2.0) = {len(df)} total essays")
            except Exception as e:
                print(f"  Warning: could not load PERSUADE 2.0 — {e}. Continuing with primary dataset only.")
        else:
            print("\nNo PERSUADE 2.0 dataset found — training on Feedback Prize only.")
            print("To add it, place persuade_corpus_2.0_train.csv in:", data_dir)

        print(f"\nFinal dataset: {len(df)} essays, {len(trait_cols)} traits")
        for trait, col in trait_cols.items():
            print(f"  {TRAIT_LABELS[trait]:20s}  ('{col}')  "
                  f"mean={df[col].mean():.1f}  std={df[col].std():.1f}")

        X_train, X_test = train_test_split(
            df[text_col],
            test_size=config.TEST_SIZE,
            random_state=config.RANDOM_STATE,
        )
        y_train_dict = {t: df.loc[X_train.index, c] for t, c in trait_cols.items()}
        y_test_dict  = {t: df.loc[X_test.index,  c] for t, c in trait_cols.items()}

        scorer = EssayScorer()
        scorer.train(X_train, y_train_dict)
        scorer.evaluate(X_test, y_test_dict)

        model_path = os.path.join(config.MODELS_DIR, 'essay_scorer.pkl')
        scorer.save(model_path)

        print("\nSample prediction:")
        sample = X_test.iloc[0]
        pred = scorer.predict(sample)
        print(f"  Overall:             {pred['score']:.1f}/100")
        for trait in TRAITS:
            print(f"  {TRAIT_LABELS[trait]:20s}: {pred[f'score_{trait}']:.1f}/100")

        print("\n" + "=" * 60)
        print("Multi-trait training complete!")
        print(f"Model saved to: {model_path}")
        print("Run 'python app.py' to start the API server.")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\nTraining error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
