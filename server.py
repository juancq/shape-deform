import sys
import random
import sqlite3
import os
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from genetic_algorithm import Container
from werkzeug.utils import secure_filename


#--------------------------------------#
app = Flask(__name__, static_url_path='')
ga = Container()

UPLOAD_FOLDER = 'data'
ALLOWED_EXTENSIONS = set(['json'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#--------------------------------------#
@app.route('/', methods=["GET", "POST"])
def index():

    selectModel = getRow("models")

    if request.method == "POST":
        selection = request.form.get('selection')
        filename = "/data/" + selection

        return render_template("index.html", selectModel=selectModel, filename=filename)

    else:

        return render_template('index.html', selectModel=selectModel)

@app.route('/single_model', methods=['GET', 'POST'])
def single():

    selectModel = getRow("models")

    if request.method == 'POST':
        selection = request.form.get('selection')
        filename = "/data/" + selection

        return render_template("single_model.html", selectModel=selectModel, filename=filename)

    else:

        return render_template("single_model.html", selectModel=selectModel)

@app.route('/view_single', methods=["POST"])
def viewSingle():
    
    if request.method == "POST":
        
        shader = request.form['shader']
        print(shader)
        return render_template("single_model.html", shader=shader)
    
    else:
        
        return render_template("single_model.html")

#--------------------------------------#
@app.route('/_start')
def start():

    size = request.args.get('size', 0, type=int)

    # start ga
    ga.on_start(popsize = 100, subset_size = size)

    subset = ga.get_subset()
    return jsonify(result=subset)

#--------------------------------------#
@app.route('/_step')
def step():
    selection = request.args.get('sel', 0, type=int)
    ga.iga_step(selection)
    subset = ga.get_subset()
    return jsonify(result=subset)

#--------------------------------------#
@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

#--------------------------------------#
@app.route('/data/<path:path>')
def send_data(path):
    return send_from_directory('data', path)

#--------------------------------------#
@app.route('/recordEquation')
def recordEquation():

    equation = request.args.get('equation')

    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("INSERT INTO equations (equation) values (?)", [equation])
        print("Equation saved: " + equation)

    con.commit()
    con.close()

    return equation


@app.route('/sendRandomEquation')
def returnRandomEQ():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM equations")

    equations = []

    for row in c.fetchall():
        equations.append(row[1])

    equation = equations[random.randrange(0, len(equations))]

    return jsonify(result=equation)

#--------------------------------------#
@app.route('/checkINT')
def checkINT():
#check for integers, convert into float if true

    data = str(request.args.get('data', 0))
    convertedData = ""

    if data != 0:

        i = 0

        while i <= len(data)-1:
            try:
                float(data[i])
                convertedINT, i = convertINT(data, i)
                convertedData += convertedINT


            except ValueError:
                convertedData += data[i]
                i += 1

    return jsonify(convertedData)


def convertINT(data, start):
#checks if int number has more than one digit

    i = start

    while True:

        try:
            i += 1
            print(i)
            float(data[i])

        except (ValueError, IndexError):
            end = i
            break;

    return [str(float(data[start:end])), end]


#--------------------------------------#
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def uploadModel(file):

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("INSERT INTO MODELS (modelName) VALUES (?)", [filename])
        print("Model saved: " + filename)

    con.commit()
    con.close()
                
    file.save(filepath)
    filename = "/data/" + filename
    return filename


@app.route('/uploadSingle', methods=['GET', 'POST'])
def uploadSingle():
    if request.method == 'POST':
        
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file and allowed_file(file.filename):

            filename = uploadModel(file)
            
            return render_template("single_model.html", filename=filename)
        
    return render_template("single_model.html")

            
@app.route('/uploadMulti', methods=['GET', 'POST'])
def uploadMulti():
    
    if request.method == 'POST':
        
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file and allowed_file(file.filename):

            filename = uploadModel(file)
            
            return render_template("index.html", filename=filename)
        
    return render_template("index.html")


#--------------------------------------#
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

#--------------------------------------#
def getRow(table):

    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("select * from " + table)

    rows = cur.fetchall();

    return rows

#--------------------------------------#
def main():
    app.run(
        host='0.0.0.0',
        port=int('8000'),
        debug=True
    )

if __name__ == '__main__':
    main()
