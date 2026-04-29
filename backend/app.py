# PATCH endpoint to update a rubric (moved after app definition)

"""
Flask API for Essay Scoring
Endpoints to score essays using the trained ML model
"""

import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import traceback
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()
from config import config
from ocr_service import extract_text_from_image
from scoring_service import scoring_service
from auth_service import auth_service

# Optional: Make supabase optional
try:
    from supabase_client import supabase_service
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️  Warning: Supabase not available (optional dependency)")


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Load trained model (handled by scoring_service)
# MODEL_PATH = os.path.join(config.MODELS_DIR, 'essay_scorer.pkl')
# scorer = None


def load_model():
    """Load the trained model on startup"""
    # Model loading is now handled by scoring_service
    if scoring_service.scorer is not None:
        print("✓ Model loaded successfully")
        return True
    else:
        print("❌ Model not loaded")
        print("Please run: python scripts/train_model.py")
        return False


def get_rubric_breakdown(total_score, rubric_id=1):
    """
    Calculate score breakdown based on selected rubric
    Uses custom rubric if one has been saved, otherwise uses default
    """
    # Default rubric mappings
    default_rubrics = {
        1: {  # Argumentative Essay
            'thesis': {'weight': 0.25, 'max': 25},
            'evidence': {'weight': 0.25, 'max': 25},
            'structure': {'weight': 0.30, 'max': 30},
            'grammar': {'weight': 0.20, 'max': 20}
        },
        2: {  # Expository Essay
            'clarity': {'weight': 0.30, 'max': 30},
            'organization': {'weight': 0.25, 'max': 25},
            'research': {'weight': 0.25, 'max': 25},
            'grammar': {'weight': 0.20, 'max': 20}
        },
        3: {  # Narrative Essay
            'storytelling': {'weight': 0.30, 'max': 30},
            'characters': {'weight': 0.25, 'max': 25},
            'engagement': {'weight': 0.25, 'max': 25},
            'language': {'weight': 0.20, 'max': 20}
        },
        4: {  # Research Paper
            'research': {'weight': 0.30, 'max': 30},
            'citations': {'weight': 0.25, 'max': 25},
            'analysis': {'weight': 0.25, 'max': 25},
            'rigor': {'weight': 0.20, 'max': 20}
        }
    }
    
    breakdown = {}
    
    # Check if custom rubric exists
    if rubric_id in custom_rubrics:
        # Use custom rubric criteria
        custom_criteria = custom_rubrics[rubric_id]
        total_points = sum(c['points'] for c in custom_criteria)
        
        for criterion in custom_criteria:
            criterion_name = criterion['name'].lower().replace(' & ', '_').replace(' ', '_')
            # Calculate proportional score
            weight = criterion['points'] / total_points if total_points > 0 else 0
            score = int(total_score * weight)
            score = min(score, criterion['points'])
            breakdown[criterion_name] = score
    else:
        # Use default rubric
        selected_rubric = default_rubrics.get(rubric_id, default_rubrics[1])
        
        for criterion, props in selected_rubric.items():
            score = int(total_score * props['weight'])
            score = min(score, props['max'])
            breakdown[criterion] = score
    
    return breakdown


@app.route('/api/signup', methods=['POST'])
def signup():
    if not SUPABASE_AVAILABLE:
        return jsonify({
            "success": False,
            "error": "Authentication requires Supabase. Use /api/score for demo mode testing."
        }), 503
    
    data = request.get_json()

    user, error = auth_service.sign_up(
        data.get("full_name"),
        data.get("email"),
        data.get("password")
    )

    if error:
        return jsonify({"success": False, "error": error}), 400

    return jsonify({
        "success": True,
        "message": "User created",
        "user_id": user.id
    }), 200


# --- Unified GET /api/rubrics endpoint ---
@app.route('/api/rubrics', methods=['GET'])
def get_all_rubrics():
    """Return both static default rubrics and user-created rubrics from Supabase"""
    # --- Static default rubrics ---
    default_rubrics = [
        {
            'id': 1,
            'title': 'Argumentative Essay',
            'criteria': [
                {'name': 'Thesis', 'points': 25},
                {'name': 'Evidence', 'points': 25},
                {'name': 'Structure', 'points': 30},
                {'name': 'Grammar', 'points': 20}
            ]
        },
        {
            'id': 2,
            'title': 'Expository Essay',
            'criteria': [
                {'name': 'Clarity', 'points': 30},
                {'name': 'Organization', 'points': 25},
                {'name': 'Research', 'points': 25},
                {'name': 'Grammar', 'points': 20}
            ]
        },
        {
            'id': 3,
            'title': 'Narrative Essay',
            'criteria': [
                {'name': 'Storytelling', 'points': 30},
                {'name': 'Characters', 'points': 25},
                {'name': 'Engagement', 'points': 25},
                {'name': 'Language', 'points': 20}
            ]
        },
        {
            'id': 4,
            'title': 'Research Paper',
            'criteria': [
                {'name': 'Research', 'points': 30},
                {'name': 'Citations', 'points': 25},
                {'name': 'Analysis', 'points': 25},
                {'name': 'Rigor', 'points': 20}
            ]
        }
    ]

    # --- User-created rubrics from Supabase ---
    user_rubrics = []
    if SUPABASE_AVAILABLE:
        try:
            user_id = request.args.get("user_id")
            query = supabase_service.client.table("rubrics").select("*")
            if user_id:
                query = query.eq("created_by", user_id)
            result = query.execute()
            if result.data:
                user_rubrics = result.data
        except Exception as e:
            print(f"Error fetching user rubrics: {e}")

    # Combine both lists (static first, then user rubrics)
    all_rubrics = default_rubrics + user_rubrics
    return jsonify(all_rubrics), 200

@app.route('/api/login', methods=['POST'])
def login():
    # Extract only serializable data from Supabase session
    try:
        user_id = session.user.id
        full_name = None
        
        # Fetch user profile to get full_name
        try:
            if SUPABASE_AVAILABLE:
                profile_response = supabase_service.client.table("profiles").select("full_name").eq("id", user_id).execute()
                if profile_response.data and len(profile_response.data) > 0:
                    full_name = profile_response.data[0].get("full_name")
        except Exception as profile_error:
            print(f"⚠️ Could not fetch profile: {profile_error}")
        
        user_data = {
            "id": user_id,
            "email": session.user.email,
            "full_name": full_name,
            "email_confirmed_at": str(session.user.email_confirmed_at) if session.user.email_confirmed_at else None,
            "created_at": str(session.user.created_at) if session.user.created_at else None
        }
        
        token_data = {
            "access_token": session.session.access_token,
            "token_type": session.session.token_type,
            "expires_in": session.session.expires_in
        }
        
        return jsonify({
            "success": True,
            "session": token_data,
            "user": user_data
        }), 200
    except Exception as e:
        print(f"Error serializing session: {e}")
        return jsonify({
            "success": False,
            "error": "Login successful but failed to process session data"
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'model_loaded': scoring_service.scorer is not None
    }), 200


# --- Rubric Endpoints ---
@app.route('/api/rubrics', methods=['POST'])
def create_rubric():
    """
    Create a new rubric and save to Supabase.
    Request body:
    {
        "title": "Rubric Title",
        "description": "Rubric description",
        "icon": "📝",
        "criteria": [
            {"name": "Content", "points": 25},
            {"name": "Organization", "points": 25}
        ],
        "created_by": "user-uuid"
    }
    """
    if not SUPABASE_AVAILABLE:
        return jsonify({"success": False, "error": "Supabase not available"}), 503

    data = request.get_json()
    if not data or not data.get("title") or not data.get("criteria"):
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    try:
        rubric_data = {
            "title": data["title"],
            "description": data.get("description", ""),
            "icon": data.get("icon", ""),
            "criteria": data["criteria"],
            "is_custom": True,
            "created_by": data.get("created_by")
        }
        result = supabase_service.client.table("rubrics").insert(rubric_data).execute()
        return jsonify({"success": True, "rubric": result.data[0]}), 201
    except Exception as e:
        print(f"Error creating rubric: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/rubrics', methods=['GET'])
def get_rubrics_api():
    user_id = request.args.get("user_id")
    if not SUPABASE_AVAILABLE:
        return jsonify({"success": False, "error": "Supabase not available"}), 503
    try:
        query = supabase_service.client.table("rubrics").select("*")
        if user_id:
            query = query.eq("created_by", user_id)
        result = query.execute()
        return jsonify(result.data), 200
    except Exception as e:
        print(f"Error fetching rubrics: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/ocr-extract', methods=['POST'])
def ocr_extract():
    """
    Extract text from uploaded image using Google Cloud Vision
    
    Request: multipart/form-data with 'file' field
    Response: {
        "success": true,
        "extracted_text": "Extracted text from image"
    }
    """
    if 'file' not in request.files:
        return jsonify({
            "success": False, 
            "error": "No file uploaded"
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            "success": False, 
            "error": "No file selected"
        }), 400
    
    # Check if file is an image or PDF
    if not (file.content_type.startswith('image/') or file.content_type == 'application/pdf'):
        return jsonify({
            "success": False, 
            "error": "File must be an image (JPG, PNG) or PDF"
        }), 400
    
    try:
        # Read the file into bytes
        img_bytes = file.read()
        
        # Call OCR service
        extracted_text = extract_text_from_image(img_bytes, file.filename)
        
        if extracted_text:
            return jsonify({
                "success": True, 
                "extracted_text": extracted_text
            }), 200
        else:
            return jsonify({
                "success": False, 
                "error": "Could not read text from image. Please try a clearer photo."
            }), 500
            
    except Exception as e:
        print(f"OCR Error: {e}")
        return jsonify({
            "success": False, 
            "error": "OCR processing failed. Please try again."
        }), 500


@app.route('/api/score', methods=['POST'])
def score_essay():
    """
    Score an essay and save to database
    
    Request body:
    {
        "prompt": "Essay question/prompt",
        "response": "Student's essay text",
        "student_name": "Student name (optional)",
        "student_id": "Student ID (optional)",
        "essay_title": "Essay title (optional)",
        "essay_type": "Essay type like 'Argumentative'",
        "rubric_id": 1,
        "user_id": "User's UUID from auth (required for history)"
    }
    """
    
    if scoring_service.scorer is None:
        return jsonify({
            'success': False,
            'error': 'Model not loaded. Please restart the server.'
        }), 500
    
    try:
        data = request.get_json()
        
        print(f"\n🚀 INSIDE score_essay() try block")
        print(f"   data keys: {list(data.keys()) if data else 'NO DATA'}")
        
        if not data or 'response' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: response'
            }), 400
        
        essay_text = data.get('response', '').strip()
        rubric_id = data.get('rubric_id', 1)
        user_id = data.get('user_id')  # Get user_id from request
        
        print(f"\n📝 Scoring essay request:")
        print(f"   user_id: {user_id}")
        print(f"   user_id type: {type(user_id)}")
        print(f"   essay length: {len(essay_text)} chars")
        print(f"   rubric_id: {rubric_id}")
        
        if len(essay_text) < 10:
            return jsonify({
                'success': False,
                'error': 'Essay too short. Minimum 10 characters required.'
            }), 400
        
        # Get prediction using scoring service
        result = scoring_service.score_essay(essay_text, data.get('prompt', ''), rubric_id)
        
        if not result['success']:
            return jsonify(result), 500
        
        print(f"\n✅ About to check user_id and save essay...")
        print(f"   user_id value is: {repr(user_id)}")
        
        # Save essay to database if user is logged in
        # Check for various falsy values: None, empty string, 'null', 'undefined'
        if not user_id or user_id == 'null' or user_id == 'undefined' or (isinstance(user_id, str) and len(user_id.strip()) == 0):
            print("⚠️ WARNING: No valid user_id provided - essay will NOT be saved to history")
            print(f"   Reason: user_id={repr(user_id)}")
            return jsonify(result), 200
        
        print(f"💾 Attempting to save essay for user: {user_id}")
        
        essay_data = {
            'user_id': user_id,  # ✓ MUST include user_id
            'student_id': data.get('student_id', 'anonymous'),
            'student_name': data.get('student_name', 'Anonymous'),
            'essay_title': data.get('essay_title') or data.get('prompt') or 'Untitled Essay',  # ✓ Default to prompt if no title
            'essay_type': data.get('essay_type', 'Essay'),
            'essay_prompt': data.get('prompt', ''),
            'essay_text': essay_text,
            'total_score': result.get('score', 0),
            'max_score': 100,
            'breakdown': result.get('breakdown', {}),
            'confidence': result.get('confidence', 0.0),
            'feedback': result.get('feedback', ''),
            'rubric_id': rubric_id,
            'topic_relevance': result.get('topic_relevance', 0.0),
            'status': 'Graded',
            'teacher_notes': ''
        }
        
        # ✅ DEBUG: Log what we're sending to save_essay_score
        print(f"📊 essay_data being sent to save_essay_score:")
        print(f"   user_id in essay_data: {essay_data.get('user_id')}")
        print(f"   user_id is None: {essay_data.get('user_id') is None}")
        print(f"   user_id type: {type(essay_data.get('user_id'))}")
        
        if SUPABASE_AVAILABLE:
            save_result = supabase_service.save_essay_score(essay_data)
            if save_result['success']:
                print(f"✓ Essay saved successfully!")
                result['essay_id'] = save_result['data'].get('id')
            else:
                print(f"❌ Could not save essay: {save_result.get('error')}")
        else:
            print(f"⚠️  Supabase not available, skipping database save")
        
        # ✅ DEBUG: Log what we're returning to frontend
        print(f"\n📤 Returning response to frontend:")
        print(f"   result keys: {list(result.keys())}")
        print(f"   breakdown: {result.get('breakdown')}")
        print(f"   score: {result.get('score')}")
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"\n❌❌❌ EXCEPTION CAUGHT IN SCORE ENDPOINT ❌❌❌")
        print(f"Error scoring essay: {e}")
        print(f"Exception type: {type(e).__name__}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/essay-history', methods=['GET'])
def get_essay_history():
    """
    Get essay scores from Supabase - filtered by user_id
    
    Query parameters:
    - user_id: (required) The UUID of the logged-in user
    - limit: (optional) Number of essays to return, default 50
    """
    try:
        user_id = request.args.get('user_id')
        limit = request.args.get('limit', 50, type=int)
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id parameter required'
            }), 400
        
        # Get essays for specific user
        if not SUPABASE_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Supabase not available'
            }), 503
        
        essays = supabase_service.get_user_essay_scores(user_id, limit)
        
        return jsonify({
            'success': True,
            'essays': essays,
            'count': len(essays)
        }), 200
        
    except Exception as e:
        print(f"Error fetching essay history: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/essay-history/<int:essay_id>', methods=['PUT'])
def update_essay(essay_id):
    """
    Update essay status or notes
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        if not SUPABASE_AVAILABLE:
            return jsonify({'success': False, 'error': 'Supabase not available'}), 503
        
        # Update essay in Supabase
        success = supabase_service.update_essay_score(essay_id, data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Essay updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update essay'
            }), 500
            
    except Exception as e:
        print(f"Error updating essay: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/essay-history/<int:essay_id>', methods=['DELETE'])
def delete_essay(essay_id):
    """
    Delete an essay from Supabase
    """
    try:
        if not SUPABASE_AVAILABLE:
            return jsonify({'success': False, 'error': 'Supabase not available'}), 503
        
        success = supabase_service.delete_essay_score(essay_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Essay deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete essay'
            }), 500
            
    except Exception as e:
        print(f"Error deleting essay: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/class-analytics', methods=['GET'])
def get_class_analytics():
    """
    Get class analytics from Supabase
    """
    try:
        if not SUPABASE_AVAILABLE:
            return jsonify({'success': False, 'error': 'Supabase not available'}), 503
        
        analytics = supabase_service.get_class_analytics()
        
        return jsonify({
            'success': True,
            'analytics': analytics
        }), 200
        
    except Exception as e:
        print(f"Error fetching analytics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/batch-score', methods=['POST'])
def batch_score():
    """
    Score multiple essays at once
    
    Request body:
    {
        "essays": [
            {"response": "essay 1 text"},
            {"response": "essay 2 text"}
        ]
    }
    """
    
    if scoring_service.scorer is None:
        return jsonify({
            'success': False,
            'error': 'Model not loaded'
        }), 500
    
    try:
        data = request.get_json()
        essays = data.get('essays', [])
        
        if not essays:
            return jsonify({
                'success': False,
                'error': 'No essays provided'
            }), 400
        
        results = []
        for essay in essays:
            response = essay.get('response', '').strip()
            if len(response) >= 10:
                result = scoring_service.score_essay(response)
                if result['success']:
                    results.append({
                        'score': result['score'],
                        'confidence': result['confidence']
                    })
                else:
                    results.append({'error': 'Scoring failed'})
            else:
                results.append({'error': 'Essay too short'})
        
        return jsonify({
            'success': True,
            'scores': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Storage for custom rubrics (in production, this would be a database)
custom_rubrics = {}





@app.route('/api/rubrics/save', methods=['POST'])
def save_rubric():
    """Save a custom rubric"""
    try:
        data = request.get_json()
        
        if not data or 'id' not in data or 'criteria' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: id and criteria'
            }), 400
        
        rubric_id = data['id']
        criteria = data['criteria']
        
        # Validate criteria
        if not isinstance(criteria, list) or len(criteria) == 0:
            return jsonify({
                'success': False,
                'error': 'Criteria must be a non-empty list'
            }), 400
        
        # Validate each criterion
        for criterion in criteria:
            if 'name' not in criterion or 'points' not in criterion:
                return jsonify({
                    'success': False,
                    'error': 'Each criterion must have name and points'
                }), 400
        
        # Save custom rubric
        custom_rubrics[rubric_id] = criteria
        
        print(f"✓ Rubric {rubric_id} saved with {len(criteria)} criteria")
        
        return jsonify({
            'success': True,
            'message': f'Rubric saved successfully',
            'rubric_id': rubric_id
        }), 200
        
    except Exception as e:
        print(f"Error saving rubric: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



@app.route('/api/rubrics/<rubric_id>', methods=['PATCH', 'OPTIONS'])
@cross_origin(origins="*", allow_headers=["Content-Type", "Authorization"], methods=["PATCH", "OPTIONS"])
def update_rubric(rubric_id):
    if request.method == 'OPTIONS':
        # Preflight request
        return '', 204
    if not SUPABASE_AVAILABLE:
        return jsonify({"success": False, "error": "Supabase not available"}), 503
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Missing rubric data"}), 400
    try:
        update_fields = {}
        for field in ["title", "description", "icon", "criteria"]:
            if field in data:
                update_fields[field] = data[field]
        if not update_fields:
            return jsonify({"success": False, "error": "No valid fields to update"}), 400
        print(f"[PATCH /api/rubrics/{{rubric_id}}] rubric_id: {rubric_id}")
        print(f"[PATCH /api/rubrics/{{rubric_id}}] update_fields: {update_fields}")
        result = supabase_service.client.table("rubrics").update(update_fields).eq("id", rubric_id).execute()
        print(f"[PATCH /api/rubrics/{{rubric_id}}] Supabase result: {result}")
        if hasattr(result, 'data') and result.data:
            print(f"[PATCH /api/rubrics/{{rubric_id}}] Updated rubric: {result.data[0]}")
            return jsonify({"success": True, "rubric": result.data[0]}), 200
        else:
            print(f"[PATCH /api/rubrics/{{rubric_id}}] No rubric updated. Supabase returned: {getattr(result, 'data', None)}")
            return jsonify({"success": False, "error": "Rubric not found or not updated"}), 404
    except Exception as e:
        print(f"Error updating rubric: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Essay Scoring API Server")
    print("=" * 60)
    
    # Load model on startup
    if load_model():
        print(f"\n✓ Server starting on http://localhost:{config.PORT}")
        print("\nAvailable endpoints:")
        print("  POST /api/score - Score a single essay")
        print("  POST /api/batch-score - Score multiple essays")
        print("  POST /api/ocr-extract - Extract text from image")
        print("  GET  /api/rubrics - Get available rubrics")
        print("  GET  /health - Health check")
        print("\nPress Ctrl+C to stop")
        print("=" * 60 + "\n")
        
        app.run(
            host='0.0.0.0',
            port=config.PORT,
            debug=config.FLASK_DEBUG
        )
    else:
        print("\n❌ Cannot start server - model not available")
        sys.exit(1)
