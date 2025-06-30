# constants.py
"""
This module centralizes all constants used throughout the Quick Tools application,
including color palettes, font definitions, and conversion factors.
"""

# --- Color Palettes ---
# These are used for the gradient generator and potentially other UI elements.
GRADIENT_STYLES = {
    'Analogous': [
        '#FF6B6B', '#FF8E53', '#FF6F91', '#C44569', '#F8B500', '#FFE66D',
        '#06FFA5', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3',
        '#54A0FF', '#5F27CD', '#00D2D3', '#FF9F43', '#10AC84', '#EE5A6F'
    ],
    'Complementary': [
        '#FF6B6B', '#4ECDC4', '#FF8E53', '#45B7D1', '#FFE66D', '#5F27CD',
        '#06FFA5', '#C44569', '#FECA57', '#54A0FF', '#FF9FF3', '#10AC84',
        '#F8B500', '#00D2D3', '#EE5A6F', '#96CEB4', '#FF9F43', '#6C5CE7'
    ],
    'Triadic': [
        '#FF6B6B', '#FECA57', '#45B7D1', '#C44569', '#06FFA5', '#5F27CD',
        '#FF8E53', '#FFE66D', '#4ECDC4', '#EE5A6F', '#10AC84', '#54A0FF',
        '#F8B500', '#96CEB4', '#6C5CE7', '#FF9FF3', '#00D2D3', '#A55EEA'
    ],
    'Tetradic': [
        '#FF6B6B', '#FECA57', '#45B7D1', '#06FFA5', '#C44569', '#FFE66D',
        '#4ECDC4', '#5F27CD', '#FF8E53', '#10AC84', '#54A0FF', '#EE5A6F',
        '#F8B500', '#96CEB4', '#6C5CE7', '#FF9FF3', '#00D2D3', '#A55EEA'
    ],
    'Warm': [
        '#FF6B6B', '#FF8E53', '#FFD93D', '#FECA57', '#F8B500', '#FFE66D',
        '#FF9F43', '#EE5A6F', '#C44569', '#FF6F91', '#F38BA8', '#F06292',
        '#FFA726', '#FF7043', '#FFAB91', '#FFCC80', '#FFB74D', '#FF8A65'
    ],
    'Cool': [
        '#45B7D1', '#4ECDC4', '#06FFA5', '#10AC84', '#96CEB4', '#54A0FF',
        '#5F27CD', '#6C5CE7', '#A55EEA', '#00D2D3', '#26C6DA', '#4DB6AC',
        '#81C784', '#64B5F6', '#7986CB', '#9575CD', '#BA68C8', '#42A5F5'
    ],
    'Neutral': [
        '#95A5A6', '#BDC3C7', '#ECF0F1', '#D5DBDB', '#AEB6BF', '#85929E',
        '#566573', '#34495E', '#2C3E50', '#ABB2B9', '#CCD1D1', '#F8F9FA',
        '#E5E8E8', '#D6DBDF', '#AAB7B8', '#85929E', '#5D6D7E', '#78909C'
    ],
    'Vibrant': [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9F43',
        '#EE5A6F', '#5F27CD', '#FF8E53', '#06FFA5', '#FFE66D', '#54A0FF',
        '#C44569', '#10AC84', '#6C5CE7', '#FF9FF3', '#F8B500', '#A55EEA'
    ],
    'Muted': [
        '#A8B3B8', '#C7CDD1', '#E1E6EA', '#B5C0C7', '#9AA5AC', '#D4D9DE',
        '#8995A1', '#7A8187', '#6B7278', '#BCC5CC', '#D8DEE3', '#F2F4F6',
        '#E7EAED', '#C3CDD6', '#A1ABB5', '#7F8A96', '#5D6872', '#9BAEC0'
    ],
    'Pastel': [
        '#FFD1DC', '#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF',
        '#C7CEEA', '#E2CBFF', '#FFC9DE', '#B5EAD7', '#FFE4E1', '#F0E68C',
        '#DDA0DD', '#98FB98', '#87CEEB', '#F5DEB3', '#FFA07A', '#20B2AA'
    ],
    'Sunset': [
        '#FF6B6B', '#FF8E53', '#FFD93D', '#FF9F43', '#EE5A6F', '#F06292',
        '#BA68C8', '#9575CD', '#7986CB', '#5C6BC0', '#42A5F5', '#29B6F6',
        '#26C6DA', '#26A69A', '#66BB6A', '#9CCC65', '#D4E157', '#FFEE58'
    ],
    'Ocean': [
        '#006994', '#0085C3', '#00A8CC', '#00B4D8', '#0096C7', '#0077B6',
        '#023E8A', '#03045E', '#90E0EF', '#CAF0F8', '#ADE8F4', '#48CAE4',
        '#00B4D8', '#0096C7', '#0077B6', '#023E8A', '#03045E', '#001D3D'
    ],
    'Forest': [
        '#386641', '#6A994E', '#A7C957', '#F2E8CF', '#BC4749', '#2D5016',
        '#52796F', '#84A98C', '#CAD2C5', '#354F52', '#2F3E46', '#588157',
        '#3A5A40', '#A3B18A', '#DAD7CD', '#A3B18A', '#588157', '#3A5A40'
    ],
    'Cosmic': [
        '#240046', '#3C096C', '#5A189A', '#7B2CBF', '#9D4EDD', '#C77DFF',
        '#E0AAFF', '#10002B', '#240046', '#3C096C', '#5A189A', '#7B2CBF',
        '#9D4EDD', '#C77DFF', '#E0AAFF', '#F72585', '#B5179E', '#7209B7'
    ]
}

# --- Popular Design Gradient Presets ---
# These are specific, well-known gradient combinations.
GRADIENT_PRESETS = {
    'Sunset': ['#FF512F', '#DD2476'],
    'Ocean': ['#2196F3', '#21CBF3'],
    'Forest': ['#11998e', '#38ef7d'],
    'Aurora': ['#00d2ff', '#3a7bd5'],
    'Fire': ['#f12711', '#f5af19'],
    'Purple Dream': ['#667eea', '#764ba2'],
    'Pink Sunset': ['#fa709a', '#fee140'],
    'Blue Steel': ['#2980B9', '#6BB6FF'],
    'Mint': ['#00b09b', '#96c93d'],
    'Cotton Candy': ['#ffecd2', '#fcb69f'],
    'Space': ['#8360c3', '#2ebf91'],
    'Lemon': ['#ffeaa7', '#fab1a0'],
    'Instagram': ['#833ab4', '#fd1d1d', '#fcb045'],
    'Spotify': ['#1DB954', '#1ed760'],
    'YouTube': ['#c4302b', '#ff5722'],
    'Twitter': ['#1DA1F2', '#1877f2'],
    'Netflix': ['#E50914', '#f40612'],
    'Slack': ['#4A154B', '#36C5F0'],
}

# --- Color Definitions ---
# These define the primary colors used across the application's UI.
PRIMARY_BG = '#ffffff'  # Main background color
SECONDARY_BG = '#b5baff' # Secondary background, often for elements like tab headers or status bar
PALETTE_INDIGO = '#7B7EC5'  # A specific indigo color, used for text in some contexts
ACCENT_BLUE = '#cccfff' # Accent color, often for active states or important buttons
TEXT_LIGHT = '#000000'  # Light text color (black for white backgrounds)
TEXT_MUTED = '#000000'  # Muted text color (lighter black for less emphasis)
INPUT_BG = '#FFFFFF'    # Background color for input fields
INPUT_FG = '#000000'    # Foreground (text) color for input fields
WARNING_RED = '#b5baff' # Color for warning messages or destructive actions
SUCCESS_GREEN = '#b5baff' # Color for success messages

# --- Hover Colors ---
# These define the colors used when a mouse hovers over interactive elements.
HOVER_PRIMARY_BG = '#FFDAAC'      # Hover color for primary background elements
HOVER_ACCENT_BLUE = '#FFDAAC'     # Hover color for accent blue elements
HOVER_WARNING_RED = '#FFDAAC'     # Hover color for warning red elements

# --- Status Message Duration ---
# Duration in milliseconds for temporary status messages to be displayed.
STATUS_MESSAGE_DURATION_MS = 2500

# --- Font Definitions ---
# Centralized font family and various sizes/styles for consistent typography.
FONT_FAMILY = "Montserrat"
FONT_REGULAR = (FONT_FAMILY, 11)
FONT_BOLD = (FONT_FAMILY, 11, "bold")
FONT_TITLE = (FONT_FAMILY, 26, "bold")
FONT_INPUT = (FONT_FAMILY, 12)
FONT_STATS_COUNT = (FONT_FAMILY, 24, "bold")
FONT_STATS_TEXT = (FONT_FAMILY, 11)

# --- Unit Conversion Factors ---
# Dictionaries mapping unit names to their conversion factors relative to a base unit (e.g., meter for length).
LENGTH_CONVERSION_FACTORS = {
    'mm': 0.001, 'cm': 0.01, 'm': 1.0, 'km': 1000.0,
    'inch': 0.0254, 'ft': 0.3048, 'yd': 0.9144, 'mile': 1609.34
}
MASS_CONVERSION_FACTORS = {
    'mg': 0.001, 'g': 1.0, 'kg': 1000.0, 'oz': 28.3495, 'lb': 453.592
}
VOLUME_CONVERSION_FACTORS = {
    'ml': 0.001, 'L': 1.0, 'fl oz': 0.0295735, 'cup': 0.236588, 'gallon': 3.78541
}

# --- Unit Categories ---
# A dictionary grouping units by their type, with sorted lists for display.
UNITS_CATEGORIES = {
    "Length": sorted(list(LENGTH_CONVERSION_FACTORS.keys())),
    "Mass": sorted(list(MASS_CONVERSION_FACTORS.keys())),
    "Volume": sorted(list(VOLUME_CONVERSION_FACTORS.keys())),
    "Temperature": ['°C', '°F'] # Temperature is handled separately due to non-linear conversion
}

