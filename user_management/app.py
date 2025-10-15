from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
import json
import os
import hashlib
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-2024'
app.config['UPLOAD_FOLDER'] = 'static/uploads/avatars'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max file size

# Đảm bảo thư mục upload tồn tại
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    try:
        with open('data/users.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Tạo admin account mặc định
        default_users = {
            "QuangNguyen": {
                "password": hash_password("MinhQu@ng2010"),
                "email": "admin@system.com",
                "avatar": "default.png",
                "role": "admin",
                "created_at": "2024-01-01 00:00:00"
            }
        }
        save_users(default_users)
        return default_users

def save_users(users):
    with open('data/users.json', 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Vui lòng đăng nhập để truy cập trang này!', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Vui lòng đăng nhập!', 'warning')
            return redirect(url_for('login'))
        
        users = load_users()
        if users.get(session['username'], {}).get('role') != 'admin':
            flash('Bạn không có quyền truy cập trang này!', 'error')
            return redirect(url_for('profile'))
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('profile'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form.get('email', '').strip()
        
        users = load_users()
        
        # Validation
        if not username or not password:
            flash('Vui lòng nhập đầy đủ thông tin!', 'error')
            return render_template('register.html')
        
        if username in users:
            flash('Tên đăng nhập đã tồn tại!', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Mật khẩu phải có ít nhất 6 ký tự!', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Mật khẩu xác nhận không khớp!', 'error')
            return render_template('register.html')
        
        # Tạo user mới
        users[username] = {
            "password": hash_password(password),
            "email": email,
            "avatar": "default.png",
            "role": "user",
            "created_at": "2024-01-01 00:00:00"  # Trong thực tế nên dùng datetime
        }
        
        save_users(users)
        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        users = load_users()
        
        if username in users and users[username]['password'] == hash_password(password):
            session['username'] = username
            session['role'] = users[username].get('role', 'user')
            flash(f'Đăng nhập thành công! Chào mừng {username}', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'error')
    
    return render_template('login.html')

@app.route('/profile')
@login_required
def profile():
    users = load_users()
    user_data = users.get(session['username'], {})
    return render_template('profile.html', user=user_data)

@app.route('/change_avatar', methods=['GET', 'POST'])
@login_required
def change_avatar():
    if request.method == 'POST':
        if 'avatar' not in request.files:
            flash('Vui lòng chọn file ảnh!', 'error')
            return redirect(url_for('change_avatar'))
        
        file = request.files['avatar']
        
        if file.filename == '':
            flash('Vui lòng chọn file ảnh!', 'error')
            return redirect(url_for('change_avatar'))
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Đổi tên file để tránh trùng lặp
            extension = filename.rsplit('.', 1)[1].lower()
            new_filename = f"{session['username']}_avatar.{extension}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            
            file.save(filepath)
            
            # Cập nhật database
            users = load_users()
            users[session['username']]['avatar'] = new_filename
            save_users(users)
            
            flash('Cập nhật avatar thành công!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('File không hợp lệ! Chỉ chấp nhận file ảnh (PNG, JPG, JPEG, GIF)', 'error')
    
    return render_template('change_avatar.html')

@app.route('/admin')
@admin_required
def admin_dashboard():
    users = load_users()
    return render_template('admin.html', users=users)

@app.route('/logout')
def logout():
    session.clear()
    flash('Đã đăng xuất thành công!', 'info')
    return redirect(url_for('index'))

@app.route('/uploads/avatars/<filename>')
def uploaded_avatar(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)