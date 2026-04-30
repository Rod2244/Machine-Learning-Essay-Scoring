"""
Supabase Client for Student Score History
"""
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import Dict, List, Optional

# Try to import supabase, but make it optional
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None
    create_client = None

# Load environment variables
load_dotenv()

class SupabaseService:
    def __init__(self):
        # Load environment variables
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
        self.supabase_service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.client = None
        self.admin_client = None
        
        if not SUPABASE_AVAILABLE:
            print("⚠️ Supabase module not installed (optional dependency)")
            return
        
        if not self.supabase_url or not self.supabase_anon_key:
            print("⚠️ Supabase credentials not found in environment variables")
            self.client = None
        else:
            try:
                # Regular client with anon key (for reads and user-specific operations)
                self.client: Client = create_client(self.supabase_url, self.supabase_anon_key)
                print("✅ Supabase client (anon) initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize Supabase client: {e}")
                self.client = None
        
        # Initialize admin client if service role key is available
        if self.supabase_url and self.supabase_service_role_key:
            try:
                # Admin client with service role key (bypasses RLS policies)
                self.admin_client: Client = create_client(self.supabase_url, self.supabase_service_role_key)
                print("✅ Supabase admin client (service role) initialized successfully")
            except Exception as e:
                print(f"⚠️ Failed to initialize Supabase admin client: {e}")
                self.admin_client = None
        else:
            print("⚠️ SUPABASE_SERVICE_ROLE_KEY not found - admin operations may not work")
    
    def is_connected(self) -> bool:
        """Check if Supabase is connected"""
        return self.client is not None
    
    def save_essay_score(self, essay_data: Dict) -> Dict:
        """
        Save essay score to Supabase
        
        Args:
            essay_data = {
                'user_id': str (UUID - required for associating with user),
                'student_id': str,
                'student_name': str,
                'essay_title': str,
                'essay_type': str,
                'essay_prompt': str,
                'essay_text': str,
                'total_score': int,
                'max_score': int,
                'breakdown': Dict,
                'confidence': float,
                'feedback': str,
                'rubric_id': int,
                'topic_relevance': float,
                'status': str,
                'teacher_notes': str
            }
        """
        # ✅ DEBUG: Log what we receive
        print(f"\n🔍 save_essay_score() called")
        print(f"   essay_data type: {type(essay_data)}")
        print(f"   essay_data keys: {list(essay_data.keys()) if isinstance(essay_data, dict) else 'NOT A DICT'}")
        print(f"   user_id key exists: {'user_id' in essay_data}")
        print(f"   user_id value: {essay_data.get('user_id') if isinstance(essay_data, dict) else 'N/A'}")
        print(f"   full essay_data: {essay_data}")
        
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase not connected'}
        
        try:
            # Prepare data for Supabase - INCLUDE user_id!
            record = {
                'user_id': essay_data.get('user_id'),  # ✓ CRITICAL: Include user_id
                'student_id': essay_data.get('student_id', 'anonymous'),
                'student_name': essay_data.get('student_name', 'Anonymous Student'),
                'essay_title': essay_data.get('essay_title', 'Untitled Essay'),
                'essay_type': essay_data.get('essay_type', 'Essay'),
                'essay_prompt': essay_data.get('essay_prompt', ''),
                'essay_text': essay_data.get('essay_text', '')[:5000],  # Limit text length
                'total_score': essay_data.get('total_score', 0),
                'max_score': essay_data.get('max_score', 100),
                'breakdown': essay_data.get('breakdown', {}),
                'confidence': essay_data.get('confidence', 0.0),
                'feedback': essay_data.get('feedback', ''),
                'rubric_id': essay_data.get('rubric_id', 1),
                'topic_relevance': essay_data.get('topic_relevance', 0.0),
                'status': essay_data.get('status', 'Graded'),
                'teacher_notes': essay_data.get('teacher_notes', '')
            }
            
            # Verify user_id exists
            if not record['user_id']:
                print("⚠️ WARNING: user_id is missing from essay_data!")
                return {'success': False, 'error': 'user_id is required to save essays'}
            
            print(f"💾 Saving essay for user: {record['user_id']}")
            
            # Insert into Supabase - let database handle created_at/updated_at timestamps
            try:
                result = self.client.table('essay_scores').insert(record).execute()
                if result.data and len(result.data) > 0:
                    print(f"✓ Essay saved successfully with ID: {result.data[0].get('id')}")
                    return {'success': True, 'data': result.data[0]}
                else:
                    return {'success': False, 'error': 'Failed to save to Supabase'}
            except Exception as e:
                # Handle common type mismatch when rubric_id is a UUID but DB expects bigint
                err_str = str(e)
                print(f"❌ Error saving essay score: {err_str}")
                if 'invalid input syntax for type bigint' in err_str and record.get('rubric_id') and not str(record.get('rubric_id')).isdigit():
                    print("⚠️ Detected bigint type error for rubric_id; retrying without numeric rubric_id and storing UUID in teacher_notes")
                    retry_record = record.copy()
                    # move the UUID into teacher_notes so it's still recorded
                    existing_notes = retry_record.get('teacher_notes') or ''
                    retry_record['teacher_notes'] = (existing_notes + f" rubric_uuid:{retry_record.get('rubric_id')}").strip()
                    retry_record['rubric_id'] = None
                    try:
                        retry_result = self.client.table('essay_scores').insert(retry_record).execute()
                        if retry_result.data and len(retry_result.data) > 0:
                            print(f"✓ Essay saved successfully on retry with ID: {retry_result.data[0].get('id')}")
                            return {'success': True, 'data': retry_result.data[0]}
                        else:
                            return {'success': False, 'error': 'Failed to save to Supabase on retry'}
                    except Exception as e2:
                        print(f"❌ Retry failed: {e2}")
                        return {'success': False, 'error': str(e2)}
                return {'success': False, 'error': str(e)}
                
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
    
    def get_user_essay_scores(self, user_id: str, limit: int = 50) -> List:
        """
        Get essay scores for a specific user from Supabase
        
        Args:
            user_id: The UUID of the user
            limit: Maximum number of records to return
        
        Returns:
            List of essays for the user
        """
        if not self.is_connected():
            return []
        
        try:
            result = self.client.table('essay_scores').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(limit).execute()
            
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
                        'criteria': self._convert_breakdown_to_criteria(essay.get('breakdown', {})),
                        'text': essay.get('essay_text', 'Essay text not available'),  # Add essay text
                        'prompt': essay.get('essay_prompt', '')  # Add prompt if available
                    })
                return essays
            else:
                return []
                
        except Exception as e:
            print(f"❌ Error fetching user essays: {e}")
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
    
    def sign_up(self, email: str, password: str):
        """
        Sign up a new user with Supabase Auth
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Response object with user data
        """
        if not self.is_connected():
            raise Exception("Supabase not connected")
        
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password
            })
            return response
        except Exception as e:
            print(f"❌ Signup error: {e}")
            raise e
    
    def sign_in(self, email: str, password: str):
        """
        Sign in a user with Supabase Auth
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Session object with user and auth token
        """
        if not self.is_connected():
            raise Exception("Supabase not connected")
        
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return response
        except Exception as e:
            print(f"❌ Login error: {e}")
            raise e

# Global instance
supabase_service = SupabaseService()
