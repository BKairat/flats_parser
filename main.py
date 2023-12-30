from flask import Flask, render_template, jsonify, request
import os
from config import db_name, db_user, db_password, db_host, db_port
from parser import parse_links
import psycopg2

app = Flask(__name__)

max_input = 700

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
       user_input = request.form.get('user_input')
       int_input = min(int(user_input), max_input)
       url = 'https://www.sreality.cz/hledani/prodej/byty?strana='
       parse_links(url, flats=int_input)

    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )

    # conn = psycopg2.connect(
    #     dbname=os.environ.get("POSTGRES_DB"),
    #     user=os.environ.get("POSTGRES_USER"),
    #     password=os.environ.get("POSTGRES_PASSWORD"),
    #     host=os.environ.get("POSTGRES_HOST"),
    #     port=os.environ.get("POSTGRES_PORT")
    # )

    cur = conn.cursor()

    cur.execute('SELECT * FROM example_table')

    rows = cur.fetchall()

    cur.close()
    conn.close()
    return render_template('index.html', rows=rows, element=len(rows))


if __name__ == ('__main__'):
    app.run(host='127.0.0.1', debug=False, port=8080)