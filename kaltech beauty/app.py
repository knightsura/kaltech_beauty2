from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
import os
import random

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}
app.config['VOTES_FILE'] = 'votes.txt'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_images():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return [f for f in files if allowed_file(f)]

def get_votes():
    if not os.path.exists(app.config['VOTES_FILE']):
        return {}
    with open(app.config['VOTES_FILE'], 'r') as f:
        lines = f.readlines()
    votes = {}
    for line in lines:
        img, count = line.strip().split(',')
        votes[img] = int(count)
    return votes

def update_votes(img):
    votes = get_votes()
    if img in votes:
        votes[img] += 1
    else:
        votes[img] = 1
    with open(app.config['VOTES_FILE'], 'w') as f:
        for img, count in votes.items():
            f.write(f'{img},{count}\n')

@app.route('/')
def index():
    images = get_images()
    if len(images) < 2:
        return "Not enough images to compare."
    img1, img2 = random.sample(images, 2)
    top_images = sorted(get_votes().items(), key=lambda x: x[1], reverse=True)[:3]
    return render_template('index.html', img1=img1, img2=img2, top_images=top_images)

@app.route('/vote', methods=['POST'])
def vote():
    img = request.form['image']
    update_votes(img)
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('index'))
    return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)
