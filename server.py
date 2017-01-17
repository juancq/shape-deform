import sys
import random
import sqlite3
from flask import Flask, render_template, request, jsonify, send_from_directory
from genetic_algorithm import Container



#--------------------------------------#
app = Flask(__name__, static_url_path='')
ga = Container()


#--------------------------------------#
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/single_model', methods=['GET', 'POST'])
def single():
    if request.method == 'POST':
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
    print(equation)

    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("INSERT INTO equations (equation) values (?)", [equation])

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
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

#--------------------------------------#
def main():
    app.run(
        host='0.0.0.0',
        port=int('8000'),
        debug=True
    )

if __name__ == '__main__':
    main()
