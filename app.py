from flask import Flask, request, redirect, send_from_directory, abort, render_template_string, url_for
import mysql.connector
from datetime import datetime
import os
from pathlib import Path
from urllib.parse import quote
from dotenv import load_dotenv

# Load .env only if it exists (won't work on Render)
if os.path.exists('.env'):
    load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)

# Supabase configuration - try to import and use if credentials are available
supabase = None
try:
    from supabase import create_client, Client
    
    SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()
    
    if SUPABASE_URL and SUPABASE_KEY and "your-supabase-project" not in SUPABASE_URL:
        try:
            supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            print("✓ Supabase connected successfully")
        except Exception as e:
            print(f"✗ Supabase connection error: {str(e)}")
            supabase = None
            print("Falling back to MySQL for authentication")
    else:
        print("⚠ Supabase credentials not configured. Using MySQL for authentication.")
        supabase = None
except ImportError:
    print("⚠ Supabase package not installed. Using MySQL for authentication.")
    supabase = None

def get_db():
    """Get database connection using environment variables or fallback to localhost"""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "root"),
        database=os.getenv("DB_NAME", "rohitproject"),
        port=int(os.getenv("DB_PORT", "3306"))
    )

def init_db():
    """Initialize database and tables - non-blocking version"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255),
            email VARCHAR(255),
            login_time DATETIME
        )
        """)
        
        db.commit()
        db.close()
        print("✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"⚠ Database initialization deferred: {type(e).__name__}")
        print(f"  Tables will be created on first request")
        return False


# Initialize database on startup (non-blocking, don't crash if fails)
db_ready = False
try:
    db_ready = init_db()
except Exception as e:
    print(f"⚠ Database not ready on startup (will retry on first request)")


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
                    <label for="login-username">Username:</label>
                    <input type="text" id="login-username" name="username" required>
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
                    <label for="register-username">Username:</label>
                    <input type="text" id="register-username" name="username" required>
                </div>
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


@app.route("/health")
def health():
    """Health check endpoint"""
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        db.close()
        return {"status": "healthy", "database": "connected"}, 200
    except Exception as e:
        return {"status": "degraded", "database": "disconnected", "error": str(e)}, 503


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    
    if not username or not email or not password or not confirm_password:
        return redirect("/?register_error=" + quote("All fields are required"))
    
    if password != confirm_password:
        return redirect("/?register_error=" + quote("Passwords do not match"))
    
    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (username, email, password)
        )
        db.commit()
        db.close()
        db = None
        
        # Also save to Supabase if configured
        if supabase:
            try:
                data = {
                    "username": username,
                    "email": email,
                    "password": password,
                    "created_at": datetime.now().isoformat()
                }
                supabase.table("registration").insert(data).execute()
            except Exception as e:
                print(f"Supabase sync failed: {str(e)}")
        
        return redirect("/success?msg=registered")
        
    except mysql.connector.Error as err:
        if db:
            try:
                db.close()
            except:
                pass
        if err.errno == 1062:  # Duplicate entry
            return redirect("/?register_error=Username or Email already exists. Please login.")
        return redirect("/?register_error=" + quote(f"Database error: {str(err)}"))
    except Exception as err:
        if db:
            try:
                db.close()
            except:
                pass
        print(f"Registration error: {str(err)}")
        error_msg = "Database connection error. Please try again later."
        return redirect("/?register_error=" + quote(error_msg))



@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    
    if not username or not password:
        return "Username and password required", 400
    
    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("SELECT id, email FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        
        if not user:
            db.close()
            db = None
            return redirect("/?login_error=" + quote("Invalid username or password"))
        
        user_id, user_email = user
        
        # Log the login
        cursor.execute(
            "INSERT INTO login_logs (username, email, login_time) VALUES (%s, %s, %s)",
            (username, user_email, datetime.now())
        )
        
        db.commit()
        db.close()
        db = None
        
        # Also log to Supabase if configured
        if supabase:
            try:
                log_data = {
                    "username": username,
                    "email": user_email,
                    "login_time": datetime.now().isoformat()
                }
                supabase.table("login_logs").insert(log_data).execute()
            except Exception as e:
                print(f"Supabase login log failed: {str(e)}")
        
        return redirect("/home2.html")
        
    except mysql.connector.Error as err:
        if db:
            try:
                db.close()
            except:
                pass
        print(f"Login error: {str(err)}")
        error_msg = "Database connection error. Please try again later."
        return redirect("/?login_error=" + quote(error_msg))
    except Exception as err:
        if db:
            try:
                db.close()
            except:
                pass
        print(f"Login error: {str(err)}")
        return redirect("/?login_error=" + quote("An error occurred. Please try again."))



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