"""
Flask API for Essay Scoring
Endpoints to score essays using the trained ML model
"""

import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()
from config import config
from ocr_service import extract_text_from_image
from scoring_service import scoring_service


app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

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


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'model_loaded': scoring_service.scorer is not None
    }), 200


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
    Score an essay
    
    Request body:
    {
        "prompt": "Essay question/prompt",
        "response": "Student's essay text",
        "rubric_id": 1  (optional, defaults to 1)
    }
    
    Response:
    {
        "success": true,
        "score": 85,
        "category": 4,
        "confidence": 0.92,
        "breakdown": {
            "criterion1": 25,
            "criterion2": 23,
            ...
        },
        "feedback": "Strong essay with good argumentation",
        "rubric_used": 1
    }
    """
    
    if scoring_service.scorer is None:
        return jsonify({
            'success': False,
            'error': 'Model not loaded. Please restart the server.'
        }), 500
    
    try:
        data = request.get_json()
        
        if not data or 'response' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: response'
            }), 400
        
        essay_text = data.get('response', '').strip()
        rubric_id = data.get('rubric_id', 1)
        
        if len(essay_text) < 10:
            return jsonify({
                'success': False,
                'error': 'Essay too short. Minimum 10 characters required.'
            }), 400
        
        # Get prediction using scoring service
        result = scoring_service.score_essay(essay_text, data.get('prompt', ''), rubric_id)
        
        if not result['success']:
            return jsonify(result), 500
        
        prediction = result
        
        # Use the result from scoring service
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error scoring essay: {e}")
        traceback.print_exc()
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


@app.route('/api/rubrics', methods=['GET'])
def get_rubrics():
    """Get available rubrics (including custom ones)"""
    # Default rubrics
    rubrics = [
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
    
    # Override with custom rubrics if they exist
    for rubric in rubrics:
        if rubric['id'] in custom_rubrics:
            rubric['criteria'] = custom_rubrics[rubric['id']]
    
    return jsonify(rubrics), 200


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
