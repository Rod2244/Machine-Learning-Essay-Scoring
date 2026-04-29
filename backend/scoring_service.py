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
                print(f"[ScoringService] rubric_id passed: {rubric_id}")
                print(f"[ScoringService] breakdown computed: {breakdown}")
            except Exception:
                pass
            
            # Generate feedback
            feedback = self._generate_feedback(score)
            
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
        Calculate deterministic score breakdown based on rubric type
        No randomness - same essay = same breakdown always
        """
        breakdown = {}
        
        try:
            from app import custom_rubrics

            # First, check in-memory custom rubrics (keys may be int or str)
            found_custom = None
            for k, v in custom_rubrics.items():
                if str(k) == str(rubric_id):
                    found_custom = v
                    break

            if found_custom is not None:
                custom_criteria = found_custom
                total_points = sum(c.get('points', 0) for c in custom_criteria)

                for criterion in custom_criteria:
                    criterion_name = criterion.get('name')
                    criterion_points = criterion.get('points', 0)

                    # Allocate points proportionally
                    criterion_score = int((score * criterion_points) / 100)
                    criterion_score = max(0, min(criterion_points, criterion_score))
                    breakdown[criterion_name] = criterion_score
            else:
                # If not in memory, try Supabase (user-created rubrics stored in DB)
                tried_db = False
                try:
                    from supabase_client import supabase_service
                    if supabase_service and getattr(supabase_service, 'client', None):
                        q = supabase_service.client.table('rubrics').select('criteria').eq('id', str(rubric_id)).execute()
                        if getattr(q, 'data', None):
                            db_criteria = q.data[0].get('criteria', [])
                            if db_criteria:
                                tried_db = True
                                for criterion in db_criteria:
                                    cname = criterion.get('name')
                                    cpoints = criterion.get('points', 0)
                                    cscore = int((score * cpoints) / 100)
                                    cscore = max(0, min(cpoints, cscore))
                                    breakdown[cname] = cscore
                except Exception:
                    tried_db = False

                if not tried_db:
                    # Default rubric types (fallback)
                    if str(rubric_id) == '2' or rubric_id == 2:  # Expository Essay
                        breakdown = {
                            "Clarity": int(score * 0.30),
                            "Organization": int(score * 0.25),
                            "Research": int(score * 0.25),
                            "Grammar": int(score * 0.20)
                        }
                    elif str(rubric_id) == '3' or rubric_id == 3:  # Narrative Essay
                        breakdown = {
                            "Storytelling": int(score * 0.30),
                            "Characters": int(score * 0.25),
                            "Engagement": int(score * 0.25),
                            "Language": int(score * 0.20)
                        }
                    elif str(rubric_id) == '4' or rubric_id == 4:  # Research Paper
                        breakdown = {
                            "Research": int(score * 0.30),
                            "Citations": int(score * 0.25),
                            "Analysis": int(score * 0.25),
                            "Academic Rigor": int(score * 0.20)
                        }
                    else:  # Argumentative Essay (default)
                        breakdown = {
                            "Thesis": int(score * 0.25),
                            "Evidence": int(score * 0.25),
                            "Structure": int(score * 0.30),
                            "Grammar": int(score * 0.20)
                        }
        except Exception:
            # Fallback if something unexpected fails
            breakdown = {
                "Thesis": int(score * 0.25),
                "Evidence": int(score * 0.25),
                "Structure": int(score * 0.30),
                "Grammar": int(score * 0.20)
            }
        
        return breakdown
    
    def _generate_feedback(self, score):
        """Generate feedback based on score"""
        if score >= 90:
            return "Excellent essay with outstanding organization, depth, and clarity"
        elif score >= 80:
            return "Very good essay with strong content and clear structure"
        elif score >= 70:
            return "Good essay with solid organization and comprehensive content"
        elif score >= 60:
            return "Satisfactory essay with adequate structure and content"
        elif score >= 50:
            return "Fair essay with some good elements but needs improvement"
        elif score >= 40:
            return "Essay needs significant improvement in organization and content"
        else:
            return "Essay requires major revisions to meet standards"
    
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

# Global instance
scoring_service = EssayScoringService()
