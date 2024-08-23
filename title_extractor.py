from flask import Flask, jsonify, request, render_template, abort, redirect, url_for, session
import os
import yaml
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for session management

UPLOAD_FOLDER = '/app/data'  # Directory to save uploaded files
ALLOWED_EXTENSIONS = {'yaml', 'json', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Helper function to check file extension
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Helper function to handle file upload
def handle_file_upload(file):
    if file and allowed_file(file.filename):
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return file_path
    return None


# Function to load YAML data
def load_yaml_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            return data
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except yaml.YAMLError as exc:
        print(f"Error while parsing YAML file: {exc}")
        return None


# Function to extract titles from YAML and format them as "title1", "title2"
def extract_titles(yaml_data):
    if yaml_data is None:
        return ""

    titles = []
    for entry in yaml_data:
        title = entry.get('title', 'No title found')
        titles.append(f'"{title}"')
    return ', '.join(titles)


# Function to extract game titles from a JSON-like file
def extract_game_titles(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Extract titles from each game and enclose each in double quotes
        titles = [f'"{game.get("title")}"' for game in data if 'title' in game]

        # Join the titles with ", " separator
        title_string = ', '.join(titles)

        return title_string
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except json.JSONDecodeError as exc:
        print(f"Error while parsing JSON file: {exc}")
        return None


# Function to read text file content
def read_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    file_path = handle_file_upload(file)

    if not file_path:
        return render_template('upload_success.html', message="File type not allowed or no file uploaded!")

    # Store the file path in session for later use
    session['file_path'] = file_path

    return render_template('upload_success.html', message=f"File '{file.filename}' has been uploaded successfully.")


@app.route('/extract', methods=['POST'])
def extract():
    extraction_type = request.form.get('extraction_type')

    # Use the session file path
    file_path = session.get('file_path')

    if not file_path or not os.path.isfile(file_path):
        return render_template('result.html', content="No valid file path provided or file does not exist.")

    if extraction_type == "titles" and file_path.endswith('.yaml'):
        yaml_data = load_yaml_file(file_path)
        result_content = extract_titles(yaml_data)
    elif extraction_type == "game_titles" and file_path.endswith('.json'):
        result_content = extract_game_titles(file_path)
    elif extraction_type == "text_content" and file_path.endswith('.txt'):
        result_content = read_text_file(file_path)
    else:
        return jsonify({'error': 'Invalid extraction type or file type mismatch!'}), 400

    return render_template('result.html', content=result_content)


if __name__ == '__main__':
    app.run(debug=True, port=8001, host='0.0.0.0')