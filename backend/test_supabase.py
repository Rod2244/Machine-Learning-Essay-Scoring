"""
Test Supabase Connection
"""
import asyncio
import os
from dotenv import load_dotenv
from supabase_client import supabase_service

# Load environment variables
load_dotenv()

async def test_supabase():
    """Test Supabase connection and basic operations"""
    print("🧪 Testing Supabase Connection...")
    
    # Load environment variables
    load_dotenv()
    
    # Check connection
    if not supabase_service.is_connected():
        print("❌ Supabase not connected. Check your .env file!")
        print("Make sure you have:")
        print("- SUPABASE_URL=https://your-project.supabase.co")
        print("- SUPABASE_ANON_KEY=your-anon-key")
        return
    
    print("✅ Supabase connected successfully!")
    
    # Test saving a sample essay
    test_essay = {
        'student_id': 'test_student_001',
        'student_name': 'Test Student',
        'essay_title': 'Test Essay for Supabase',
        'essay_type': 'Argumentative Essay',
        'essay_prompt': 'technology in education',
        'essay_text': 'Technology has transformed education in many ways...',
        'total_score': 85,
        'max_score': 100,
        'breakdown': {
            'Thesis': 22,
            'Evidence': 21,
            'Structure': 25,
            'Grammar': 17
        },
        'confidence': 0.87,
        'feedback': 'Good essay with strong arguments',
        'rubric_id': 1,
        'topic_relevance': 0.92,
        'status': 'Graded',
        'teacher_notes': ''
    }
    
    # Save test essay
    print("📝 Saving test essay...")
    save_result = await supabase_service.save_essay_score(test_essay)
    
    if save_result['success']:
        print(f"✅ Test essay saved! ID: {save_result['data']['id']}")
    else:
        print(f"❌ Failed to save: {save_result['error']}")
        return
    
    # Test fetching essays
    print("📚 Fetching essay history...")
    history_result = await supabase_service.get_student_history()
    
    if history_result['success']:
        print(f"✅ Found {len(history_result['data'])} essays in database")
        for essay in history_result['data']:
            print(f"   📄 {essay['essay_title']} - {essay['student_name']} - {essay['total_score']}/100")
    else:
        print(f"❌ Failed to fetch: {history_result['error']}")
    
    print("\n🎉 Supabase test completed!")

if __name__ == "__main__":
    asyncio.run(test_supabase())
