
"""
ColorMe - Main Application Entry Point
This is the main Flask application that serves the frontend and handles all API endpoints
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import jwt
import datetime

# Import analysis modules
try:
    from logic.colorpalette import (
        determine_season, 
        get_season_description, 
        generate_palette, 
        get_season_palette, 
        rgb_to_hsv, 
        calculate_contrast
    )
    from logic.undertone import (
        analyze_undertone, 
        get_undertone_recommendations, 
        analyze_detailed_undertone
    )
    print("✓ Successfully imported colorpalette and undertone modules")

except ImportError as e:
    print(f"Warning: Could not import analysis modules: {e}")
    print(f"Files in logic folder: {os.listdir('logic') if os.path.exists('logic') else 'logic folder not found'}")

    # Provide fallback functions
    def determine_season(skin_rgb, hair_rgb, eye_rgb):
        _ = (skin_rgb, hair_rgb, eye_rgb)
        return "Spring"
    
    def get_season_description(season):
        _ = season
        return {"characteristics": "Season analysis module not loaded"}
    
    def analyze_undertone(skin_rgb):
        _ = skin_rgb
        return "warm"
    
    def get_undertone_recommendations(undertone):
        _ = undertone
        return {"jewelry": "Analysis module not loaded"}
    
    def generate_palette(base_color, palette_type):
        _ = (base_color, palette_type)
        return ["#FF0000", "#00FF00", "#0000FF"]
    
    def get_season_palette(season, base_color=None):
        _ = (season, base_color)
        return ["#FF0000", "#00FF00", "#0000FF"]
    
    def analyze_detailed_undertone(skin_rgb):
        _ = skin_rgb
        return {"undertone": "warm", "warm_percentage": 50, "cool_percentage": 30, "neutral_percentage": 20}
    
    def rgb_to_hsv(rgb):
        _ = rgb
        return (0, 0, 0)
    
    def calculate_contrast(color1, color2):
        _ = (color1, color2)
        return 0.5

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)  # Enable CORS for all routes

# Secret key for JWT tokens
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'

# File paths for simple file-based storage
USERS_FILE = 'users.txt'
RESULTS_FILE = 'user_results.json'

# ============ UTILITY FUNCTIONS ============

def parse_rgb(rgb_string):
    """Convert 'rgb(255, 255, 255)' to (255, 255, 255)"""
    try:
        rgb_string = rgb_string.replace('rgb(', '').replace(')', '').strip()
        r, g, b = map(int, [x.strip() for x in rgb_string.split(',')])
        return (r, g, b)
    except Exception as e:
        raise ValueError(f"Invalid RGB format: {rgb_string}")

def load_users():
    """Load users from file"""
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and ':' in line:
                    parts = line.split(':', 2)
                    if len(parts) >= 3:
                        username = parts[0]
                        users[username] = {
                            'username': username,
                            'email': parts[1],
                            'password': parts[2]
                        }
    return users

def save_user(username, email, password):
    """Save a new user to file"""
    hashed_password = generate_password_hash(password)
    with open(USERS_FILE, 'a') as f:
        f.write(f"{username}:{email}:{hashed_password}\n")

def load_results():
    """Load all user results from JSON file"""
    if os.path.exists(RESULTS_FILE):
        try:
            with open(RESULTS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_results(results_data):
    """Save all results to JSON file"""
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results_data, f, indent=2)

def save_user_result(username, analysis_result):
    """Save a user's analysis result"""
    all_results = load_results()
    
    if username not in all_results:
        all_results[username] = []
    
    # Add timestamp if not present
    if 'timestamp' not in analysis_result:
        analysis_result['timestamp'] = datetime.datetime.now().isoformat()
    
    all_results[username].append(analysis_result)
    save_results(all_results)

def get_user_results(username):
    """Get all results for a specific user"""
    all_results = load_results()
    return all_results.get(username, [])

# ============ FRONTEND ROUTES ============

@app.route('/')
def index():
    """Serve the main index.html page"""
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from the frontend folder"""
    try:
        return send_from_directory('frontend', path)
    except:
        # If file not found, return index.html for client-side routing
        return send_from_directory('frontend', 'index.html')

# ============ API ROUTES ============

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "Backend running",
        "version": "1.0.0",
        "modules": {
            "colorpalette": "loaded",
            "undertone": "loaded"
        }
    })

@app.route('/analyze', methods=['POST'])
def analyze_colors():
    """
    Main color analysis endpoint
    Receives skin, hair, and eye colors from the frontend
    Returns seasonal analysis and undertone
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get RGB colors from frontend
        skin_color = data.get('skin')
        hair_color = data.get('hair')
        eye_color = data.get('eyes')
        
        if not all([skin_color, hair_color, eye_color]):
            return jsonify({'error': 'Missing color data. Please select all three colors.'}), 400
        
        # Convert RGB strings to tuples
        skin_rgb = parse_rgb(skin_color)
        hair_rgb = parse_rgb(hair_color)
        eye_rgb = parse_rgb(eye_color)
        
        # Calculate some debug values
        skin_hsv = rgb_to_hsv(skin_rgb)
        hair_hsv = rgb_to_hsv(hair_rgb)
        contrast_skin_hair = calculate_contrast(skin_rgb, hair_rgb)
        
        print("\n" + "="*60)
        print("🎨 COLOR ANALYSIS DEBUG")
        print("="*60)
        print(f"Input Colors:")
        print(f"  Skin RGB:  {skin_rgb} (Brightness: {skin_hsv[2]:.2f})")
        print(f"  Hair RGB:  {hair_rgb} (Brightness: {hair_hsv[2]:.2f})")
        print(f"  Eye RGB:   {eye_rgb}")
        print(f"\nAnalysis Factors:")
        print(f"  Skin-Hair Contrast: {contrast_skin_hair:.3f}")
        print(f"  Warm Score: {((skin_rgb[0] + skin_rgb[1])/2 - skin_rgb[2])/255:.3f}")
        print(f"  Hair Darkness: {'Very Dark' if hair_hsv[2] < 0.25 else 'Dark' if hair_hsv[2] < 0.35 else 'Medium' if hair_hsv[2] < 0.55 else 'Light'}")
        
        # Perform analysis
        season = determine_season(skin_rgb, hair_rgb, eye_rgb)
        undertone = analyze_undertone(skin_rgb)
        
        # CRITICAL: Season ALWAYS determines undertone in 12-season system
        # Winter/Summer = Cool undertones ALWAYS
        # Spring/Autumn = Warm undertones ALWAYS
        
        if "Winter" in season or "Summer" in season:
            original_undertone = undertone
            undertone = "cool"
            if original_undertone != "cool":
                print(f"  → Undertone FORCED to 'cool' for {season} (was {original_undertone})")
        
        elif "Spring" in season or "Autumn" in season:
            original_undertone = undertone
            undertone = "warm"
            if original_undertone != "warm":
                print(f"  → Undertone FORCED to 'warm' for {season} (was {original_undertone})")
        
        season_info = get_season_description(season)
        undertone_info = get_undertone_recommendations(undertone)
        detailed_undertone = analyze_detailed_undertone(skin_rgb)
        
        print(f"\nResults:")
        print(f"  Season:    {season}")
        print(f"  Undertone: {undertone}")
        print(f"  Breakdown: Warm {detailed_undertone['warm_percentage']}%, "
              f"Cool {detailed_undertone['cool_percentage']}%, "
              f"Neutral {detailed_undertone['neutral_percentage']}%")
        print("="*60 + "\n")
        
        # Generate recommended color palette
        palette = get_season_palette(season, skin_rgb)
        
        # Return comprehensive results
        return jsonify({
            'success': True,
            'season': season,
            'undertone': undertone,
            'skin_rgb': f"rgb({skin_rgb[0]}, {skin_rgb[1]}, {skin_rgb[2]})",
            'hair_rgb': f"rgb({hair_rgb[0]}, {hair_rgb[1]}, {hair_rgb[2]})",
            'eye_rgb':  f"rgb({eye_rgb[0]}, {eye_rgb[1]}, {eye_rgb[2]})",
            'message': f'Your color season is {season} with {undertone} undertones!',
            'season_info': {
                'characteristics': season_info.get('characteristics', ''),
                'best_colors': season_info.get('best_colors', []),
                'avoid_colors': season_info.get('avoid_colors', []),
                'metals': season_info.get('metals', ''),
            },
            'undertone_info': {
                'jewelry': undertone_info.get('jewelry', ''),
                'best_colors': undertone_info.get('best_colors', []),
                'makeup_tips': undertone_info.get('makeup_tips', []),
            },
            'detailed_undertone': detailed_undertone,
            'recommended_palette': palette
        })
        
    except ValueError as e:
        print(f"ValueError in analyze_colors: {str(e)}")
        return jsonify({'error': f'Invalid color format: {str(e)}'}), 400
    except Exception as e:
        print(f"Error in analyze_colors: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/palette', methods=['POST'])
def palette_route():
    """
    Generate color palette from a base color
    Supports different palette types
    """
    try:
        data = request.get_json()
        
        base_color = data.get('base_color', [255, 0, 0])  # Default = red
        palette_type = data.get('palette_type', 'complementary')
        
        # Generate palette
        palette = generate_palette(base_color, palette_type)
        
        return jsonify({
            "success": True,
            "base_color": base_color,
            "palette_type": palette_type,
            "generated_palette": palette
        })
        
    except Exception as e:
        print(f"Error in palette_route: {str(e)}")
        return jsonify({"error": str(e)}), 400

# ============ AUTHENTICATION ROUTES ============

@app.route('/login', methods=['POST'])
def login():
    """Login endpoint with result saving support"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        analysis_results = data.get('analysis_results')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Missing username or password'
            }), 400
        
        # Load users
        users = load_users()
        
        # Check if user exists
        if username not in users:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 401
        
        # Verify password
        user = users[username]
        if not check_password_hash(user['password'], password):
            return jsonify({
                'success': False,
                'message': 'Incorrect password'
            }), 401
        
        # Save analysis results if provided
        if analysis_results:
            try:
                save_user_result(username, analysis_results)
                print(f"✓ Saved analysis results for user: {username}")
            except Exception as e:
                print(f"Warning: Could not save analysis results: {e}")
        
        # Generate JWT token
        token = jwt.encode({
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'token': token,
            'username': username,
            'user_id': username
        })
            
    except Exception as e:
        print(f"Error in login: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/signup', methods=['POST'])
def signup():
    """Signup endpoint with result saving support"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        analysis_results = data.get('analysis_results')
        
        # Validate input
        if not username or not password or not email:
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        # Check if user already exists
        users = load_users()
        if username in users:
            return jsonify({
                'success': False,
                'error': 'Username already exists'
            }), 400
        
        # Check if email already exists
        for user in users.values():
            if user['email'] == email:
                return jsonify({
                    'success': False,
                    'error': 'Email already registered'
                }), 400
        
        # Save new user
        save_user(username, email, password)
        print(f"✓ Created new user: {username}")
        
        # Save analysis results if provided
        if analysis_results:
            try:
                save_user_result(username, analysis_results)
                print(f"✓ Saved initial analysis results for user: {username}")
            except Exception as e:
                print(f"Warning: Could not save analysis results: {e}")
        
        # Generate JWT token
        token = jwt.encode({
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully',
            'token': token,
            'username': username,
            'user_id': username
        })
            
    except Exception as e:
        print(f"Error in signup: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============ USER RESULTS ROUTES ============

@app.route('/user/results', methods=['POST'])
def get_user_results_route():
    """Get all saved results for a user"""
    try:
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({'error': 'Username required'}), 400
        
        # Get user's results
        results = get_user_results(username)
        
        return jsonify({
            'success': True,
            'username': username,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        print(f"Error in get_user_results_route: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/user/save-result', methods=['POST'])
def save_result_route():
    """Save a new analysis result for a logged-in user"""
    try:
        data = request.get_json()
        username = data.get('username')
        result = data.get('result')
        
        if not username or not result:
            return jsonify({'error': 'Username and result required'}), 400
        
        # Save the result
        save_user_result(username, result)
        
        return jsonify({
            'success': True,
            'message': 'Result saved successfully'
        })
        
    except Exception as e:
        print(f"Error in save_result_route: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/user/delete-result', methods=['POST'])
def delete_result_route():
    """Deletes analysis result for the user"""
    try:
        data = request.get_json()
        username = data.get('username')
        timestamp = data.get('timestamp')

        if not username or not timestamp:
            return jsonify({'error': 'Username and timestamp required'}), 400
        
        all_results = load_results()

        if username in all_results:
            original_count = len(all_results[username])
            all_results[username] = [r for r in all_results[username] if r.get('timestamp') != timestamp]

            if len(all_results[username]) < original_count:
                save_results(all_results)
                return jsonify({'success': True, 'message': 'Result deleted successfully'})
            else:
                return jsonify({'error': 'User not found'}), 404
        
    except Exception as e:
        print(f"Error in delete_result_route: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============ SETTINGS ROUTES ============

@app.route('/get-user-info', methods=['POST'])
def get_user_info():
    try:
        data = request.get_json()
        username = data.get('username')

        users = load_users()
        
        if username in users:
            user = users[username]
            return jsonify({
                'username': user['username'],
                'email': user['email']
            })
        
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        print(f"Error getting user info: {e}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/update-password', methods=['POST'])
def update_password():
    try:
        data = request.get_json()
        username = data.get('username')
        old_password = data.get('oldPassword')
        new_password = data.get('newPassword')

        if not os.path.exists(USERS_FILE):
            return jsonify({'success': False, 'message': 'Database error'}), 500
        
        with open(USERS_FILE, 'r') as f:
            lines = f.readlines()
        
        new_lines = []
        user_found = False
        password_correct = False

        for line in lines:
            line = line.strip()
            if not line: continue

            parts = line.split(':', 2)

            if parts[0] == username:
                user_found = True
                # Check if old password matches
                if len(parts) >= 3 and check_password_hash(parts[2], old_password):
                    password_correct = True
                    # Create new line with new password
                    new_password_hash = generate_password_hash(new_password)
                    new_line = f"{parts[0]}:{parts[1]}:{new_password_hash}\n"
                    new_lines.append(new_line)
                else:
                    # Old password is wrong
                    new_lines.append(line + '\n')
            else:
                # Not the user
                new_lines.append(line + '\n')
        
        if not user_found:
            return jsonify({'success': False, 'message': 'User not found'})
        
        if not password_correct:
            return jsonify({'success': False, 'message': 'Old password is incorrect'})
        
        with open(USERS_FILE, 'w') as f:
            f.writelines(new_lines)

        return jsonify({'success': True, 'message': 'Password updated successfully'})
    
    except Exception as e:
        print(f"Error updating password: {e}")
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Check if frontend folder exists
    if not os.path.exists('frontend'):
        print("Warning: 'frontend' folder not found!")
        print("Please make sure your HTML files are in a 'frontend' folder")
    
    # Check if logic folder exists
    if not os.path.exists('logic'):
        print("Warning: 'logic' folder not found!")
        print("Please make sure colorpalette.py and undertone.py are in a 'logic' folder")
    
    # Create users file if it doesn't exist
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            pass
        print(f"✓ Created {USERS_FILE}")
    
    # Create results file if it doesn't exist
    if not os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'w') as f:
            json.dump({}, f)
        print(f"✓ Created {RESULTS_FILE}")
    
    print("\n" + "="*50)
    print("ColorMe Application Starting...")
    print("="*50)
    print("Frontend: http://localhost:5001")
    print("API Endpoints:")
    print("  - GET  /health")
    print("  - POST /analyze")
    print("  - POST /palette")
    print("  - POST /login")
    print("  - POST /signup")
    print("  - POST /user/results")
    print("  - POST /user/save-result")
    print("  - POST /get-user-info")
    print("  - POST /update-password")
    print("="*50 + "\n")
    
    # Run the Flask app
    app.run(debug=True, use_reloader=False, port=5001, host='0.0.0.0')
