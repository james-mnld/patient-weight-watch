from flask import Flask, render_template, request
import psycopg2

DATABASE = "weight_watcher"
USER = "weight_watcher"
PASSWORD = "letmewatch"
HOST = "127.0.0.1"
PORT = "5432"

app = Flask(__name__, template_folder='templates')
app.config["DEBUG"] = True


@app.route('/home', methods=['GET'])
def home():
    return render_template("home.html")

# Function called upon submission of symptom webform
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
    exec_db_command(command_update_symp)

    # update rec_weights on PATIENT_INFO
    command_update_info = """UPDATE PATIENT_INFO \
                            SET REC_WEIGHTS = REC_WEIGHTS || '%s' \
                            WHERE PATIENTID = %i \
                            """ % (', '+str(p_weight), p_id)
    exec_db_command(command_update_info)

    return render_template("submitted.html", p_weight=p_weight,
                           p_nausea=p_nausea, p_skinirr=p_skinirr,
                           p_diffswall=p_diffswall, p_diffbreath=p_diffbreath)


# Helper function that executes given MySQL string command
def exec_db_command(command):
    con = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD,
                           host=HOST, port=PORT)
    cur = con.cursor()
    cur.execute(command)
    con.commit()


app.run()
