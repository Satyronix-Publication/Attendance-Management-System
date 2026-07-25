
# config.py
# Attendance Management System - CBSE Class 12 Project
# Centralized Configuration (Email + Theme)

# -------------------------------------------------------
# EMAIL CONFIGURATION
# To enable email notifications:
#  1. Go to your Google Account -> Security -> 2-Step Verification (enable it)
#  2. Go to Google Account -> Security -> App Passwords
#  3. Generate an App Password for "Mail"
#  4. Paste the 16-character App Password below (remove spaces)
# -------------------------------------------------------
EMAIL_SENDER = "your_email@gmail.com"       # <-- Replace with your Gmail
EMAIL_APP_PASSWORD = "your_app_password"    # <-- Replace with your 16-char App Password
EMAIL_ENABLED = False  # Set to True once you configure credentials above

# -------------------------------------------------------
# THEME COLORS
# Two themes: "dark" (default) and "light"
# -------------------------------------------------------

THEMES = {
    "dark": {
        "bg":          "#0f0a1e",
        "sidebar_bg":  "#1e1040",
        "card_bg":     "#2d1b60",
        "accent":      "#8b5cf6",
        "fg":          "white",
        "fg_dim":      "#a8a8b3",
        "success":     "#155724",
        "danger":      "#7b1c1c",
        "warning":     "#856404",
        "info":        "#1e3a5f",
        "row_even":    "#1e1040",
        "row_odd":     "#1a1f3c",
        "entry_bg":    "#2d1b60",
        "tree_bg":     "#1e1040",
        "tree_head":   "#2d1b60",
        "top_bar":     "#8b5cf6",
        "name":        "Dark Mode",
    },
    "light": {
        "bg":          "#f0f2f5",
        "sidebar_bg":  "#ffffff",
        "card_bg":     "#e8e0ff",
        "accent":      "#7c3aed",
        "fg":          "#1a1a2e",
        "fg_dim":      "#555577",
        "success":     "#d4edda",
        "danger":      "#f8d7da",
        "warning":     "#fff3cd",
        "info":        "#cce5ff",
        "row_even":    "#ffffff",
        "row_odd":     "#f3f0ff",
        "entry_bg":    "#e8e0ff",
        "tree_bg":     "#ffffff",
        "tree_head":   "#7c3aed",
        "top_bar":     "#7c3aed",
        "name":        "Light Mode",
    }
}

# Current active theme (toggled at runtime)
current_theme = "dark"


def get_theme():
    """Returns the current theme dict."""
    return THEMES[current_theme]


def toggle_theme():
    """Switches between dark and light themes."""
    global current_theme
    current_theme = "light" if current_theme == "dark" else "dark"
    return THEMES[current_theme]
