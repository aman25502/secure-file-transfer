from flask import Flask, request, redirect, url_for, flash, render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
import os
from cryptography.fernet import Fernet
from flask_mail import Mail, Message
import logging

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate secret key
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Set these as GitHub secrets
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

# User authentication setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['username']
        login_user(User(user_id))
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Encrypt the file
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        with open(file_path, 'rb') as f:
            encrypted_file = cipher_suite.encrypt(f.read())
        encrypted_file_path = file_path + '.enc'
        with open(encrypted_file_path, 'wb') as f:
            f.write(encrypted_file)

        # Send email
        send_email(request.form['receiver_email'], encrypted_file_path, key.decode())
        flash('File successfully uploaded and encrypted')
        return redirect(url_for('index'))
    flash('File type or size not allowed')
    return redirect(url_for('index'))

def allowed_file(filename):
    allowed_extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def send_email(receiver_email, file_path, key):
    msg = Message('Encrypted File', sender=app.config['MAIL_USERNAME'], recipients=[receiver_email])
    msg.body = f'Please find the encrypted file attached. The decryption key is: {key}'
    with app.open_resource(file_path) as fp:
        msg.attach(file_path, 'application/octet-stream', fp.read())
    mail.send(msg)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
