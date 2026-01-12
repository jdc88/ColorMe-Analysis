from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from sklearn.cluster import KMeans
import cv2
import numpy as np
from PIL import Image
import io
import os

# Import your analysis modules
try:
    from colorpalette import determine_season
    from undertone import analyze_undertone
except ImportError:
    # Fallback functions if modules don't exist yet
    def determine_season(skin_rgb, hair_rgb, eye_rgb):
        return "Spring"
    
    def analyze_undertone(skin_rgb):
        return "warm"

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)  # Enable CORS for frontend-backend communication

# Extract colors using KMeans
def extract_dominant_colors(image, num_colors=3):
    """
    Input: image (OpenCV BGR array)
    Output: list of dominant RGB colors
    """
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = image.reshape((-1, 3))
    kmeans = KMeans(n_clusters=num_colors, n_init=10)
    kmeans.fit(image)
    colors = kmeans.cluster_centers_.astype(int)
    return colors.tolist()

def parse_rgb(rgb_string):
    """Convert 'rgb(255, 255, 255)' to (255, 255, 255)"""
    rgb_string = rgb_string.replace('rgb(', '').replace(')', '').strip()
    r, g, b = map(int, [x.strip() for x in rgb_string.split(',')])
    return (r, g, b)

# Serve the frontend files
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory('frontend', path)
    except:
        return send_from_directory('frontend', 'index.html')

# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "Backend running", 
        "model": "KMeans color extraction + Season analysis"
    })

# Color analysis endpoint - receives RGB values from frontend color picker
@app.route('/analyze', methods=['POST'])
def analyze_colors():
    try:
        data = request.get_json()
        
        # Get RGB colors from frontend
        skin_color = data.get('skin')
        hair_color = data.get('hair')
        eye_color = data.get('eyes')
        
        if not all([skin_color, hair_color, eye_color]):
            return jsonify({'error': 'Missing color data'}), 400
        
        # Convert RGB strings to tuples
        skin_rgb = parse_rgb(skin_color)
        hair_rgb = parse_rgb(hair_color)
        eye_rgb = parse_rgb(eye_color)
        
        # Call your color analysis functions
        season = determine_season(skin_rgb, hair_rgb, eye_rgb)
        undertone = analyze_undertone(skin_rgb)
        
        # Return results
        return jsonify({
            'season': season,
            'undertone': undertone,
            'skin_rgb': skin_rgb,
            'hair_rgb': hair_rgb,
            'eye_rgb': eye_rgb,
            'message': f'Your color season is {season} with {undertone} undertones!'
        })
        
    except Exception as e:
        print(f"Error in analyze_colors: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Image upload endpoint - for automatic color extraction using KMeans
@app.route('/extract_colors', methods=['POST'])
def extract_colors():
    """Extract dominant colors from uploaded image using KMeans"""
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400
        
        file = request.files['image']
        
        # Read image
        image_stream = np.array(Image.open(io.BytesIO(file.read())))
        image_cv = cv2.cvtColor(image_stream, cv2.COLOR_RGB2BGR)
        
        # Get number of colors to extract
        num_colors = int(request.form.get('num_colors', 3))
        
        # Extract dominant colors
        colors = extract_dominant_colors(image_cv, num_colors=num_colors)
        
        return jsonify({"dominant_colors": colors})
        
    except Exception as e:
        print(f"Error in extract_colors: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        # TODO: Add your authentication logic here
        # For now, just a simple check
        if username and password:
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'username': username
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Signup endpoint
@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        
        # TODO: Add your user registration logic here
        if username and password and email:
            return jsonify({
                'success': True,
                'message': 'Account created successfully',
                'username': username
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
