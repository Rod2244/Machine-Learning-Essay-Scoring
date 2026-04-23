"""
Supabase Client for Student Score History
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime
from typing import Dict, List, Optional

# Load environment variables
load_dotenv()

class SupabaseService:
    def __init__(self):
        # Load environment variables
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            print("⚠️ Supabase credentials not found in environment variables")
            self.client = None
        else:
            try:
                self.client: Client = create_client(self.supabase_url, self.supabase_key)
                print("✅ Supabase client initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize Supabase client: {e}")
                self.client = None
    
    def is_connected(self) -> bool:
        """Check if Supabase is connected"""
        return self.client is not None
    
    def save_essay_score(self, essay_data: Dict) -> Dict:
        """
        Save essay score to Supabase
        
        Args:
            essay_data = {
                'student_id': str,
                'student_name': str,
                'essay_title': str,
                'essay_type': str,
                'essay_prompt': str,
                'essay_text': str,
                'total_score': int,
                'max_score': int,
                'breakdown': Dict,  # rubric breakdown
                'confidence': float,
                'feedback': str,
                'rubric_id': int,
                'topic_relevance': float,
                'status': str,  # 'Graded', 'For Review', 'Returned'
                'teacher_notes': str
            }
        """
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase not connected'}
        
        try:
            # Prepare data for Supabase
            record = {
                'student_id': essay_data.get('student_id', 'anonymous'),
                'student_name': essay_data.get('student_name', 'Anonymous Student'),
                'essay_title': essay_data.get('essay_title', 'Untitled Essay'),
                'essay_type': essay_data.get('essay_type', 'Essay'),
                'essay_prompt': essay_data.get('essay_prompt', ''),
                'essay_text': essay_data.get('essay_text', '')[:1000],  # Limit text length
                'total_score': essay_data.get('total_score', 0),
                'max_score': essay_data.get('max_score', 100),
                'breakdown': essay_data.get('breakdown', {}),
                'confidence': essay_data.get('confidence', 0.0),
                'feedback': essay_data.get('feedback', ''),
                'rubric_id': essay_data.get('rubric_id', 1),
                'topic_relevance': essay_data.get('topic_relevance', 0.0),
                'status': essay_data.get('status', 'Graded'),
                'teacher_notes': essay_data.get('teacher_notes', ''),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Insert into Supabase
            result = self.client.table('essay_scores').insert(record).execute()
            
            if result.data:
                return {'success': True, 'data': result.data[0]}
            else:
                return {'success': False, 'error': 'Failed to save to Supabase'}
                
        except Exception as e:
            print(f"❌ Error saving essay score: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_student_history(self, student_id: str = None, limit: int = 50) -> Dict:
        """
        Get essay scores from Supabase
        
        Args:
            student_id: Optional filter by student
            limit: Maximum number of records to return
        """
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase not connected'}
        
        try:
            query = self.client.table('essay_scores').select('*').order('created_at', desc=True).limit(limit)
            
            if student_id:
                query = query.eq('student_id', student_id)
            
            result = query.execute()
            
            return {'success': True, 'data': result.data}
            
        except Exception as e:
            print(f"❌ Error fetching essay history: {e}")
            return {'success': False, 'error': str(e)}
    
    async def update_essay_status(self, essay_id: str, status: str, notes: str = None) -> Dict:
        """Update essay status and/or notes"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase not connected'}
        
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.now().isoformat()
            }
            
            if notes is not None:
                update_data['teacher_notes'] = notes
            
            result = self.client.table('essay_scores').update(update_data).eq('id', essay_id).execute()
            
            if result.data:
                return {'success': True, 'data': result.data[0]}
            else:
                return {'success': False, 'error': 'Essay not found'}
                
        except Exception as e:
            print(f"❌ Error updating essay: {e}")
            return {'success': False, 'error': str(e)}
    
    async def delete_essay(self, essay_id: str) -> Dict:
        """Delete essay record"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase not connected'}
        
        try:
            result = self.client.table('essay_scores').delete().eq('id', essay_id).execute()
            
            if result.data:
                return {'success': True, 'data': result.data[0]}
            else:
                return {'success': False, 'error': 'Essay not found'}
                
        except Exception as e:
            print(f"❌ Error deleting essay: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_class_analytics(self) -> Dict:
        """Get class-wide analytics"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase not connected'}
        
        try:
            # Get all essays
            result = self.client.table('essay_scores').select('*').execute()
            
            if not result.data:
                return {'success': True, 'analytics': {}}
            
            essays = result.data
            
            # Calculate analytics
            total_essays = len(essays)
            avg_score = sum(e['total_score'] for e in essays) / total_essays if total_essays > 0 else 0
            
            # Score distribution
            score_ranges = {
                'excellent': len([e for e in essays if e['total_score'] >= 90]),
                'good': len([e for e in essays if 75 <= e['total_score'] < 90]),
                'average': len([e for e in essays if 60 <= e['total_score'] < 75]),
                'poor': len([e for e in essays if e['total_score'] < 60])
            }
            
            # Top performers
            top_students = {}
            for essay in essays:
                student = essay['student_name']
                if student not in top_students:
                    top_students[student] = []
                top_students[student].append(essay['total_score'])
            
            avg_by_student = {student: sum(scores) / len(scores) for student, scores in top_students.items()}
            top_performers = sorted(avg_by_student.items(), key=lambda x: x[1], reverse=True)[:5]
            
            analytics = {
                'total_essays': total_essays,
                'average_score': round(avg_score, 1),
                'score_distribution': score_ranges,
                'top_performers': top_performers,
                'recent_activity': essays[:5]  # Last 5 essays
            }
            
            return {'success': True, 'analytics': analytics}
            
        except Exception as e:
            print(f"❌ Error calculating analytics: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_all_essay_scores(self) -> List:
        """
        Get all essay scores from Supabase
        """
        if not self.is_connected():
            return []
        
        try:
            result = self.client.table('essay_scores').select('*').order('created_at', desc=True).execute()
            
            if result.data:
                # Convert Supabase data to frontend format
                essays = []
                for essay in result.data:
                    essays.append({
                        'id': essay['id'],
                        'title': essay['essay_title'],
                        'student': essay['student_name'],
                        'type': essay['essay_type'],
                        'date': essay['created_at'].split('T')[0],  # Format as YYYY-MM-DD
                        'totalScore': essay['total_score'],
                        'maxScore': essay['max_score'],
                        'status': essay['status'],
                        'notes': essay['teacher_notes'],
                        'criteria': self._convert_breakdown_to_criteria(essay.get('breakdown', {}))
                    })
                return essays
            else:
                return []
                
        except Exception as e:
            print(f"❌ Error fetching all essays: {e}")
            return []
    
    def update_essay_score(self, essay_id: int, data: Dict) -> bool:
        """
        Update essay score in Supabase
        """
        if not self.is_connected():
            return False
        
        try:
            update_data = {}
            if 'status' in data:
                update_data['status'] = data['status']
            if 'notes' in data:
                update_data['teacher_notes'] = data['notes']
            
            update_data['updated_at'] = datetime.now().isoformat()
            
            result = self.client.table('essay_scores').update(update_data).eq('id', essay_id).execute()
            
            return len(result.data) > 0
                
        except Exception as e:
            print(f"❌ Error updating essay: {e}")
            return False
    
    def delete_essay_score(self, essay_id: int) -> bool:
        """
        Delete essay score from Supabase
        """
        if not self.is_connected():
            return False
        
        try:
            result = self.client.table('essay_scores').delete().eq('id', essay_id).execute()
            
            return len(result.data) > 0
                
        except Exception as e:
            print(f"❌ Error deleting essay: {e}")
            return False
    
    def _convert_breakdown_to_criteria(self, breakdown: Dict) -> List:
        """
        Convert breakdown JSON to criteria format for frontend
        """
        criteria = []
        for criterion_name, score in breakdown.items():
            criteria.append({
                'name': criterion_name,
                'score': score,
                'max': 25  # Default max score, adjust as needed
            })
        return criteria

# Global instance
supabase_service = SupabaseService()
