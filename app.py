from flask import Flask, request, redirect, send_from_directory, abort, render_template_string, url_for
import mysql.connector
from datetime import datetime
import os
from pathlib import Path
from urllib.parse import quote
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None
    print("Warning: Supabase credentials not configured. Please set SUPABASE_URL and SUPABASE_KEY in .env file")

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="rohitproject"
    )

def init_db():
    """Initialize database and tables"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255),
            login_time DATETIME
        )
        """)
        
        db.commit()
        db.close()
    except Exception as e:
        print(f"Database initialization error: {e}")


# Initialize database on startup
init_db()

LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Multi Wellness System - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; }
        .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); width: 100%; max-width: 400px; }
        h1 { color: #333; margin-bottom: 30px; text-align: center; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #555; font-weight: bold; }
        input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
        input:focus { outline: none; border-color: #667eea; box-shadow: 0 0 5px rgba(102, 126, 234, 0.5); }
        button { width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; font-weight: bold; }
        button:hover { background: #764ba2; }
        .tabs { display: flex; margin-bottom: 30px; border-bottom: 2px solid #eee; }
        .tab-btn { flex: 1; padding: 12px; background: none; border: none; cursor: pointer; font-size: 16px; color: #999; border-bottom: 3px solid transparent; }
        .tab-btn.active { color: #667eea; border-bottom-color: #667eea; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .error-box { background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 12px; border-radius: 5px; margin-bottom: 20px; font-size: 14px; }
        .success-box { background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 12px; border-radius: 5px; margin-bottom: 20px; font-size: 14px; }
        .error { color: #e74c3c; font-size: 14px; margin-top: 5px; }
        .success { color: #27ae60; font-size: 14px; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Multi Wellness System</h1>
        
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('login')">Login</button>
            <button class="tab-btn" onclick="switchTab('register')">Register</button>
        </div>
        
        <div id="login" class="tab-content active">
            <div id="login-message"></div>
            <form method="POST" action="/login">
                <div class="form-group">
                    <label for="login-email">Email:</label>
                    <input type="email" id="login-email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="login-password">Password:</label>
                    <input type="password" id="login-password" name="password" required>
                </div>
                <button type="submit">Login</button>
            </form>
        </div>
        
        <div id="register" class="tab-content">
            <div id="register-message"></div>
            <form method="POST" action="/register">
                <div class="form-group">
                    <label for="register-email">Email:</label>
                    <input type="email" id="register-email" name="email" required>
                </div>
                <div class="form-group">
                    <label for="register-password">Password:</label>
                    <input type="password" id="register-password" name="password" required>
                </div>
                <div class="form-group">
                    <label for="register-confirm">Confirm Password:</label>
                    <input type="password" id="register-confirm" name="confirm_password" required>
                </div>
                <button type="submit">Register</button>
            </form>
        </div>
    </div>
    
    <script>
        function switchTab(tab) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tab).classList.add('active');
            event.target.classList.add('active');
        }
        
        function showMessage(type, message) {
            const elem = document.getElementById(type + '-message');
            if (elem && message) {
                // Decode URL-encoded message
                const decodedMessage = decodeURIComponent(message);
                const isError = decodedMessage.toLowerCase().includes('error') || decodedMessage.toLowerCase().includes('invalid') || decodedMessage.toLowerCase().includes('not') || decodedMessage.toLowerCase().includes('already');
                const className = isError ? 'error-box' : 'success-box';
                elem.innerHTML = '<div class="' + className + '">' + decodedMessage + '</div>';
                console.log('Message shown:', decodedMessage);
            }
        }
        
        // Check URL for error/success messages on page load
        window.addEventListener('load', function() {
            const params = new URLSearchParams(window.location.search);
            console.log('URL params:', window.location.search);
            if (params.has('login_error')) {
                const errorMsg = params.get('login_error');
                console.log('Login error found:', errorMsg);
                switchTab('login');
                setTimeout(() => showMessage('login', errorMsg), 100);
            }
            if (params.has('register_error')) {
                const errorMsg = params.get('register_error');
                console.log('Register error found:', errorMsg);
                switchTab('register');
                setTimeout(() => showMessage('register', errorMsg), 100);
            }
            if (params.has('register_success')) {
                const successMsg = params.get('register_success');
                console.log('Register success found:', successMsg);
                switchTab('login');
                setTimeout(() => showMessage('login', successMsg), 100);
            }
        });
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    """Serve login page"""
    return render_template_string(LOGIN_PAGE)


@app.route("/register", methods=["POST"])
def register():
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    
    if not email or not password or not confirm_password:
        return redirect("/?register_error=" + quote("All fields are required"))
    
    if password != confirm_password:
        return redirect("/?register_error=" + quote("Passwords do not match"))
    
    try:
        if supabase:
            # Use Supabase for registration
            try:
                # Check if email already exists
                response = supabase.table("registration").select("*").eq("email", email).execute()
                if response.data:
                    return redirect("/?register_error=Email already exists. Please login.")
                
                # Insert new registration
                data = {
                    "email": email,
                    "password": password,
                    "created_at": datetime.now().isoformat()
                }
                supabase.table("registration").insert(data).execute()
                return redirect("/success?msg=registered")
            except Exception as err:
                return redirect("/?register_error=" + quote(f"Registration error: {str(err)}"))
        else:
            # Fallback to MySQL if Supabase not configured
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute(
                "INSERT INTO users (email, password) VALUES (%s, %s)",
                (email, password)
            )
            
            db.commit()
            db.close()
            
            return redirect("/success?msg=registered")
    except mysql.connector.Error as err:
        if err.errno == 1062:  # Duplicate entry
            return redirect("/?register_error=Email already exists. Please login.")
        return redirect("/?register_error=" + quote(f"Registration error: {str(err)}"))


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    
    if not email or not password:
        return "Email and password required", 400
    
    try:
        if supabase:
            # Use Supabase for login verification
            try:
                response = supabase.table("registration").select("*").eq("email", email).eq("password", password).execute()
                user = response.data
                
                if not user:
                    return redirect("/?login_error=" + quote("Invalid email or password"))
                
                # Log the login
                log_data = {
                    "email": email,
                    "login_time": datetime.now().isoformat()
                }
                supabase.table("login_logs").insert(log_data).execute()
                
                return redirect("/home2.html")
            except Exception as err:
                return f"Login error: {str(err)}", 500
        else:
            # Fallback to MySQL if Supabase not configured
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute("SELECT id FROM users WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone()
            
            if not user:
                db.close()
                return redirect("/?login_error=" + quote("Invalid email or password"))
            
            # Log the login
            cursor.execute(
                "INSERT INTO login_logs (email, login_time) VALUES (%s, %s)",
                (email, datetime.now())
            )
            
            db.commit()
            db.close()
            
            return redirect("/home2.html")
    except mysql.connector.Error as err:
        return f"Login error: {err}", 500


@app.route("/success")
def success():
    msg = request.args.get("msg", "")
    if msg == "registered":
        return "Registration Successful! You can now login."
    return "Login Data Stored Successfully"


@app.route('/<path:filename>')
def serve_file(filename):
    # Basic sanitization to avoid path traversal
    safe_path = Path(filename)
    if safe_path.is_absolute() or '..' in safe_path.parts:
        abort(400)

    target = BASE_DIR / filename
    if target.exists() and target.is_file():
        return send_from_directory(str(BASE_DIR), filename)

    abort(404)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)