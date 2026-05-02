"""
Enhanced Topic Relevance Detection using Semantic Embeddings
Uses sentence-transformers for semantic similarity instead of simple keyword matching
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from config import config


class TopicRelevanceService:
    """
    Advanced topic relevance detection using semantic embeddings.
    Leverages pre-trained sentence transformers to understand essay content
    in context, not just keyword matching.
    """
    
    def __init__(self):
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the sentence transformer model on startup"""
        try:
            from sentence_transformers import SentenceTransformer
            # Use lightweight model for fast inference
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✓ Semantic embedding model loaded successfully")
        except ImportError:
            print("⚠️  sentence-transformers not installed. Falling back to keyword matching.")
            self.model = None
        except Exception as e:
            print(f"⚠️  Error loading semantic model: {e}. Falling back to keyword matching.")
            self.model = None
    
    def calculate_semantic_relevance(self, essay_text, essay_prompt):
        """
        Calculate topic relevance using semantic similarity
        
        Args:
            essay_text: The student's essay
            essay_prompt: The essay prompt/topic
            
        Returns:
            float: Relevance score 0-100
        """
        if not essay_prompt or essay_prompt.strip() == "":
            return 80  # Default if no prompt
        
        if not self.model:
            return self._fallback_keyword_relevance(essay_text, essay_prompt)
        
        try:
            # Split essay into chunks for better semantic understanding
            sentences = self._split_into_sentences(essay_text)
            
            if not sentences:
                return 0
            
            # Get embeddings
            prompt_embedding = self.model.encode(essay_prompt, convert_to_numpy=True)
            essay_embeddings = self.model.encode(sentences, convert_to_numpy=True)
            
            # Calculate similarity for each sentence to the prompt
            similarities = cosine_similarity(
                [prompt_embedding],
                essay_embeddings
            )[0]
            
            # Use multiple scoring metrics:
            # 1. Max similarity (best sentence match)
            max_similarity = float(np.max(similarities))
            
            # 2. Mean similarity (overall relevance)
            mean_similarity = float(np.mean(similarities))
            
            # 3. Percentage of sentences above relevance threshold
            threshold = 0.3
            relevant_sentences = float(np.sum(similarities > threshold)) / len(similarities)
            
            # Combine metrics (weighted average)
            # - Mean similarity: 50% weight (overall consistency)
            # - Max similarity: 30% weight (peak relevance)
            # - Relevant sentence ratio: 20% weight (breadth of relevance)
            combined_score = (
                mean_similarity * 0.5 +
                max_similarity * 0.3 +
                relevant_sentences * 0.2
            )
            
            # Convert from 0-1 range to 0-100
            relevance_score = combined_score * 100
            
            # Apply bonus for essay length (more content generally = more thorough coverage)
            word_count = len(essay_text.split())
            if word_count > 200:
                relevance_score = min(100, relevance_score + 5)
            elif word_count < 50:
                relevance_score = max(0, relevance_score - 20)
            
            print(f"[TopicRelevance] Semantic analysis:")
            print(f"  - Max similarity: {max_similarity:.3f}")
            print(f"  - Mean similarity: {mean_similarity:.3f}")
            print(f"  - Relevant sentences: {relevant_sentences:.1%}")
            print(f"  - Combined score: {relevance_score:.1f}/100")
            
            return float(max(0, min(100, relevance_score)))
            
        except Exception as e:
            print(f"⚠️  Error in semantic relevance calculation: {e}")
            return self._fallback_keyword_relevance(essay_text, essay_prompt)
    
    def _split_into_sentences(self, text):
        """Split text into sentences for semantic analysis"""
        # Split on periods, exclamation marks, and question marks
        import re
        
        # Simple sentence splitter
        sentences = re.split(r'[.!?]+', text)
        
        # Clean up and filter short fragments
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        return sentences if sentences else [text]
    
    def _fallback_keyword_relevance(self, essay_text, essay_prompt):
        """
        Fallback to keyword-based relevance if semantic model unavailable
        """
        if not essay_prompt or essay_prompt.strip() == "":
            return 80
        
        # Extract key words from prompt
        prompt_words = set(essay_prompt.lower().split())
        essay_words = set(essay_text.lower().split())
        
        # Common words to ignore
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you',
            'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'its', 'our', 'their'
        }
        
        prompt_words = prompt_words - common_words
        essay_words = essay_words - common_words
        
        # Calculate word overlap
        matching_words = prompt_words.intersection(essay_words)
        
        if len(prompt_words) == 0:
            word_relevance = 50
        else:
            word_relevance = (len(matching_words) / len(prompt_words)) * 60
        
        # Length bonus
        length_bonus = min(20, len(essay_text.split()) / 50)
        
        total_relevance = word_relevance + length_bonus
        return min(100, max(0, total_relevance))


# Global instance
_topic_service = None


def get_topic_relevance_service():
    """Get or create the global topic relevance service instance"""
    global _topic_service
    if _topic_service is None:
        _topic_service = TopicRelevanceService()
    return _topic_service
