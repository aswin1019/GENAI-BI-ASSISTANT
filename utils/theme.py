def load_light_theme():
    return """
    <style>
    body { background: linear-gradient(to right, #f7f9fc, #eef3f7); }
    .main { background: transparent; }
    .stApp { background-color: #f5f7fa; }
    .card {
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08); margin: 20px 0;
    }
    .scroll-box {
        max-height: 200px; overflow-y: auto; padding: 10px;
        border: 1px solid #ddd; border-radius: 8px;
        background-color: #fafafa;
    }
    .chat-bubble { padding: 12px 16px; border-radius: 16px;
        margin: 10px 0; max-width: 75%; font-size: 15px; line-height: 1.4; }
    .user-bubble { background: #00796b; color: white;
        margin-left: auto; text-align: right; }
    .ai-bubble { background: #f1f3f4; color: #222;
        margin-right: auto; text-align: left; }
    </style>
    """

def load_dark_theme():
    return """
    <style>
    body { background: #121212; color: #e0e0e0; }
    .main { background: transparent; }
    .stApp { background-color: #181818; }
    .card {
        background: #1f1f1f; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5); margin: 20px 0; color: #eee;
    }
    .scroll-box {
        max-height: 200px; overflow-y: auto; padding: 10px;
        border: 1px solid #444; border-radius: 8px;
        background-color: #2a2a2a; color: #f5f5f5;
    }
    h1, h2, h3, h4, h5, h6, label, p, span {
        color: #f5f5f5 !important;
    }
    .chat-bubble { padding: 12px 16px; border-radius: 16px;
        margin: 10px 0; max-width: 75%; font-size: 15px; line-height: 1.4; }
    .user-bubble { background: #00bfa5; color: white;
        margin-left: auto; text-align: right; }
    .ai-bubble { background: #333333; color: #f1f1f1;
        margin-right: auto; text-align: left; }
    </style>
    """
