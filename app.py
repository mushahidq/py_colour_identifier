from flask import Flask, flash, request, redirect, url_for, send_from_directory, send_file, render_template
from werkzeug.utils import secure_filename
import os

from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np
import cv2
from collections import Counter
from skimage.color import rgb2lab, deltaE_cie76

#Identify Colours
def get_img(img_path):
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

def RGB2HEX(color):
    return "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))

def get_colours(img_path, no_of_colours, show_chart):
    img = get_img(img_path)
    #Reduce image size to reduce the execution time
    mod_img = cv2.resize(img, (600, 400), interpolation = cv2.INTER_AREA)
    #Reduce the input to two dimensions for KMeans
    mod_img = mod_img.reshape(mod_img.shape[0]*mod_img.shape[1], 3)

    #Define the clusters
    clf = KMeans(n_clusters = no_of_colours)
    labels = clf.fit_predict(mod_img)

    counts = Counter(labels)
    counts = dict(sorted(counts.items()))

    center_colours = clf.cluster_centers_
    ordered_colours = [center_colours[i] for i in counts.keys()]
    hex_colours = [RGB2HEX(ordered_colours[i]) for i in counts.keys()]
    rgb_colours = [ordered_colours[i] for i in counts.keys()]

    if (show_chart):
        plt.figure(figsize = (8, 6))
        plt.pie(counts.values(), labels = hex_colours, colors = hex_colours)
        pie = os.path.join(app.config['UPLOAD_FOLDER'], 'pie.png')
        plt.savefig(pie, transparent=True)
        os.remove(img_path)
        return
    else:
        return rgb_colours

        
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app =Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        n = request.form['n']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            try:
                os.mkdir('static/')
                os.mkdir('static/images/')
            except:
                #f = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                #f = open(f, "x")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('colours', filename = filename, n = n))
            #f = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            #f = open(f, "x")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('colours', filename = filename, n = n))
    else:
        if(os.path.isfile('static/images/pie.png')):
            os.remove('static/images/pie.png')
    return '''
        <!doctype html>
        <head>
            <title>Colour Identifier</title>
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
            <link rel="stylesheet" href="static/css/sticky-footer.css">
            <style>
                html, body {
                    height: 100%;
                }
                body {
                    display: -ms-flexbox;
                    display: flex;
                    -ms-flex-align: center;
                    align-items: center;
                    padding-top: 40px;
                    background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
                    background-size: 400% 400%;
                    animation: gradient 15s ease infinite;
                }
                @keyframes gradient {
                    0% {
                        background-position: 0% 50%;
                    }
                    50% {
                        background-position: 100% 50%;
                    }
                    100% {
                        background-position: 0% 50%;
                    }
                }
                .btn-outline-light{
                    color: #f8f9fa;
                    border-color: #f8f9fa;
                    background-color: transparent;
                }
                .btn-outline-light:hover {
                    color: #212529;
                    background-color: #f8f9fa;
                    border-color: #f8f9fa;
                }
            </style>
        </head>
        <body style="display:flex; align-items:center; height: 100%;">
            <div class="container align-middle">
                <h1 class="text-center align-middle">Identify Most Used<br>Colours In an Image</h1>
                <form method=post enctype=multipart/form-data>
                    <div class="form-group">
                        <label for="file">Select a file to find the colours in it.</label>
                        <input type="file" name="file" placeholder="">
                        <small id="emailHelp" style="color:#333;"class="form-text text-muted">The image will be destroyed after generating the ouput.</small>
                    </div>
                    <div class="form-group">
                        <label for="n">Enter the number of colours to find:</label>
                        <input type=text name=n class="form-control" id="n">
                    </div>
                    <button  class="btn btn-outline-light" type="submit">Upload</button>
                </form>
            </div>
            <footer class="footer">
                <div class="container text-center">
                    <span class="text-secondary">Made by Mohammed Mushahid Qureshi(<a href="https://github.com/mushahidq">Github</a>). <a href="https://github.com/mushahidq/py_colour_identifier">Code for this site.</a></span>
                </div>
            </footer>
            <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>
        </body>
    '''

@app.route('/colours/<filename>/<n>')
def colours(filename, n = 5):
    col = int(n)
    file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    get_colours(file, col, True)
    return render_template('pie.html', n=n)
