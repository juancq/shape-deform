import sys
import random
import sqlite3
import os
from treelib import Tree
from genetic_algorithm import Container
from newGA import newGA
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect

#--------------------------------------#
app = Flask(__name__, static_url_path='')
ga = Container()
na = newGA()

UPLOAD_FOLDER = 'data'
ALLOWED_EXTENSIONS = set(['json'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#--------------------------------------#
@app.route('/', methods=["GET", "POST"])
def index():

    selectModel = getRow("models")

    if request.method == "POST":
        selection = request.form.get('selection')

        if selection == "none":
            return redirect(request.url)

        filename = "/data/" + selection

        return render_template("index.html", selectModel=selectModel, filename=filename)

    else:

        return render_template('index.html', selectModel=selectModel)

@app.route('/experiment_page')
def experimental():

    return render_template('experiment_page.html')

@app.route('/single_model', methods=['GET', 'POST'])
def single():

    selectModel = getRow("models")
    selectEquation = getRow("equations")

    if request.method == 'POST' and request.form.get('selection'):
        selection = request.form.get('selection')

        if selection == "none":
            return redirect(request.url)

        filename = "/data/" + str(selection)

        return render_template("single_model.html", selectModel=selectModel, filename=filename)

    elif request.method == 'POST'and (request.form.get('select_equation') or request.form['shader']):

        if(request.form.get('select_equation')):
            shader = request.form.get('select_equation')
        elif(request.form['shader']):
            shader = request.form['shader']

        if shader == "none":
            return redirect(request.url)

        return render_template("single_model.html", selectEquation = selectEquation, shader = shader, selectModel=selectModel)

    else:

        return render_template("single_model.html", selectModel=selectModel, selectEquation=selectEquation)

#for experimental_page, to record positive/negative
@app.route('/positive')
def positive():

    equation = request.args.get('equation')

    file = open('positive.txt', 'a')
    file.write(equation+"\n")

    return jsonify(data="Success: Positive Recorded")

@app.route('/negative')
def negative():

    equation = request.args.get('equation')

    file = open('negative.txt', 'a')
    file.write(equation+"\n")

    return jsonify(data="Success: Negative Recorded")

@app.route('/treeEQ')
def treeEQ():

    equation = generateEquation(generateTree())

    return jsonify(result=equation)

@app.route('/startNA')
def startNA():

    size = request.args.get('size', type=int)
    na.start(size)

    subset = na.get_expressions()

    return jsonify(result=subset)

@app.route('/naMutate')
def naMutate():

    selection = request.args.get('selection', type=int)
    size = request.args.get('size', type=int)

    na.mutate(selection)
    subset = na.get_expressions()

    return jsonify(result=subset)

@app.route('/randTreeEQ')
def randTreeEQ():

    equation = request.args.get('equation', 0)
    equation = similarTreeEquations(equation)

    return jsonify(result=equation)

@app.route('/about', methods=['GET'])
def about():

    return render_template('about.html')

#--------------------------------------#
@app.route('/_start')
def start():

   size = request.args.get('size', 0, type=int)

   #start ga
   ga.on_start(popsize = 50, subset_size = size)

   subset = ga.get_subset()

   # subset = []
   #
   # for i in range(0, 9):
   #     subset.append(generateEquation(generateTree()))

   return jsonify(result=subset)

#--------------------------------------#
@app.route('/_step')
def step():

    selection = request.args.get('sel', 0, type=int)
    ga.iga_step(selection)
    subset = ga.get_subset()

    # subset = []
    #
    # if selection == 0:
    #     #If model not altered or request was an error; revert all to default state
    #     for i in range(0, 9):
    #         subset.append("0.0")
    #
    # else:
    #     for i in range(0, 9):
    #         subset.append(similarTreeEquations(selection))

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
    #records the selected equation into the database

    equation = request.args.get('equation')

    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("INSERT INTO equations (equation) values (?)", [equation])
        print("Equation saved: " + equation)

    con.commit()
    con.close()

    return equation

@app.route('/saveEquation')
def saveEquation():
    #save input equation from equationTextField to database

        saveEquation = request.args.get('equation')

        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO equations (equation) values (?)", [saveEquation])
            print("Equation saved: " + str(saveEquation))

        con.commit()
        con.close()

        #save input equation to text file
        file = open("Equation Records.txt", "a")
        if (os.path.getsize("Equation Records.txt")>0): #check if text file is empty
            file.write("\n" + saveEquation) #if text file is not empty, add equation to new line
        else:
            file.write(saveEquation)
        file.close()

        return saveEquation

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
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def uploadModel(file):
    #uploads model into the database

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
    #upload funcion for single model page

    if request.method == 'POST':

        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)

        file = request.files['file']

        if file and allowed_file(file.filename):

            filename = uploadModel(file)
            alert = file.filename + " has been uploaded."
            selectModel = getRow("models")

            return render_template("single_model.html", filename=filename, selectModel=selectModel, alert=alert)


    return render_template("single_model.html")

@app.route('/uploadMulti', methods=['GET', 'POST'])
def uploadMulti():
    #upload function for multi model page


    if request.method == 'POST':

        if 'file' not in request.files:
            print("No file part")
            return redirect(request.url)

        file = request.files['file']

        if file and allowed_file(file.filename):

            filename = uploadModel(file)
            alert = file.filename + " has been uploaded."
            selectModel = getRow("models")

            return render_template("index.html", filename=filename, selectModel=selectModel, alert=alert)

    return render_template("index.html")

#--------------------------------------#
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

#--------------------------------------#
def getRow(table):
    #returns rows of saved models' names

    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("select * from " + table)

    rows = cur.fetchall();

    return rows

#--------------------------------------#
# Tree Equations

operators = ["+", "-", "/", "*"]
cOperators = ["sin", "cos", "tan"]

def randomOperator():

    operator = ["+", "-", "/", "*", "sin", "cos", "tan"]

    return random.choice(operator)

def randomVariable():

    variables = ["x", "y", "z", "time"]

    return random.choice(variables)

def randomValue():

    variables = ["x", "y", "z", "time"]

    if random.random() < 0.5:
        num = random.uniform(-1,1)
        if num == 0:
            return randomValue()
        return "(" + str(num) + ")"
    else:
        return random.choice(variables)

def randomAll():

    variables = ["x", "y", "z", "+", "-", "/", "*", "sin", "cos", "tan"]

    if random.random() < 0.5:
        num = random.uniform(-1,1)
        if num == 0:
            return randomAll()
        return "(" + str(num) + ")"
    else:
        return random.choice(variables)

def determineNoChildren(operator):

    #determine how many children the parent would have based on the operator

    if operator == "+" or operator == "-" or operator == "/" or operator == "*":
        return 2
    else:
        return 1

def equationInorder(tree, index):

    #generate string of equation from index's child, based on type of operators

    children = tree.is_branch(index)
    equation = "(" + str(tree[children[0]].tag) + tree[index].tag + str(tree[children[1]].tag) + ")"
    tree[index].tag = equation

    return tree

def trigonometricEquation(tree, index):

    child = tree.is_branch(index)
    equation = str(tree[index].tag) + "(" + str(tree[child[0]].tag) + ")"
    tree[index].tag = equation

    return tree

def generateTree():

    tree = Tree()
    parent = []
    opParent = 1
    operatorChild = 3

    tree.create_node(randomOperator(), 0)

    depth = determineNoChildren(tree[0].tag)

    for x in range(0, depth):

        if x == 0:
            tree.create_node(randomVariable(), opParent, parent=0)
            if tree[opParent].tag in operators or tree[opParent].tag in cOperators:
                parent.append(opParent)
            opParent += 1
        else:
            tree.create_node(randomAll(), opParent, parent=0)
            if tree[opParent].tag in operators or tree[opParent].tag in cOperators:
                parent.append(opParent)
            opParent+=1

    for node in parent:

        depth = determineNoChildren(tree[node].tag)

        for i in range(0, depth):

            if i == 0:
                tree.create_node(randomValue(), operatorChild, parent=node)
                operatorChild += 1

            else:
                tree.create_node(randomValue(), operatorChild, parent=node)
                operatorChild+=1

    return tree

def generateEquation(tree):

    if tree[0].tag in cOperators:

        if tree[1].tag in cOperators:
            tree = trigonometricEquation(tree, 1)
            tree = trigonometricEquation(tree, 0)

        elif tree[1].tag in operators:
            tree = equationInorder(tree, 1)
            tree = trigonometricEquation(tree, 0)

        else:
            tree[0].tag = tree[0].tag + "(" + str(tree[1].tag) + ")"

    else:

        children = tree.is_branch(0)

        for child in children:

            if tree[children[child-1]].tag in cOperators:
                tree = trigonometricEquation(tree, child)

            elif tree[children[child-1]].tag in operators:
                tree = equationInorder(tree, child)

        tree = equationInorder(tree, 0)

    return tree[0].tag


def similarTreeEquations(equation):

    if random.random() < 0.5:

        equation += random.choice(operators) + randomVariable()

    elif random.random() < 0.5:

        equation += random.choice(operators) + random.choice(cOperators) + "(" + randomVariable() + ")"

        if random.random() < 0.5:
            equation += random.choice(operators) + randomVariable()

    else:

        newVariable = randomVariable()

        for variable in ['x', 'y', 'z']:
            equation = equation.replace(variable, newVariable)

    return equation


#--------------------------------------#
def main():
    app.run(
        host='0.0.0.0',
        port=int('8000'),
        debug=True
    )

if __name__ == '__main__':
    main()
