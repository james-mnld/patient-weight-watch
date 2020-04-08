from flask import Flask, render_template, request, jsonify
from datetime import date, datetime
import psycopg2
import psycopg2.extras

DATABASE = "weight_watcher"
USER = "weight_watcher"
PASSWORD = "letmewatch"
HOST = "127.0.0.1"
PORT = "5432"

app = Flask(__name__, template_folder='templates')
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")


@app.route('/dashboard')
def dashboard():
    command_query_db = """SELECT * FROM PATIENT_INFO"""
    response = exec_db_command(command_query_db, 1)  # 1 returns fetchall
    rows = build_weights(response)
    return render_template('test.html', tabData=rows,
                           lastUpdate=datetime.now())
    # return render_template('dashboard.html')


# Helper function to extract and format weight info from rec_weights column
def build_weights(p_list):
    new_list = []
    for dictionary in p_list:
        p_dict = dictionary.copy()
        weights = p_dict["rec_weights"].split(", ")

        last_weight = float(weights[-2])
        current_weight = float(weights[-1])
        change_weight = current_weight - last_weight

        p_dict["last_weight"] = '%.2f' % last_weight
        p_dict["current_weight"] = '%.2f' % current_weight
        p_dict["change_weight"] = '%.2f' % change_weight

        print(p_dict)
        new_list.append(p_dict)
    return new_list


# Function called upon submission of symptom webform (db for database)
@app.route('/update_db', methods=['POST'])
def update_db():
    p_id = int(request.form["p_id"])
    p_weight = request.form["p_weight"]
    p_nausea = int(request.form["p_nausea"])
    p_skinirr = int(request.form["p_skinirr"])
    p_diffswall = int(request.form["p_diffswall"])
    p_diffbreath = int(request.form["p_diffbreath"])

    # update PATIENT_SYMPTOMS
    command_update_symp = """UPDATE PATIENT_SYMPTOMS \
                            SET NAUSEA = %i, SKIN_IRRITATE = %i, \
                            DIFF_SWALLOW = %i, DIFF_BREATH = %i \
                            WHERE PATIENTID = %i \
                            """ % (p_nausea, p_skinirr, p_diffswall,
                                   p_diffbreath, p_id)
    exec_db_command(command_update_symp, 0)

    # update rec_weights and last_submit on PATIENT_INFO
    command_update_info = """UPDATE PATIENT_INFO \
                            SET REC_WEIGHTS = REC_WEIGHTS || '%s', \
                            LAST_SUBMIT = '%s' \
                            WHERE PATIENTID = %i \
                            """ % (', '+str(p_weight), date.today(), p_id)
    exec_db_command(command_update_info, 0)

    return render_template("submitted.html", p_weight=p_weight,
                           p_nausea=p_nausea, p_skinirr=p_skinirr,
                           p_diffswall=p_diffswall, p_diffbreath=p_diffbreath)


# Helper function that executes given MySQL string command
def exec_db_command(command, withval):
    con = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD,
                           host=HOST, port=PORT)
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(command)
    con.commit()
    if withval:  # if withval has value, return fetchall data
        return cur.fetchall()


@app.route('/update_dash')
def update_dash():
    command_query_db = """SELECT * FROM PATIENT_INFO"""
    response = exec_db_command(command_query_db, 1)  # 1 returns fetchall
    rows = build_weights(response)
    return jsonify(time=datetime.now(), sort="DEFAULT", tab_dat=rows)
    # return str(datetime.now())


if __name__ == '__main__':
    app.run()
