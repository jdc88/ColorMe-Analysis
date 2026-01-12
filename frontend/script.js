const BACKEND_URL = "http://127.0.0.1:5000";

// Send image to backend for color extraction
async function sendToBackend(imageFile) {
    const formData = new FormData();
    formData.append("image", imageFile);

    try {
        const response = await fetch(`${BACKEND_URL}/extract_colors`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Colors from backend:", data);
        return data;
    } catch (error) {
        console.error("Error extracting colors:", error);
        throw error;
    }
}

// Send color analysis to backend
async function analyzeColors(colorData) {
    try {
        const response = await fetch(`${BACKEND_URL}/analyze`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(colorData)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        return result;
    } catch (error) {
        console.error("Error analyzing colors:", error);
        throw error;
    }
}

// Store analysis results in sessionStorage for signup
function storeResultsForSignup(result, colors) {
    const resultsData = {
        season: result.season,
        undertone: result.undertone,
        message: result.message,
        colors: {
            skin: colors.skin,
            hair: colors.hair,
            eyes: colors.eyes
        },
        timestamp: new Date().toISOString()
    };

    sessionStorage.setItem('pendingResults', JSON.stringify(resultsData));
    console.log("Results stored for signup:", resultsData);
}

// Redirect to signup page with results
function saveAndSignUp() {
    // Check if results exist
    const pendingResults = sessionStorage.getItem('pendingResults');
    
    if (!pendingResults) {
        alert('Please analyze your colors first!');
        return;
    }

    // Redirect to signup page
    window.location.href = '/signup.html';
}

// Redirect to login page with results
function saveAndLogin() {
    // Check if results exist
    const pendingResults = sessionStorage.getItem('pendingResults');
    
    if (!pendingResults) {
        alert('Please analyze your colors first!');
        return;
    }

    // Redirect to login page with save parameter
    window.location.href = '/Login page.html?save=true';
}

// Clear stored results
function clearStoredResults() {
    sessionStorage.removeItem('pendingResults');
}

// Get stored results
function getStoredResults() {
    const results = sessionStorage.getItem('pendingResults');
    return results ? JSON.parse(results) : null;
}

// Export results as JSON file
function exportResults() {
    const results = getStoredResults();
    
    if (!results) {
        alert('No results to export!');
        return;
    }

    const dataStr = JSON.stringify(results, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `colorMe-analysis-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
}

// Display color palette
function displayColorPalette(colors, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const colorHTML = `
        <div style="display: flex; gap: 15px; justify-content: center; margin-top: 20px;">
            <div style="text-align: center;">
                <p style="margin-bottom: 5px; font-size: 12px;">Skin</p>
                <div style="width: 50px; height: 50px; background-color: ${colors.skin}; border: 3px solid white; border-radius: 50%;"></div>
            </div>
            <div style="text-align: center;">
                <p style="margin-bottom: 5px; font-size: 12px;">Hair</p>
                <div style="width: 50px; height: 50px; background-color: ${colors.hair}; border: 3px solid white; border-radius: 50%;"></div>
            </div>
            <div style="text-align: center;">
                <p style="margin-bottom: 5px; font-size: 12px;">Eyes</p>
                <div style="width: 50px; height: 50px; background-color: ${colors.eyes}; border: 3px solid white; border-radius: 50%;"></div>
            </div>
        </div>
    `;

    container.innerHTML = colorHTML;
}

// Convert RGB string to hex
function rgbToHex(rgb) {
    const result = rgb.match(/\d+/g);
    if (!result) return rgb;
    
    const r = parseInt(result[0]);
    const g = parseInt(result[1]);
    const b = parseInt(result[2]);
    
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}

// Format color data for backend
function formatColorData(skinRgb, hairRgb, eyesRgb) {
    return {
        skin: skinRgb,
        hair: hairRgb,
        eyes: eyesRgb,
        skin_hex: rgbToHex(skinRgb),
        hair_hex: rgbToHex(hairRgb),
        eyes_hex: rgbToHex(eyesRgb)
    };
}

// Initialize app - check for saved results on page load
document.addEventListener('DOMContentLoaded', () => {
    // Check if returning from signup/login
    const urlParams = new URLSearchParams(window.location.search);
    const fromSignup = urlParams.get('from');
    
    if (fromSignup === 'signup' || fromSignup === 'login') {
        // Clear stored results after successful signup/login
        clearStoredResults();
    }

    // Display any existing results
    const storedResults = getStoredResults();
    if (storedResults) {
        console.log('Found stored results:', storedResults);
    }
});

// Export functions for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        sendToBackend,
        analyzeColors,
        storeResultsForSignup,
        saveAndSignUp,
        saveAndLogin,
        clearStoredResults,
        getStoredResults,
        exportResults,
        displayColorPalette,
        rgbToHex,
        formatColorData
    };
}
