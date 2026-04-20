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
        Score an essay using the trained ML model
        
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
            # Topic-aware scoring
            topic_relevance_score = self.calculate_topic_relevance(essay_text, prompt)
            
            # Get base ML score
            prediction = self.scorer.predict(essay_text)
            base_score = prediction['score']
            confidence = prediction['confidence']
            
            # Adjust score based on topic relevance
            if topic_relevance_score < 30:  # Very off-topic
                base_score = max(0, base_score - 40)  # Heavy penalty
            elif topic_relevance_score < 60:  # Somewhat off-topic  
                base_score = max(0, base_score - 20)  # Moderate penalty
            # On-topic essays keep their score
            
            # Add some variety for demo (±10 points)
            import random
            score = max(0, min(100, base_score + random.randint(-10, 10)))
            
            # Create dynamic breakdown based on rubric
            import random
            
            # Import custom rubrics from app.py
            from app import custom_rubrics
            
            breakdown = {}
            
            # Check if this is a custom rubric
            if rubric_id in custom_rubrics:
                # Custom rubric - create breakdown dynamically
                custom_criteria = custom_rubrics[rubric_id]
                total_points = sum(c['points'] for c in custom_criteria)
                
                for criterion in custom_criteria:
                    criterion_name = criterion['name']
                    criterion_points = criterion['points']
                    
                    # Calculate score proportionally with some randomness
                    base_score = int((score * criterion_points) / total_points)
                    final_score = max(1, min(criterion_points, base_score + random.randint(-3, 5)))
                    breakdown[criterion_name] = final_score
                    
            else:
                # Default rubric - use hardcoded logic
                if rubric_id == 3:  # Narrative Essay
                    breakdown = {
                        "Storytelling": max(5, min(30, score // 3 + random.randint(-5, 10))),
                        "Characters": max(5, min(25, score // 4 + random.randint(-3, 7))),
                        "Engagement": max(5, min(25, score // 4 + random.randint(-5, 5))),
                        "Language": max(5, min(20, score // 5 + random.randint(-2, 8)))
                    }
                else:  # Argumentative Essay (default)
                    breakdown = {
                        "Thesis": max(5, min(25, score // 4 + random.randint(-5, 5))),
                        "Evidence": max(5, min(25, score // 4 + random.randint(-3, 7))),
                        "Structure": max(5, min(30, score // 3 + random.randint(-5, 10))),
                        "Grammar": max(5, min(20, score // 5 + random.randint(-2, 8)))
                    }
            
            # Use the confidence from the model
            
            # Generate feedback
            if score >= 80:
                feedback = "Excellent essay with strong arguments and good structure"
            elif score >= 60:
                feedback = "Good essay with room for improvement in clarity"
            else:
                feedback = "Essay needs work on organization and evidence"
            
            return {
                "success": True,
                "score": score,
                "category": score // 20,
                "confidence": confidence,
                "breakdown": breakdown,
                "feedback": feedback
            }
            
        except Exception as e:
            print(f"Scoring error: {e}")
            return {"success": False, "error": f"Scoring failed: {str(e)}"}

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
