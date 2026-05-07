import os
import sys
from config import config
from topic_relevance_service import get_topic_relevance_service

# Add the scripts directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class EssayScoringService:
    def __init__(self):
        self.model_path = os.path.join(config.MODELS_DIR, 'essay_scorer.pkl')
        self.scorer = None
        self.topic_relevance_service = get_topic_relevance_service()
        self.load_model()
    
    def load_model(self):
        """Load the trained model on startup"""
        try:
            from scripts.train_model import EssayScorer
            self.scorer = EssayScorer.load(self.model_path)
            print(f"Model loaded from: {self.model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.scorer = None
    
    def score_essay(self, essay_text, prompt="", rubric_id=1):
        """
        Score an essay using the trained ML model (XGBoost with advanced features)
        
        Args:
            essay_text: The student's essay response
            prompt: The essay prompt/question
            rubric_id: ID of the rubric to use
            
        Returns:
            dict: Scoring results or error message
        """
        if not self.scorer:
            return {"success": False, "error": "Model not loaded"}
        
        if not essay_text or not essay_text.strip():
            return {"success": False, "error": "Empty essay text"}
        
        try:
            # Get per-trait ML predictions
            prediction = self.scorer.predict(essay_text)
            confidence = prediction['confidence']

            # Apply quality penalties — convert to a 0.0–1.0 multiplicative factor
            quality_penalty = self._calculate_quality_penalties(essay_text)
            quality_factor = max(0.0, 1.0 - quality_penalty / 100.0)

            # Get rubric-specific weights (used for logging only now)
            weights = self._get_rubric_weights(rubric_id)

            raw_trait_scores = {
                'content':      prediction.get('score_content',      prediction.get('score', 50)),
                'organization': prediction.get('score_organization', prediction.get('score', 50)),
                'voice':        prediction.get('score_voice',        prediction.get('score', 50)),
                'conventions':  prediction.get('score_conventions',  prediction.get('score', 50)),
            }

            overall_score = sum(raw_trait_scores[t] * w for t, w in weights.items())

            print(f"[ScoringService] Trait scores: {raw_trait_scores}")
            print(f"[ScoringService] Rubric weights (id={rubric_id}): {weights}")
            print(f"[ScoringService] Weighted score: {overall_score:.1f}, quality_factor: {quality_factor:.2f}")

            # Calculate topic relevance (if prompt provided)
            topic_relevance = self.calculate_topic_relevance(essay_text, prompt)

            # Convert topic relevance to a multiplicative factor
            if topic_relevance < 30:
                relevance_factor = 0.70
            elif topic_relevance < 60:
                relevance_factor = 0.85
            else:
                relevance_factor = 1.0

            # Single combined factor applied to all breakdown scores
            combined_factor = quality_factor * relevance_factor

            # Build breakdown — combined_factor scales all trait scores uniformly
            breakdown = self._build_breakdown_from_traits(prediction, rubric_id, combined_factor)

            # Total score = sum of breakdown (always consistent with what is displayed)
            score = max(0, min(100, sum(breakdown.values())))

            print(f"[ScoringService] rubric_id: {repr(rubric_id)}")
            print(f"[ScoringService] combined_factor: {combined_factor:.2f}  final score: {score}")
            print(f"[ScoringService] breakdown: {breakdown}")
            
            # Generate feedback based on rubric breakdown and per-trait scores
            feedback = self._generate_feedback(score, breakdown, prediction, rubric_id)
            
            result = {
                "success": True,
                "score": int(score),
                "category": int(score // 20),
                "confidence": float(confidence),
                "breakdown": breakdown,
                "feedback": feedback,
                "topic_relevance": float(topic_relevance)
            }
            
            # Save to Supabase if available
            try:
                from supabase_client import supabase_service
                
                essay_data = {
                    'student_id': 'anonymous',
                    'student_name': 'Anonymous Student',
                    'essay_title': prompt[:50] + '...' if len(prompt) > 50 else prompt or 'Untitled Essay',
                    'essay_type': self._get_essay_type_by_rubric_id(rubric_id),
                    'essay_prompt': prompt,
                    'essay_text': essay_text,
                    'total_score': int(score),
                    'max_score': 100,
                    'breakdown': breakdown,
                    'confidence': float(confidence),
                    'feedback': feedback,
                    'rubric_id': rubric_id,
                    'topic_relevance': float(topic_relevance),
                    'status': 'Graded',
                    'teacher_notes': ''
                }
            except Exception as e:
                print(f"⚠️ Failed to save to Supabase: {e}")
            
            return result
            
        except Exception as e:
            print(f"Scoring error: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": f"Scoring failed: {str(e)}"}
    
    # Rubric-specific trait weights (must sum to 1.0)
    # These define what each essay TYPE values most — changing rubric changes the score
    _RUBRIC_TRAIT_WEIGHTS = {
        1: {'content': 0.40, 'organization': 0.25, 'voice': 0.15, 'conventions': 0.20},  # Argumentative
        2: {'content': 0.35, 'organization': 0.30, 'voice': 0.15, 'conventions': 0.20},  # Expository
        3: {'content': 0.25, 'organization': 0.20, 'voice': 0.40, 'conventions': 0.15},  # Narrative
        4: {'content': 0.40, 'organization': 0.30, 'voice': 0.10, 'conventions': 0.20},  # Research Paper
    }
    # Title keyword → weights (for UUID-based Supabase rubrics)
    _RUBRIC_TITLE_WEIGHTS = {
        'argumentative': {'content': 0.40, 'organization': 0.25, 'voice': 0.15, 'conventions': 0.20},
        'expository':    {'content': 0.35, 'organization': 0.30, 'voice': 0.15, 'conventions': 0.20},
        'narrative':     {'content': 0.25, 'organization': 0.20, 'voice': 0.40, 'conventions': 0.15},
        'research':      {'content': 0.40, 'organization': 0.30, 'voice': 0.10, 'conventions': 0.20},
        'descriptive':   {'content': 0.30, 'organization': 0.25, 'voice': 0.30, 'conventions': 0.15},
        'persuasive':    {'content': 0.40, 'organization': 0.25, 'voice': 0.20, 'conventions': 0.15},
    }
    # Default weights for custom rubrics (balanced)
    _DEFAULT_TRAIT_WEIGHTS = {'content': 0.30, 'organization': 0.25, 'voice': 0.25, 'conventions': 0.20}

    def _get_rubric_weights(self, rubric_id):
        """
        Resolve trait weights for a rubric_id that may be an integer (1-4)
        or a UUID string from Supabase. Falls back to title-keyword matching.
        """
        # Integer ID (default rubrics 1-4)
        if str(rubric_id).isdigit():
            return self._RUBRIC_TRAIT_WEIGHTS.get(int(rubric_id), self._DEFAULT_TRAIT_WEIGHTS)

        # UUID — look up the rubric title in Supabase and match by keyword
        try:
            from supabase_client import supabase_service
            if supabase_service and getattr(supabase_service, 'admin_client', None):
                q = supabase_service.admin_client.table('rubrics') \
                    .select('title').eq('id', str(rubric_id)).execute()
                if getattr(q, 'data', None) and len(q.data) > 0:
                    title = q.data[0].get('title', '').lower()
                    for keyword, weights in self._RUBRIC_TITLE_WEIGHTS.items():
                        if keyword in title:
                            print(f"[ScoringService] Rubric '{title}' matched keyword '{keyword}'")
                            return weights
                    print(f"[ScoringService] Rubric '{title}' — no keyword match, using default weights")
        except Exception as e:
            print(f"[ScoringService] Could not resolve rubric weights: {e}")

        return self._DEFAULT_TRAIT_WEIGHTS

    # Keyword → trait mapping used to match rubric criterion names to ML trait scores
    _CRITERION_TRAIT_MAP = {
        # content
        'content': 'content', 'ideas': 'content', 'thesis': 'content',
        'argument': 'content', 'evidence': 'content', 'analysis': 'content',
        'research': 'content', 'clarity': 'content', 'depth': 'content',
        'vocabulary': 'content', 'storytelling': 'content', 'characters': 'content',
        'engagement': 'content',
        # organization
        'organization': 'organization', 'structure': 'organization',
        'flow': 'organization', 'coherence': 'organization', 'citations': 'organization',
        'sequence': 'organization', 'paragraph': 'organization',
        # voice
        'voice': 'voice', 'style': 'voice', 'language': 'voice',
        'tone': 'voice', 'expression': 'voice', 'academic': 'voice',
        'rigor': 'voice', 'syntax': 'voice', 'phraseology': 'voice',
        # conventions
        'grammar': 'conventions', 'conventions': 'conventions',
        'spelling': 'conventions', 'punctuation': 'conventions', 'mechanics': 'conventions',
    }

    # Ordered fallback trait assignment for rubric criteria (by position)
    _POSITION_TRAIT_ORDER = ['content', 'organization', 'voice', 'conventions']

    def _criterion_to_trait(self, criterion_name, position=0):
        """Map a rubric criterion name to one of the 4 ML trait scores."""
        name_lower = criterion_name.lower()
        for keyword, trait in self._CRITERION_TRAIT_MAP.items():
            if keyword in name_lower:
                return trait
        # Positional fallback
        return self._POSITION_TRAIT_ORDER[position % 4]

    def _build_breakdown_from_traits(self, prediction, rubric_id, relevance_factor=1.0):
        """
        Build the rubric breakdown using real per-trait ML scores.

        For each rubric criterion, the ML score for the best-matching trait
        is scaled by the criterion's max points and the topic-relevance factor.

        Supports:
          - Custom rubrics from Supabase (with 'levels' or flat 'points')
          - 4 default built-in rubrics
        """
        breakdown = {}

        # Per-trait scores (0-100) from the multi-trait model
        trait_scores = {
            'content':      prediction.get('score_content',      prediction.get('score', 50)),
            'organization': prediction.get('score_organization', prediction.get('score', 50)),
            'voice':        prediction.get('score_voice',        prediction.get('score', 50)),
            'conventions':  prediction.get('score_conventions',  prediction.get('score', 50)),
        }
        # Apply relevance penalty
        trait_scores = {t: max(0.0, min(100.0, v * relevance_factor)) for t, v in trait_scores.items()}

        def trait_score_to_points(trait, max_points):
            """Convert 0-100 trait score to actual rubric points."""
            return max(0, int(round(trait_scores[trait] / 100.0 * max_points)))

        try:
            # ── Try custom rubric from Supabase ───────────────────────────────
            criteria_with_levels = None
            try:
                from supabase_client import supabase_service
                if supabase_service and getattr(supabase_service, 'admin_client', None):
                    rubric_id_str = str(rubric_id)
                    q = supabase_service.admin_client.table('rubrics') \
                        .select('id, title, criteria').eq('id', rubric_id_str).execute()
                    if getattr(q, 'data', None) and len(q.data) > 0:
                        db_criteria = q.data[0].get('criteria', [])
                        if db_criteria:
                            criteria_with_levels = db_criteria
                            print(f"[ScoringService] Using Supabase rubric: {q.data[0].get('title')}")
            except Exception as e:
                print(f"[ScoringService] Supabase lookup failed: {e}")

            if criteria_with_levels:
                for i, criterion in enumerate(criteria_with_levels):
                    name       = criterion.get('name', f'Criterion {i+1}')
                    max_pts    = criterion.get('points', 25)
                    trait      = self._criterion_to_trait(name, i)
                    score_pts  = trait_score_to_points(trait, max_pts)
                    breakdown[name] = score_pts
                    print(f"[ScoringService] {name} → trait={trait}, {trait_scores[trait]:.1f}/100 → {score_pts}/{max_pts} pts")

            else:
                # ── Default built-in rubrics ──────────────────────────────────
                # Maps criterion name → (max_points, trait)
                default_rubrics = {
                    1: [  # Argumentative
                        ('Thesis',    25, 'content'),
                        ('Evidence',  25, 'content'),
                        ('Structure', 30, 'organization'),
                        ('Grammar',   20, 'conventions'),
                    ],
                    2: [  # Expository
                        ('Clarity',       30, 'content'),
                        ('Organization',  25, 'organization'),
                        ('Research',      25, 'content'),
                        ('Grammar',       20, 'conventions'),
                    ],
                    3: [  # Narrative
                        ('Storytelling', 30, 'content'),
                        ('Characters',   25, 'content'),
                        ('Engagement',   25, 'voice'),
                        ('Language',     20, 'voice'),
                    ],
                    4: [  # Research Paper
                        ('Research',  30, 'content'),
                        ('Citations', 25, 'organization'),
                        ('Analysis',  25, 'content'),
                        ('Rigor',     20, 'voice'),
                    ],
                }

                rubric_key = int(rubric_id) if str(rubric_id).isdigit() else 1
                rubric_template = default_rubrics.get(rubric_key, default_rubrics[1])

                for name, max_pts, trait in rubric_template:
                    score_pts = trait_score_to_points(trait, max_pts)
                    breakdown[name] = score_pts
                    print(f"[ScoringService] {name} → trait={trait}, {trait_scores[trait]:.1f}/100 → {score_pts}/{max_pts} pts")

        except Exception as e:
            print(f"[ScoringService] Error building breakdown: {e}")
            import traceback
            traceback.print_exc()
            breakdown = {'Content': 18, 'Organization': 18, 'Voice': 14, 'Conventions': 14}

        print(f"[ScoringService] Final breakdown: {breakdown}")
        return breakdown
    
    # Trait-specific improvement tips
    _TRAIT_TIPS = {
        'content': [
            "Develop your main argument with more specific evidence and examples.",
            "Ensure every paragraph directly supports your central thesis.",
            "Add data, quotes, or real-world examples to strengthen your ideas.",
        ],
        'organization': [
            "Use transition words (however, furthermore, in conclusion) to connect ideas.",
            "Make sure your essay has a clear introduction, body paragraphs, and conclusion.",
            "Each paragraph should focus on one main idea with a clear topic sentence.",
        ],
        'voice': [
            "Vary your sentence lengths to create a more engaging rhythm.",
            "Use more precise and sophisticated vocabulary to strengthen your voice.",
            "Adjust your tone to suit your audience — formal for academic, expressive for narrative.",
        ],
        'conventions': [
            "Proofread for grammar errors, especially subject-verb agreement.",
            "Check punctuation at the end of every sentence.",
            "Avoid repetitive word choices — use a thesaurus to diversify your language.",
        ],
    }

    def _generate_feedback(self, score, breakdown=None, prediction=None, rubric_id=1):
        """
        Generate detailed, trait-specific feedback tailored to the rubric type.

        Args:
            score:      Overall score (0-100)
            breakdown:  Dict of criterion -> points
            prediction: Raw per-trait prediction dict from EssayScorer.predict()
            rubric_id:  Active rubric ID (affects which traits to emphasise in feedback)
        """
        weights = self._get_rubric_weights(rubric_id)

        # Find the top-weighted trait for this rubric (what the rubric cares about most)
        primary_trait = max(weights, key=weights.get)
        trait_label_map = {
            'content': 'Content & Ideas',
            'organization': 'Organization',
            'voice': 'Voice & Style',
            'conventions': 'Conventions',
        }
        rubric_names = {1: 'Argumentative', 2: 'Expository', 3: 'Narrative', 4: 'Research Paper'}
        rubric_key = int(rubric_id) if str(rubric_id).isdigit() else 0
        if rubric_key in rubric_names:
            rubric_name = rubric_names[rubric_key]
        else:
            # Try to get title from Supabase for UUID rubrics
            rubric_name = 'Essay'
            try:
                from supabase_client import supabase_service
                if supabase_service and getattr(supabase_service, 'admin_client', None):
                    q = supabase_service.admin_client.table('rubrics') \
                        .select('title').eq('id', str(rubric_id)).execute()
                    if getattr(q, 'data', None) and len(q.data) > 0:
                        rubric_name = q.data[0].get('title', 'Essay')
            except Exception:
                pass

        if score >= 90:
            overall_level = "Excellent"
        elif score >= 80:
            overall_level = "Very Good"
        elif score >= 70:
            overall_level = "Good"
        elif score >= 60:
            overall_level = "Satisfactory"
        elif score >= 50:
            overall_level = "Fair"
        elif score >= 40:
            overall_level = "Needs Improvement"
        else:
            overall_level = "Requires Revision"

        parts = [f"Overall: {overall_level} ({round(score)}/100)."]

        # Trait-level analysis from ML prediction
        if prediction and isinstance(prediction, dict):
            try:
                trait_scores = {
                    'Content & Ideas':  prediction.get('score_content',      score),
                    'Organization':     prediction.get('score_organization', score),
                    'Voice & Style':    prediction.get('score_voice',        score),
                    'Conventions':      prediction.get('score_conventions',  score),
                }
                trait_key_map = {
                    'Content & Ideas': 'content',
                    'Organization':    'organization',
                    'Voice & Style':   'voice',
                    'Conventions':     'conventions',
                }

                # Highlight primary trait performance for this rubric
                primary_label = trait_label_map[primary_trait]
                primary_score = trait_scores.get(primary_label, score)
                _article = 'an' if rubric_name and rubric_name[0].lower() in 'aeiou' else 'a'
                parts.append(
                    f"For {_article} {rubric_name}, {primary_label} is most important "
                    f"({int(weights[primary_trait]*100)}% weight): {primary_score:.0f}/100."
                )

                sorted_traits = sorted(trait_scores.items(), key=lambda x: x[1], reverse=True)
                strongest_label, strongest_val = sorted_traits[0]
                weakest_label,   weakest_val   = sorted_traits[-1]

                if strongest_val - weakest_val > 8:
                    parts.append(f"Weakest area: {weakest_label} ({weakest_val:.0f}/100).")
                    tip_key = trait_key_map.get(weakest_label, 'content')
                    tip = self._TRAIT_TIPS[tip_key][0]
                    parts.append(f"Tip: {tip}")

                if score < 60:
                    for label, val in sorted_traits[-2:]:
                        if val < 60:
                            tip_key = trait_key_map.get(label, 'content')
                            parts.append(f"{label}: {self._TRAIT_TIPS[tip_key][1]}")
            except Exception as e:
                print(f"Error generating trait feedback: {e}")

        elif breakdown and isinstance(breakdown, dict):
            # Fallback: use breakdown points if no prediction dict
            sorted_criteria = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
            if sorted_criteria:
                parts.append(f"Strongest area: {sorted_criteria[0][0]} ({sorted_criteria[0][1]} pts).")
            if len(sorted_criteria) > 1 and sorted_criteria[0][1] - sorted_criteria[-1][1] > 3:
                parts.append(f"Needs improvement: {sorted_criteria[-1][0]} ({sorted_criteria[-1][1]} pts).")

        if score >= 80:
            parts.append("Keep up this level of quality.")
        elif score >= 60:
            parts.append("Focus on improving the weaker areas to raise your score.")
        else:
            parts.append("Significant improvement is needed across multiple areas.")

        return " ".join(parts)
    
    def _get_essay_type_by_rubric_id(self, rubric_id):
        """Get essay type name by rubric ID"""
        rubric_types = {
            1: 'Argumentative Essay',
            2: 'Expository Essay',
            3: 'Narrative Essay',
            4: 'Research Paper'
        }
        return rubric_types.get(rubric_id, 'Essay')


    def calculate_topic_relevance(self, essay_text, essay_prompt):
        """
        Calculate how relevant the essay is to the given prompt/topic using semantic embeddings.
        Returns a score from 0-100.
        
        Uses semantic similarity analysis which understands meaning beyond keywords.
        """
        return self.topic_relevance_service.calculate_semantic_relevance(
            essay_text, 
            essay_prompt
        )
    
    def _calculate_quality_penalties(self, essay_text):
        """
        Calculate quality penalties based on essay characteristics
        Returns the total penalty to subtract from ML score
        
        Checks for:
        - Very short essays (< 50 words)
        - Poor grammar patterns
        - Incomplete sentences
        - Lack of structure/paragraphs
        """
        penalty = 0
        
        # Check essay length
        words = essay_text.strip().split()
        word_count = len(words)
        
        if word_count < 20:
            penalty += 50  # Severe penalty for extremely short essays
            print(f"[QualityCheck] Very short essay ({word_count} words) → +50 penalty")
        elif word_count < 50:
            penalty += 30  # Major penalty for short essays
            print(f"[QualityCheck] Short essay ({word_count} words) → +30 penalty")
        elif word_count < 100:
            penalty += 10  # Minor penalty for essays under 100 words
            print(f"[QualityCheck] Moderately short essay ({word_count} words) → +10 penalty")
        
        # Check for basic paragraph structure (should have multiple periods/line breaks)
        sentences = essay_text.split('.')
        sentence_count = len([s for s in sentences if s.strip()])
        
        if sentence_count < 3:
            penalty += 20  # Penalty for very few sentences
            print(f"[QualityCheck] Few sentences ({sentence_count}) → +20 penalty")
        
        # Check for capitalization issues (poor grammar indicator)
        lines = essay_text.split('\n')
        uncapitalized_lines = 0
        for line in lines:
            line_stripped = line.strip()
            if line_stripped and not line_stripped[0].isupper():
                uncapitalized_lines += 1
        
        if uncapitalized_lines > len(lines) * 0.3:  # More than 30% uncapitalized
            penalty += 15
            print(f"[QualityCheck] Poor capitalization ({uncapitalized_lines}/{len(lines)} lines) → +15 penalty")
        
        # Check for common grammar mistakes
        grammar_issues = 0
        
        # Check for "cause" instead of "because"
        if ' cause ' in essay_text.lower() and ' because ' not in essay_text.lower():
            grammar_issues += 1
        
        # Check for missing spaces after punctuation (common error)
        if '..' in essay_text or ',,' in essay_text or '???' in essay_text:
            grammar_issues += 2
        
        # Check for repeated single character (common typo)
        import re
        repeated_chars = len(re.findall(r'([a-z])\1{2,}', essay_text.lower()))
        grammar_issues += repeated_chars
        
        if grammar_issues > 0:
            penalty += min(15, grammar_issues * 5)
            print(f"[QualityCheck] Grammar issues detected ({grammar_issues}) → +{min(15, grammar_issues * 5)} penalty")
        
        # Check for low word diversity (repetitive writing)
        if word_count > 0:
            unique_words = len(set(w.lower() for w in words))
            word_diversity_ratio = unique_words / word_count
            
            if word_diversity_ratio < 0.4:  # Less than 40% unique words
                penalty += 15
                print(f"[QualityCheck] Low word diversity ({word_diversity_ratio:.1%}) → +15 penalty")
        
        print(f"[QualityCheck] Total quality penalty: {penalty} points")
        return penalty

# Global instance
scoring_service = EssayScoringService()
