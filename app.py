from flask import Flask, request, render_template, send_file, jsonify
import uproot
import os
import matplotlib.pyplot as plt
import io
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Upload configuration
UPLOAD_FOLDER = './uploaded_files'
ALLOWED_EXTENSIONS = {'root'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'filename': filename})
    return 'File upload failed', 400

@app.route('/uploaded_files', methods=['GET'])
def uploaded_files():
    files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if allowed_file(f)]
    return jsonify(files)

@app.route('/explore/<filename>')
def explore(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file = uproot.open(filepath)
    tree = build_tree(file)
    return jsonify(tree)

@app.route('/plot/<filename>/<tree_name>/<branch>')
def plot(filename, tree_name, branch):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file = uproot.open(filepath)
    tree = file[tree_name]
    data = tree[branch].array(library="np")

    # Create plot
    fig, ax = plt.subplots()
    ax.hist(data, bins=30, alpha=0.7, color="skyblue")
    ax.set_title(f"Histogram of {branch}")
    ax.set_xlabel("Value")
    ax.set_ylabel("Frequency")

    # Save to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

def build_tree(directory, path=""):
    """
    Recursively builds a nested tree structure.
    """
    tree = {}
    for key, obj in directory.items():
        full_path = f"{path}/{key}"
        if isinstance(obj, uproot.behaviors.TTree.TTree):
            tree[key] = {'type': 'tree', 'branches': list(obj.keys())}
        elif isinstance(obj, uproot.reading.ReadOnlyDirectory):
            tree[key] = {'type': 'directory', 'content': build_tree(obj, path=full_path)}
    return tree

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
