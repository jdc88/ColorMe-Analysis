"""
Skin Undertone Analysis Module
Determines whether someone has warm, cool, or neutral undertones
"""
import colorsys

def rgb_to_hsv(rgb):
    """
    Convert RGB tuple to HSV
    """
    r, g, b = [x / 255.0 for x in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return (h * 360, s * 100, v * 100)

def analyze_undertone(skin_rgb):
    """
    Analyze skin undertone from RGB values
    Returns: 'warm', 'cool', or 'neutral'
    
    Theory:
    - Warm undertones: Yellow, peachy, golden base (more red and yellow)
    - Cool undertones: Pink, rosy, bluish base (more blue)
    - Neutral undertones: Mix of warm and cool (balanced)
    """
    r, g, b = skin_rgb
    
    # Normalize values
    if r + g + b == 0:
        return "neutral"
    
    # Method 1: Blue component analysis (MOST IMPORTANT)
    # Cool skin has higher blue relative to the other channels
    # Warm skin has lower blue
    blue_ratio = b / max((r + g) / 2, 1)
    
    # Method 2: Red vs Blue direct comparison
    # This is critical - even peachy skin can be cool if blue is close to red
    red_blue_diff = r - b
    
    # Method 3: Green-Blue relationship
    # Warm: green > blue (yellow tones)
    # Cool: blue >= green (pink/blue tones)
    green_blue_diff = g - b
    
    # Method 4: Check if skin is more pink (cool) or peach (warm)
    # Pink = high red BUT also high blue
    # Peach = high red but LOW blue
    is_pink = (r > g) and (b / max(r, 1) > 0.85)  # Blue is close to red = pink
    is_peach = (r > g) and (b / max(r, 1) < 0.80)  # Blue much less than red = peach
    
    # Method 5: Overall yellow vs blue
    print(f"  Undertone Debug:")
    print(f"    Red-Blue diff: {red_blue_diff}")
    print(f"    Green-Blue diff: {green_blue_diff}")
    print(f"    Blue ratio: {blue_ratio:.3f}")
    print(f"    Is pink: {is_pink}, Is peach: {is_peach}")
    
    # DECISION LOGIC - More nuanced
    
    # Strong Cool Indicators
    if is_pink:
        return "cool"
    
    if b > r:  # Blue higher than red = definitely cool
        return "cool"
    
    if blue_ratio > 0.95:  # Blue very close to average of r+g
        return "cool"
    
    if red_blue_diff < 15 and green_blue_diff < 10:
        # Red and blue are very close = cool/neutral
        return "cool"
    
    # Strong Warm Indicators
    if is_peach:
        return "warm"
    
    if red_blue_diff > 35 and green_blue_diff > 25:
        # Significant yellow tones = warm
        return "warm"
    
    if blue_ratio < 0.80:  # Blue much lower than r+g average
        return "warm"
    
    # Medium Warm
    if red_blue_diff > 25 and green_blue_diff > 15:
        return "warm"
    
    # Medium Cool  
    if red_blue_diff < 20:
        return "cool"
    
    # Default to neutral for borderline cases
    return "neutral"

def get_undertone_recommendations(undertone):
    """Get color and makeup recommendations based on undertone"""
    recommendations = {
        "warm": {
            "best_colors": [
                "Earth tones (brown, beige, olive)",
                "Warm reds and oranges",
                "Golden yellows",
                "Warm greens"
            ],
            "avoid_colors": [
                "Jewel tones",
                "Icy blues and pinks",
                "Pure white"
            ],
            "jewelry": "Gold and copper look best on you",
            "makeup_tips": [
                "Use warm-toned foundations with yellow or golden undertones",
                "Try peachy or coral blushes",
                "Warm brown or bronze eyeshadows",
                "Warm red or coral lipsticks"
            ],
            "hair_colors": [
                "Golden blonde",
                "Warm brown",
                "Auburn",
                "Copper red"
            ]
        },
        "cool": {
            "best_colors": [
                "Jewel tones (sapphire, emerald, ruby)",
                "Cool blues and purples",
                "Pink and berry shades",
                "Pure white and black"
            ],
            "avoid_colors": [
                "Orange and warm browns",
                "Mustard yellow",
                "Olive green"
            ],
            "jewelry": "Silver and platinum look best on you",
            "makeup_tips": [
                "Use cool-toned foundations with pink undertones",
                "Try pink or berry blushes",
                "Cool-toned purples and silvers for eyeshadow",
                "Cool pink or berry lipsticks"
            ],
            "hair_colors": [
                "Ash blonde",
                "Cool brown",
                "Burgundy",
                "Blue-black"
            ]
        },
        "neutral": {
            "best_colors": [
                "You can wear both warm and cool colors!",
                "Try muted tones",
                "Soft pastels",
                "Medium-depth colors"
            ],
            "avoid_colors": [
                "Very extreme warm or cool colors might be less flattering"
            ],
            "jewelry": "Both gold and silver look good on you",
            "makeup_tips": [
                "Look for 'neutral' labeled foundations",
                "You have flexibility with most makeup colors",
                "Experiment with both warm and cool tones"
            ],
            "hair_colors": [
                "Most hair colors work well",
                "Try balanced tones",
                "Medium browns",
                "Natural shades"
            ]
        }
    }
    return recommendations.get(undertone, {})

def analyze_detailed_undertone(skin_rgb):
    """
    More detailed undertone analysis with percentages
    Returns a dictionary with undertone and confidence scores
    """
    r, g, b = skin_rgb
    
    # Calculate various color ratios
    total = r + g + b
    if total == 0:
        return {
            "undertone": "neutral",
            "warm_percentage": 33,
            "cool_percentage": 33,
            "neutral_percentage": 34
        }
        
    # Warm score (more red and yellow/green)
    warm_indicator = (r + g - 2*b) / total
    
    # Cool score (more blue)
    cool_indicator = (b - ((r + g) / 2)) / total
    
    # Convert to percentages
    if warm_indicator > 0.1:
        warm_pct = min(70 + warm_indicator * 100, 100)
        cool_pct = max(30 - warm_indicator * 100, 0)
        neutral_pct = 100 - warm_pct - cool_pct
        undertone = "warm"
    elif cool_indicator > 0.05:
        cool_pct = min(70 + cool_indicator * 100, 100)
        warm_pct = max(30 - cool_indicator * 100, 0)
        neutral_pct = 100 - warm_pct - cool_pct
        undertone = "cool"
    else:
        warm_pct = 40
        cool_pct = 35
        neutral_pct = 25
        undertone = "neutral"
    
    return {
        "undertone": undertone,
        "warm_percentage": round(warm_pct, 1),
        "cool_percentage": round(cool_pct, 1),
        "neutral_percentage": round(neutral_pct, 1),
        "rgb": skin_rgb
    }

def get_vein_color_meaning():
    """
    Provides information about the vein test for undertones
    This is educational content for users
    """
    return {
        "green_veins": "Warm undertone - Your veins appear greenish, indicating warm undertones",
        "blue_purple_veins": "Cool undertone - Your veins appear blue or purple, indicating cool undertones",
        "both": "Neutral undertone - Your veins appear to be a mix, indicating neutral undertones",
        "instructions": "Look at the veins on your wrist in natural light to help determine your undertone"
    }

def get_jewelry_test_info():
    """
    Information about the jewelry test for undertones
    """
    return {
        "gold_looks_better": "Warm undertone - If gold jewelry flatters you more",
        "silver_looks_better": "Cool undertone - If silver jewelry flatters you more",
        "both_look_good": "Neutral undertone - If both metals look equally good on you",
        "instructions": "Hold gold and silver jewelry near your face in natural light and see which makes your skin glow"
    }

# Example usage and testing
if __name__ == "__main__":
    print("=== Testing Skin Undertone Analysis ===\n")
    
    # Test with example skin tones
    test_skins = [
        ((230, 180, 140), "Light warm skin"),
        ((200, 170, 170), "Light cool skin"),
        ((210, 190, 175), "Light neutral skin"),
        ((150, 120, 100), "Medium warm skin"),
        ((120, 100, 110), "Medium cool skin"),
        ((135, 115, 110), "Medium neutral skin"),
        ((80, 60, 50), "Deep warm skin"),
        ((70, 55, 60), "Deep cool skin"),
        ((75, 60, 58), "Deep neutral skin")
    ]
    
    for rgb, description in test_skins:
        undertone = analyze_undertone(rgb)
        detailed = analyze_detailed_undertone(rgb)
        recommendations = get_undertone_recommendations(undertone)
        
        print(f"{description}: RGB{rgb}")
        print(f"  Undertone: {undertone.upper()}")
        print(f"  Breakdown: Warm {detailed['warm_percentage']}%, Cool {detailed['cool_percentage']}%, Neutral {detailed['neutral_percentage']}%")
        print(f"  Jewelry: {recommendations['jewelry']}")
        print(f"  Best colors: {', '.join(recommendations['best_colors'][:3])}")
        print()
    
    print("\n=== Undertone Tests Information ===")
    print("\nVein Test:")
    vein_info = get_vein_color_meaning()
    for key, value in vein_info.items():
        print(f"  {key}: {value}")
    
    print("\nJewelry Test:")
    jewelry_info = get_jewelry_test_info()
    for key, value in jewelry_info.items():
        print(f"  {key}: {value}")
