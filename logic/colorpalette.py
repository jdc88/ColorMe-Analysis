
"""
Color Palette and Season Analysis Module
Combines color palette generation with seasonal color analysis
"""

import colorsys
import numpy as np

# Convert HEX <-> RGB
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % tuple(int(x) for x in rgb)

# Rotate hue (in HSV space)
def adjust_hue(rgb, degree_shift):
    r, g, b = [x/255.0 for x in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h = (h + degree_shift / 360.0) % 1.0
    r2, g2, b2 = colorsys.hsv_to_rgb(h, s, v)
    return [r2 * 255, g2 * 255, b2 * 255]

# Generate palette from one color
def generate_palette(base_color, palette_type="complementary"):
    """
    palette_type: 'complementary', 'analogous', 'triadic', 'monochromatic', 'split_complementary'
    base_color: [R, G, B] or '#RRGGBB'
    """
    if isinstance(base_color, str):
        base_rgb = np.array(hex_to_rgb(base_color))
    else:
        base_rgb = np.array(base_color)

    palette = []

    if palette_type == "complementary":
        palette = [base_rgb, adjust_hue(base_rgb, 180)]
    elif palette_type == "analogous":
        palette = [adjust_hue(base_rgb, -30), base_rgb, adjust_hue(base_rgb, 30)]
    elif palette_type == "triadic":
        palette = [base_rgb, adjust_hue(base_rgb, 120), adjust_hue(base_rgb, 240)]
    elif palette_type == "split_complementary":
        palette = [base_rgb, adjust_hue(base_rgb, 150), adjust_hue(base_rgb, 210)]
    elif palette_type == "monochromatic":
        # Generate lighter/darker variations of the same hue
        r, g, b = base_rgb
        for factor in [0.5, 0.75, 1.0, 1.25, 1.5]:
            new_color = np.clip(base_rgb * factor, 0, 255)
            palette.append(new_color)
    else:
        raise ValueError("Palette type not specified.") 

    # Convert to HEX for frontend readability
    palette_hex = [rgb_to_hex(color) for color in palette]
    return palette_hex

# ========== SEASONAL COLOR ANALYSIS FUNCTIONS ==========

def rgb_to_hsv(rgb):
    """Convert RGB tuple to HSV"""
    r, g, b = [x / 255.0 for x in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return (h * 360, s, v)  # Return hue in degrees

def calculate_contrast(color1_rgb, color2_rgb):
    """Calculate contrast between two colors"""
    def luminance(rgb):
        r, g, b = [x / 255.0 for x in rgb]
        return 0.299 * r + 0.587 * g + 0.114 * b
    
    lum1 = luminance(color1_rgb)
    lum2 = luminance(color2_rgb)
    
    return abs(lum1 - lum2)

def determine_season(skin_rgb, hair_rgb, eye_rgb):
    """
    Determine color season based on skin, hair, and eye colors
    Returns: 'Spring', 'Summer', 'Autumn', or 'Winter'
    
    Theory:
    - Spring: Warm, bright, clear colors (warm undertone, high contrast)
    - Summer: Cool, soft, muted colors (cool undertone, low contrast)
    - Autumn: Warm, deep, muted colors (warm undertone, low-medium contrast)
    - Winter: Cool, bright, clear colors (cool undertone, high contrast)
    """
    
    # Convert to HSV for better color analysis
    skin_hsv = rgb_to_hsv(skin_rgb)
    hair_hsv = rgb_to_hsv(hair_rgb)
    eye_hsv = rgb_to_hsv(eye_rgb)
    
    # Analyze skin undertone with more sensitivity
    skin_r, skin_g, skin_b = skin_rgb
    
    # More nuanced warm/cool detection
    # Warm: More red and yellow (R+G > B)
    # Cool: More blue and pink (B >= R or B > G significantly)
    red_to_blue_ratio = skin_r / max(skin_b, 1)
    yellow_component = (skin_r + skin_g) / 2
    warm_score = (yellow_component - skin_b) / 255.0
    
    # Additional undertone check using green channel
    # Warm skin has more yellow (higher green relative to blue)
    # Cool skin has more pink/blue
    green_blue_diff = (skin_g - skin_b) / 255.0
    
    # Combined warm score
    combined_warm = (warm_score * 0.6) + (green_blue_diff * 0.4)
    
    # Calculate overall saturation (color intensity)
    avg_saturation = (skin_hsv[1] + hair_hsv[1] + eye_hsv[1]) / 3
    
    # Calculate contrast between features (CRITICAL for Winter detection)
    contrast_skin_hair = calculate_contrast(skin_rgb, hair_rgb)
    contrast_skin_eye = calculate_contrast(skin_rgb, eye_rgb)
    contrast_hair_eye = calculate_contrast(hair_rgb, eye_rgb)
    overall_contrast = (contrast_skin_hair + contrast_skin_eye + contrast_hair_eye) / 3
    
    # Calculate value/brightness from HSV
    skin_brightness = skin_hsv[2]
    hair_brightness = hair_hsv[2]
    eye_brightness = eye_hsv[2]
    
    # Calculate how saturated/muted the colors are
    skin_saturation = skin_hsv[1]
    hair_saturation = hair_hsv[1]
    eye_saturation = eye_hsv[1]
    
    # CRITICAL: Hair darkness factor (very important for Winter detection!)
    hair_is_very_dark = hair_brightness < 0.25  # Almost black
    hair_is_dark = hair_brightness < 0.35
    hair_is_medium = 0.35 <= hair_brightness <= 0.55
    hair_is_light = hair_brightness > 0.55
    hair_is_very_light = hair_brightness > 0.7
    
    # Skin brightness categories
    skin_is_very_light = skin_brightness > 0.75
    skin_is_light = skin_brightness > 0.6
    skin_is_medium = 0.45 <= skin_brightness <= 0.6
    skin_is_deep = skin_brightness < 0.45
    
    # Eye color analysis
    eye_is_light = eye_brightness > 0.5
    eye_is_dark = eye_brightness < 0.35
    eye_is_saturated = eye_hsv[1] > 0.3
    
    # WINTER PRIORITY CHECK (most distinctive season)
    # Winter = Cool undertone + HIGH contrast + Clear colors
    is_very_high_contrast = contrast_skin_hair > 0.35
    is_high_contrast = overall_contrast > 0.25
    
    # CRITICAL: Check for classic Winter FIRST: Very dark hair + Light skin
    # This is the most distinctive Winter characteristic
    # CONTRAST IS MORE IMPORTANT THAN UNDERTONE for Winter!
    if (hair_is_very_dark or hair_is_dark) and (skin_is_light or skin_is_very_light):
        # Classic high-contrast Winter look
        # Very dark hair + light skin = Winter (regardless of slight warm undertones)
        if contrast_skin_hair > 0.3:  # Significant contrast
            # Don't check undertone - contrast is king for Winter
            # Even if skin reads slightly warm, high contrast + dark hair = Winter
            print(f"  → Winter detected: Dark hair ({hair_brightness:.2f}) + Light skin ({skin_brightness:.2f}) + High contrast ({contrast_skin_hair:.2f})")
            return "Winter"
    
    # Additional Winter check: Medium-dark hair with very high contrast
    if hair_brightness < 0.4 and contrast_skin_hair > 0.4:
        if combined_warm < 0.08:  # Not strongly warm
            print(f"  → Winter detected: Medium-dark hair + Very high contrast")
            return "Winter"
    
    # Check for Winter with any dark hair and decent contrast
    if hair_is_dark and contrast_skin_hair > 0.35:
        # High enough contrast with dark hair usually means Winter
        if not (combined_warm > 0.1):  # Not very strongly warm
            print(f"  → Winter detected: Dark hair + High contrast + Not very warm")
            return "Winter"
    
    # Decision logic for undertone
    is_warm = combined_warm > 0.03  # Warm undertone
    is_cool = combined_warm < -0.01  # Cool undertone
    is_neutral = not is_warm and not is_cool
    
    # Brightness and clarity
    is_bright_clear = avg_saturation > 0.35 and skin_brightness > 0.55
    is_muted_soft = avg_saturation < 0.25 or (skin_brightness < 0.45 and skin_brightness > 0.25)
    
    # WINTER: Cool + High Contrast + Clear
    if is_cool or (is_neutral and combined_warm <= 0.01):
        if is_high_contrast:
            # High contrast with cool tones = Winter
            return "Winter"
        elif is_muted_soft or hair_is_light:
            # Cool + Low contrast or soft = Summer
            return "Summer"
        else:
            # Default cool with medium features
            return "Summer"
    
    # WARM UNDERTONES: Spring or Autumn
    elif is_warm:
        if is_high_contrast and is_bright_clear:
            # Warm + High Contrast + Bright = Spring
            return "Spring"
        elif hair_is_dark or is_muted_soft:
            # Warm + Dark features or muted = Autumn
            return "Autumn"
        else:
            # Default warm = Spring
            return "Spring"
    
    # NEUTRAL UNDERTONES: Look at other factors
    else:
        if is_very_high_contrast and (hair_is_very_dark or hair_is_dark):
            # Neutral but high contrast with dark hair = Winter
            return "Winter"
        elif is_high_contrast:
            # Neutral + high contrast = likely Spring
            return "Spring"
        elif is_muted_soft:
            # Neutral + muted = Summer
            return "Summer"
        else:
            # Default neutral
            return "Summer"

def get_season_description(season):
    """Get detailed description of each season's characteristics"""
    descriptions = {
        # WINTER SUBTYPES
        "Clear Winter": {
            "colors": ["Icy, vivid, high-contrast colors", "True red", "Bright white", "Black", "Royal blue", "Hot pink"],
            "best_colors": ["Icy pink", "Pure white", "Black", "True red", "Royal blue", "Emerald"],
            "avoid_colors": ["Muted tones", "Earth tones", "Warm oranges", "Beige"],
            "metals": "Silver and white gold suit you best",
            "characteristics": "High contrast with bright, clear, icy colors"
        },
        "Cool Winter": {
            "colors": ["Cool, clear, intense colors", "Navy", "Pure white", "Burgundy", "Pine green", "Magenta"],
            "best_colors": ["Navy", "Pure white", "Cool red", "Icy blue", "Purple", "Emerald"],
            "avoid_colors": ["Orange", "Warm browns", "Golden yellow"],
            "metals": "Silver jewelry suits you best",
            "characteristics": "Cool undertone with high contrast, classic winter look"
        },
        "Deep Winter": {
            "colors": ["Deep, dramatic, cool colors", "Charcoal", "Deep purple", "Navy", "Pine", "Ruby"],
            "best_colors": ["Black", "Charcoal", "Deep purple", "Navy", "Ruby red", "Teal"],
            "avoid_colors": ["Pastels", "Light colors", "Warm browns", "Orange"],
            "metals": "Silver and platinum suit you best",
            "characteristics": "Deep, rich coloring with high contrast"
        },
        
        # SUMMER SUBTYPES
        "Light Summer": {
            "colors": ["Soft, light, cool-toned colors", "Sky blue", "Rose pink", "Lavender", "Mint"],
            "best_colors": ["Powder blue", "Rose", "Lavender", "Soft pink", "Cool gray", "Periwinkle"],
            "avoid_colors": ["Black", "Orange", "Bright colors", "Dark colors"],
            "metals": "Rose gold and silver suit you best",
            "characteristics": "Light, delicate coloring with low contrast"
        },
        "Cool Summer": {
            "colors": ["Cool, soft, elegant colors", "Soft blue", "Rose", "Cocoa", "Mauve"],
            "best_colors": ["Soft blue", "Dusty rose", "Mauve", "Cool gray", "Soft white", "Plum"],
            "avoid_colors": ["Orange", "Warm browns", "Bright colors"],
            "metals": "Silver jewelry suits you best",
            "characteristics": "Cool undertone with medium-low contrast, elegant look"
        },
        "Soft Summer": {
            "colors": ["Soft, muted, cool-toned colors", "Dusty rose", "Soft blue", "Mauve", "Pewter"],
            "best_colors": ["Dusty rose", "Soft blue", "Mauve", "Gray-green", "Taupe", "Lavender"],
            "avoid_colors": ["Bright colors", "Black", "Orange", "Bright yellow"],
            "metals": "Silver and pewter suit you best",
            "characteristics": "Soft, muted coloring with low contrast"
        },
        
        # SPRING SUBTYPES
        "Light Spring": {
            "colors": ["Light, warm, delicate colors", "Peach", "Light aqua", "Coral", "Cream"],
            "best_colors": ["Peach", "Light coral", "Cream", "Light aqua", "Warm pink", "Camel"],
            "avoid_colors": ["Black", "Dark colors", "Cool tones"],
            "metals": "Gold and rose gold suit you best",
            "characteristics": "Light, warm coloring with delicate clarity"
        },
        "Warm Spring": {
            "colors": ["Warm, golden, clear colors", "Coral", "Golden yellow", "Peach", "Turquoise"],
            "best_colors": ["Coral", "Golden yellow", "Peach", "Warm pink", "Clear aqua", "Camel"],
            "avoid_colors": ["Cool tones", "Black", "Dark navy", "Burgundy"],
            "metals": "Gold jewelry suits you best",
            "characteristics": "Warm undertone with golden, sunny coloring"
        },
        "Clear Spring": {
            "colors": ["Clear, bright, warm colors", "Coral red", "Bright aqua", "Warm pink", "Clear yellow"],
            "best_colors": ["Coral", "Clear aqua", "Bright warm pink", "Golden yellow", "Orange", "Kelly green"],
            "avoid_colors": ["Muted tones", "Cool tones", "Black"],
            "metals": "Gold and bright metals suit you best",
            "characteristics": "Warm with high clarity and brightness"
        },
        
        # AUTUMN SUBTYPES
        "Soft Autumn": {
            "colors": ["Soft, muted, warm earth tones", "Olive", "Rust", "Camel", "Sage"],
            "best_colors": ["Olive", "Rust", "Camel", "Sage green", "Warm beige", "Terracotta"],
            "avoid_colors": ["Bright colors", "Cool tones", "Black", "Pure white"],
            "metals": "Antique gold and bronze suit you best",
            "characteristics": "Soft, muted warm coloring with low contrast"
        },
        "Warm Autumn": {
            "colors": ["Warm, rich, earthy colors", "Rust", "Olive", "Burnt orange", "Warm brown"],
            "best_colors": ["Rust", "Warm brown", "Olive green", "Burnt orange", "Terracotta", "Golden tan"],
            "avoid_colors": ["Cool tones", "Pastels", "Black", "Icy colors"],
            "metals": "Gold and copper suit you best",
            "characteristics": "Strong warm undertone with rich, earthy coloring"
        },
        "Deep Autumn": {
            "colors": ["Deep, warm, rich colors", "Forest green", "Burgundy", "Chocolate", "Deep orange"],
            "best_colors": ["Forest green", "Burgundy", "Chocolate brown", "Deep orange", "Rust", "Olive"],
            "avoid_colors": ["Pastels", "Icy colors", "Cool pinks", "Light colors"],
            "metals": "Gold and aged metals suit you best",
            "characteristics": "Deep, rich warm coloring with strong presence"
        },
        
        # Legacy 4-season support
        "Winter": {
            "colors": ["Cool, bright, clear colors", "True red", "Navy blue", "Pure white", "Hot pink"],
            "best_colors": ["True red", "Royal blue", "Pure white", "Black", "Hot pink", "Emerald green"],
            "avoid_colors": ["Orange", "Gold", "Warm browns"],
            "metals": "Silver jewelry suits you best",
            "characteristics": "Cool undertone with high contrast coloring"
        },
        "Summer": {
            "colors": ["Cool, soft, muted colors", "Rose pink", "Lavender", "Soft blue", "Mauve"],
            "best_colors": ["Soft pink", "Lavender", "Powder blue", "Rose", "Soft white", "Light gray"],
            "avoid_colors": ["Orange", "Bright yellow", "True black"],
            "metals": "Silver jewelry suits you best",
            "characteristics": "Cool undertone with soft, muted coloring"
        },
        "Spring": {
            "colors": ["Warm, clear, bright colors", "Peachy pinks", "Coral", "Golden yellow", "Bright green"],
            "best_colors": ["Peach", "Coral", "Golden yellow", "Warm pink", "Turquoise", "Light orange"],
            "avoid_colors": ["Black", "Pure white", "Dark navy", "Burgundy"],
            "metals": "Gold jewelry suits you best",
            "characteristics": "Warm undertone with bright, clear coloring"
        },
        "Autumn": {
            "colors": ["Warm, deep, muted colors", "Rust", "Olive green", "Camel", "Deep orange"],
            "best_colors": ["Rust", "Olive", "Camel", "Warm brown", "Terracotta", "Forest green"],
            "avoid_colors": ["Pastel colors", "Cool pinks", "Bright white"],
            "metals": "Gold jewelry suits you best",
            "characteristics": "Warm undertone with rich, earthy coloring"
        }
    }
    return descriptions.get(season, {})

def get_season_palette(season, base_color=None):
    """
    Generate a color palette suitable for the given season
    Returns hex color codes
    """
    season_colors = {
        "Spring": ["#FFB6C1", "#FF7F50", "#FFD700", "#98FB98", "#87CEEB"],
        "Summer": ["#E6B8E6", "#B0C4DE", "#FFB6C1", "#D8BFD8", "#F5F5DC"],
        "Autumn": ["#CD853F", "#808000", "#D2691E", "#8B4513", "#556B2F"],
        "Winter": ["#FF0000", "#000080", "#FFFFFF", "#FF1493", "#50C878"]
    }
    
    # If a base color is provided, generate a palette based on season's recommended type
    if base_color:
        season_info = get_season_description(season)
        palette_type = season_info.get("palette_type", "complementary")
        return generate_palette(base_color, palette_type)
    
    return season_colors.get(season, season_colors["Spring"])

# Example usage and testing
if __name__ == "__main__":
    # Test seasonal analysis
    print("=== Testing Seasonal Color Analysis ===")
    
    test_cases = [
        ((220, 180, 150), (50, 30, 20), (100, 80, 60), "Light peachy skin, dark hair, brown eyes"),
        ((240, 220, 210), (200, 180, 150), (150, 180, 200), "Light cool skin, light hair, blue eyes"),
        ((180, 140, 110), (70, 40, 20), (80, 60, 40), "Medium warm skin, dark hair, brown eyes"),
        ((200, 190, 190), (40, 40, 50), (100, 120, 140), "Light cool skin, dark hair, blue eyes")
    ]
    
    for skin, hair, eyes, description in test_cases:
        season = determine_season(skin, hair, eyes)
        print(f"\n{description}")
        print(f"RGB - Skin: {skin}, Hair: {hair}, Eyes: {eyes}")
        print(f"Season: {season}")
        print(f"Characteristics: {get_season_description(season)['characteristics']}")
        print(f"Best metals: {get_season_description(season)['metals']}")
    
    # Test palette generation
    print("\n\n=== Testing Palette Generation ===")
    base_color = [255, 100, 100]
    for palette_type in ["complementary", "analogous", "triadic", "monochromatic"]:
        palette = generate_palette(base_color, palette_type)
        print(f"\n{palette_type.title()}: {palette}")
