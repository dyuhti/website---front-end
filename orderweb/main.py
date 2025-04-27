from flask import Flask, request, redirect, session, Response
import os
import json

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# User storage
USER_FILE = "users.json"


def load_users():
    """Load users from file or create new file"""
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, 'w') as f:
            json.dump({"admin@example.com": {"password": "admin123", "name": "Admin"}}, f)
        return {"admin@example.com": {"password": "admin123", "name": "Admin"}}
    with open(USER_FILE, 'r') as f:
        return json.load(f)


def save_users(users):
    """Save users to file"""
    with open(USER_FILE, 'w') as f:
        json.dump(users, f, indent=4)


def get_html(file_path, replacements=None):
    """Read HTML file and apply replacements"""
    with open(file_path, 'r') as f:
        content = f.read()
        if replacements:
            for key, value in replacements.items():
                content = content.replace(key, value)
        return content


# Routes must be defined BEFORE first request
@app.route('/')
def home():
    return get_html('cover.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        email = request.form.get('email')
        password = request.form.get('password')

        if email in users and users[email]['password'] == password:
            session['user'] = email
            return redirect('/main')

        return get_html('login.html', {'<!-- ERROR -->': '<div class="error">Invalid credentials</div>'})
    return get_html('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        users = load_users()
        email = request.form.get('email')

        if email in users:
            return get_html('signup.html', {'<!-- ERROR -->': '<div class="error">Email exists</div>'})

        users[email] = {
            'name': request.form.get('name'),
            'password': request.form.get('password')
        }
        save_users(users)
        return redirect('/')
    return get_html('signup.html')


@app.route('/main')
def main():
    if 'user' not in session:
        return redirect('/')
    return get_html('mainpg.html', {'{{ user_email }}': session['user']})


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


if __name__ == '__main__':
    # Verify required files exist
    required_files = ['login.html', 'signup.html', 'mainpg.html']
    for file in required_files:
        if not os.path.exists(file):
            raise FileNotFoundError(f"Missing required file: {file}")

    app.run(debug=True)