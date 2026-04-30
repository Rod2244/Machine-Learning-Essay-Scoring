import os
import sys
from config import config

# Add the scripts directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class EssayScoringService:
    def __init__(self):
        self.model_path = os.path.join(config.MODELS_DIR, 'essay_scorer.pkl')
        self.scorer = None
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
            # Get ML model prediction
            prediction = self.scorer.predict(essay_text)
            base_score = prediction['score']
            confidence = prediction['confidence']
            
            # Apply quality checks and penalties
            quality_penalty = self._calculate_quality_penalties(essay_text)
            base_score = max(0, base_score - quality_penalty)
            
            print(f"[ScoringService] Base ML score: {prediction['score']}")
            print(f"[ScoringService] Quality penalty: {quality_penalty}")
            print(f"[ScoringService] Score after quality check: {base_score}")
            
            # Calculate topic relevance (if prompt provided)
            topic_relevance = self.calculate_topic_relevance(essay_text, prompt)
            
            # Adjust score based on topic relevance
            score = base_score
            if topic_relevance < 30:  # Very off-topic
                score = max(0, score - 30)  # Penalize significantly
            elif topic_relevance < 60:  # Somewhat off-topic
                score = max(0, score - 15)  # Moderate penalty
            # On-topic essays keep their score
            
            # Ensure score is in valid range
            score = max(0, min(100, score))
            
            # Calculate breakdown based on score (deterministic, no randomness)
            breakdown = self._calculate_breakdown(score, rubric_id)

            # DEBUG: log rubric_id and breakdown for troubleshooting custom rubrics
            try:
                print(f"[ScoringService] ===== SCORING COMPLETE =====")
                print(f"[ScoringService] rubric_id passed: {repr(rubric_id)} (type: {type(rubric_id).__name__})")
                print(f"[ScoringService] ML score: {score}")
                print(f"[ScoringService] breakdown computed: {breakdown}")
                print(f"[ScoringService] ===== END SCORING =====")
            except Exception:
                pass
            
            # Generate feedback based on rubric breakdown
            feedback = self._generate_feedback(score, breakdown)
            
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
    
    def _calculate_breakdown(self, score, rubric_id):
        """
        Calculate score breakdown based on rubric scoring levels
        Maps 0-100 ML score to appropriate rubric level (Beginning/Developing/Proficient/Excellent)
        for each criterion and returns actual points from the rubric definition
        
        Score Range to Level Mapping:
        - 0-25:   Beginning (worst performance)
        - 26-50:  Developing (below average)
        - 51-75:  Proficient (average to good)
        - 76-100: Excellent (best performance)
        """
        breakdown = {}
        
        try:
            # Map score to performance level
            def get_performance_level(score):
                if score <= 25:
                    return "Beginning"
                elif score <= 50:
                    return "Developing"
                elif score <= 75:
                    return "Proficient"
                else:
                    return "Excellent"
            
            performance_level = get_performance_level(score)
            print(f"[ScoringService] ML Score: {score} → Performance Level: {performance_level}")
            print(f"[ScoringService] Looking for rubric_id: {repr(rubric_id)} (type: {type(rubric_id).__name__})")
            
            # Try to get rubric with levels from Supabase (user-created rubrics)
            criteria_with_levels = None
            try:
                from supabase_client import supabase_service
                if supabase_service and getattr(supabase_service, 'admin_client', None):
                    # Use admin client to bypass RLS
                    rubric_id_str = str(rubric_id)
                    print(f"[ScoringService] Querying Supabase for rubric_id: {repr(rubric_id_str)}")
                    q = supabase_service.admin_client.table('rubrics').select('id, title, criteria').eq('id', rubric_id_str).execute()
                    print(f"[ScoringService] Supabase query result: {q.data if hasattr(q, 'data') else 'NO DATA ATTR'}")
                    if getattr(q, 'data', None) and len(q.data) > 0:
                        print(f"[ScoringService] ✅ Found rubric in Supabase! Title: {q.data[0].get('title', 'Unknown')}")
                        db_criteria = q.data[0].get('criteria', [])
                        if db_criteria and len(db_criteria) > 0 and 'levels' in db_criteria[0]:
                            criteria_with_levels = db_criteria
                            print(f"[ScoringService] ✅ Found {len(db_criteria)} criteria with levels")
                        else:
                            print(f"[ScoringService] ⚠️ Criteria found but no levels in first criterion")
                    else:
                        print(f"[ScoringService] ⚠️ No rubric found in Supabase for ID: {rubric_id_str}")
            except Exception as e:
                print(f"[ScoringService] ❌ Error fetching from Supabase: {e}")
                import traceback
                traceback.print_exc()
            
            # If we have criteria with levels, use them
            if criteria_with_levels:
                for criterion in criteria_with_levels:
                    criterion_name = criterion.get('name', 'Unknown')
                    levels = criterion.get('levels', [])
                    
                    if not levels:
                        # Fallback if no levels defined
                        criterion_points = criterion.get('points', 0)
                        criterion_score = int((score * criterion_points) / 100)
                        breakdown[criterion_name] = max(0, min(criterion_points, criterion_score))
                        continue
                    
                    # Find the level that matches our performance level
                    selected_level = None
                    for level in levels:
                        if level.get('label', '').strip() == performance_level:
                            selected_level = level
                            break
                    
                    if selected_level:
                        # Use the actual points from the rubric level
                        criterion_score = selected_level.get('score', 0)
                        print(f"[ScoringService] {criterion_name}: {performance_level} → {criterion_score} points")
                    else:
                        # Fallback: use proportional if level not found
                        criterion_points = criterion.get('points', 0)
                        criterion_score = int((score * criterion_points) / 100)
                        print(f"[ScoringService] {criterion_name}: Level not found, using proportional → {criterion_score} points")
                    
                    breakdown[criterion_name] = max(0, criterion_score)
            else:
                # Fallback: use default rubrics if no custom rubric found
                print(f"[ScoringService] No custom rubric found, using default rubric for ID: {rubric_id}")
                
                # Default rubric definitions with levels
                default_rubrics = {
                    1: {  # Argumentative Essay
                        'Thesis': {'Beginning': 5, 'Developing': 12, 'Proficient': 18, 'Excellent': 25},
                        'Evidence': {'Beginning': 5, 'Developing': 12, 'Proficient': 18, 'Excellent': 25},
                        'Structure': {'Beginning': 6, 'Developing': 15, 'Proficient': 23, 'Excellent': 30},
                        'Grammar': {'Beginning': 4, 'Developing': 10, 'Proficient': 15, 'Excellent': 20}
                    },
                    2: {  # Expository Essay
                        'Clarity': {'Beginning': 6, 'Developing': 15, 'Proficient': 22, 'Excellent': 30},
                        'Organization': {'Beginning': 5, 'Developing': 12, 'Proficient': 18, 'Excellent': 25},
                        'Research': {'Beginning': 5, 'Developing': 12, 'Proficient': 18, 'Excellent': 25},
                        'Grammar': {'Beginning': 4, 'Developing': 10, 'Proficient': 15, 'Excellent': 20}
                    },
                    3: {  # Narrative Essay
                        'Storytelling': {'Beginning': 6, 'Developing': 15, 'Proficient': 22, 'Excellent': 30},
                        'Characters': {'Beginning': 5, 'Developing': 12, 'Proficient': 18, 'Excellent': 25},
                        'Engagement': {'Beginning': 5, 'Developing': 12, 'Proficient': 18, 'Excellent': 25},
                        'Language': {'Beginning': 4, 'Developing': 10, 'Proficient': 15, 'Excellent': 20}
                    },
                    4: {  # Research Paper
                        'Research': {'Beginning': 6, 'Developing': 15, 'Proficient': 22, 'Excellent': 30},
                        'Citations': {'Beginning': 5, 'Developing': 12, 'Proficient': 18, 'Excellent': 25},
                        'Analysis': {'Beginning': 5, 'Developing': 12, 'Proficient': 18, 'Excellent': 25},
                        'Academic Rigor': {'Beginning': 4, 'Developing': 10, 'Proficient': 15, 'Excellent': 20}
                    }
                }
                
                # Get the appropriate default rubric (convert rubric_id to int)
                rubric_key = int(rubric_id) if isinstance(rubric_id, (int, str)) and str(rubric_id).isdigit() else 1
                rubric_template = default_rubrics.get(rubric_key, default_rubrics[1])
                
                # Apply the performance level to all criteria
                for criterion_name, levels_dict in rubric_template.items():
                    criterion_score = levels_dict.get(performance_level, levels_dict.get('Proficient', 0))
                    breakdown[criterion_name] = criterion_score
                    print(f"[ScoringService] {criterion_name}: {performance_level} → {criterion_score} points")
        
        except Exception as e:
            print(f"[ScoringService] Error in _calculate_breakdown: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to default
            breakdown = {
                "Thesis": 18,
                "Evidence": 18,
                "Structure": 23,
                "Grammar": 15
            }
        
        print(f"[ScoringService] Final breakdown: {breakdown}")
        return breakdown
    
    def _generate_feedback(self, score, breakdown=None):
        """
        Generate detailed feedback based on score and rubric breakdown
        
        Args:
            score: Overall score (0-100)
            breakdown: Dictionary of criterion -> points breakdown
            
        Returns:
            Detailed feedback that references specific rubric criteria
        """
        # Determine overall performance level
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
        
        # If we have breakdown data, create detailed feedback
        if breakdown and isinstance(breakdown, dict):
            try:
                # Find strengths (highest scoring criteria)
                sorted_criteria = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
                
                # Identify weak and strong areas
                strongest = sorted_criteria[0] if sorted_criteria else None
                weakest = sorted_criteria[-1] if sorted_criteria else None
                
                # Build feedback mentioning specific criteria
                feedback_parts = [f"Overall: {overall_level} essay (Score: {score}/100)."]
                
                if strongest:
                    feedback_parts.append(f"Strongest area: {strongest[0]} ({strongest[1]} points).")
                
                if weakest and len(sorted_criteria) > 1:
                    # Only mention weakest if it's significantly lower than strongest
                    if strongest[1] - weakest[1] > 3:
                        feedback_parts.append(f"Needs improvement: {weakest[0]} ({weakest[1]} points).")
                
                # Add actionable suggestions based on score
                if score >= 80:
                    feedback_parts.append("Maintain this level of quality.")
                elif score >= 60:
                    feedback_parts.append("Focus on improving the weaker criteria to raise your score.")
                else:
                    feedback_parts.append("Significant improvement needed across multiple criteria.")
                
                return " ".join(feedback_parts)
            except Exception as e:
                print(f"Error generating detailed feedback: {e}")
        
        # Fallback to simple feedback if breakdown unavailable
        if score >= 90:
            return "Excellent essay with outstanding organization, depth, and clarity."
        elif score >= 80:
            return "Very good essay with strong content and clear structure."
        elif score >= 70:
            return "Good essay with solid organization and comprehensive content."
        elif score >= 60:
            return "Satisfactory essay with adequate structure and content."
        elif score >= 50:
            return "Fair essay with some good elements but needs improvement."
        elif score >= 40:
            return "Essay needs significant improvement in organization and content."
        else:
            return "Essay requires major revisions to meet standards."
    
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
        Calculate how relevant the essay is to the given prompt/topic
        Returns a score from 0-100
        """
        if not essay_prompt or essay_prompt.strip() == "":
            return 80  # Default score if no prompt provided
        
        # Extract key topic words from prompt
        prompt_words = set(essay_prompt.lower().split())
        essay_words = set(essay_text.lower().split())
        
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'}
        
        prompt_words = prompt_words - common_words
        essay_words = essay_words - common_words
        
        # Calculate word overlap
        matching_words = prompt_words.intersection(essay_words)
        
        # Base relevance from word overlap
        if len(prompt_words) == 0:
            word_relevance = 50
        else:
            word_relevance = (len(matching_words) / len(prompt_words)) * 60
        
        # Bonus for longer essays (assume more content = more likely on-topic)
        length_bonus = min(20, len(essay_text.split()) / 50)
        
        # Bonus for related concepts (simple keyword matching)
        related_bonus = 0
        topic_keywords = {
            'climate': ['environment', 'weather', 'temperature', 'warming', 'carbon', 'emissions', 'greenhouse'],
            'technology': ['digital', 'computer', 'internet', 'software', 'apps', 'devices', 'innovation'],
            'education': ['school', 'learning', 'students', 'teachers', 'knowledge', 'study', 'academic'],
            'health': ['medical', 'doctor', 'hospital', 'medicine', 'disease', 'treatment', 'patient'],
            'economy': ['money', 'business', 'market', 'financial', 'economic', 'trade', 'investment']
        }
        
        for topic, keywords in topic_keywords.items():
            if topic in essay_prompt.lower():
                found_keywords = sum(1 for keyword in keywords if keyword in essay_text.lower())
                related_bonus += min(20, found_keywords * 4)
        
        total_relevance = word_relevance + length_bonus + related_bonus
        return min(100, max(0, total_relevance))
    
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
