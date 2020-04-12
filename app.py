from flask import Flask, render_template, request, jsonify, Response
from flask.json import JSONEncoder
from werkzeug.exceptions import BadRequestKeyError
from datetime import date, datetime
import psycopg2
import psycopg2.extras
import json
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

# Database login credentials
DATABASE = "weight_watcher"
USER = "weight_watcher"
PASSWORD = "letmewatch"
HOST = "127.0.0.1"
PORT = "5432"

# Mapping of formal table headers to column names on database
DASH_COLUMNS = [
                ("Patient ID", "patientid"),
                ("Lastname", "lastname"),
                ("Firstname", "firstname"),
                ("Sex", "sex"),
                ("Age", "age"),
                ("Treatment", "treatment"),
                ("Last Appointment", "last_appointment"),
                ("Last Weight", "last_weight"),
                ("Current Weight", "current_weight"),
                ("Change in Weight", "change_weight"),
                ("Last Submission", "last_submit")
                ]
SYMP_COLUMNS = [
                ("Nausea", "nausea"),
                ("Skin Irritation", "skin_irritate"),
                ("Difficulty Swallowing", "diff_swallow"),
                ("Difficulty Breathing", "diff_breath")
                ]

# Global variables for sorting functionality
DEF_SORT_KEY = "change_weight"
LAST_SORT_KEY = ""
REV_ORDER = False

# Datetime formats
DATETIME_FORMAT_LIVE = "%a %b/%d/%Y %H:%M:%S"
DATETIME_FORMAT_TABLE = "%a %b/%d/%Y"

# Modifiable global variable for recorded weights
REC_WEIGHTS = []


# JSON encoder to keep dates in the format yyyy-mm-dd
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, date):
                return obj.strftime(DATETIME_FORMAT_TABLE)  # %H:%M:%S")
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


app = Flask(__name__, template_folder='templates', static_url_path='/static')
app.json_encoder = CustomJSONEncoder
app.config["DEBUG"] = True


@app.route("/")
@app.route("/home")
@app.route("/index")
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    try:
        sort_key = request.form["sort_key"]
        update_last_sort(sort_key)
    except BadRequestKeyError:
        print('No POST form received')
        update_last_sort(DEF_SORT_KEY)
        global REV_ORDER
        REV_ORDER = False
    finally:
        response = update_dash()
        jsonDat = json.loads(response.get_data().decode("utf-8"))
        tabData = jsonDat["tab_dat"]
        lastUpdate = jsonDat["time"]
        sortStatus = jsonDat["sort"]

    return render_template('test.html', tabData=tabData, colNames=DASH_COLUMNS,
                           lastUpdate=lastUpdate, sortStatus=sortStatus)
    # return render_template('dashboard.html', tabData=tabData,
    #                        colNames=DASH_COLUMNS, lastUpdate=lastUpdate,
    #                        sortStatus=sortStatus)


# Function that sends time, sort, and database info as json to "/update_dash"
@app.route('/update_dash')
def update_dash():
    command_query_db = """SELECT * FROM PATIENT_INFO"""
    response = exec_db_command(command_query_db, 1)  # 1 returns fetchall
    rows = build_weights(response)

    if LAST_SORT_KEY != "":
        # use last sort settings for live update
        sort_key, rev_order = LAST_SORT_KEY, REV_ORDER
    else:
        sort_key, rev_order = DEF_SORT_KEY, False

    rows.sort(key=lambda k: k.get(sort_key), reverse=rev_order)

    sort_key_formal = get_formalized(sort_key)
    if rev_order:
        sort_key_formal += ' (reverse)'

    now = datetime.now().strftime(DATETIME_FORMAT_LIVE)
    return jsonify(time=now, sort=sort_key_formal, tab_dat=rows)


# Function that sends RT info, symptoms, and weight history to "/RT_symptoms"
@app.route('/RT_symptoms', methods=['POST'])
def get_RTsymptoms():
    p_id = int(request.form["p_id"])

    # query PATIENT_INFO using p_id
    command_query_info_db = """SELECT * FROM PATIENT_INFO
                        WHERE PATIENTID = %i""" % p_id
    response = exec_db_command(command_query_info_db, 1)
    row_info = build_weights(response)[0]  # just take the only element in list
    rec_weights_arr = [float(x) for x in row_info['rec_weights'].split(', ')]
    global REC_WEIGHTS
    REC_WEIGHTS = rec_weights_arr

    # query PATIENT_SYMPTOMS using p_id
    command_query_symp_db = """SELECT * FROM PATIENT_SYMPTOMS
                        WHERE PATIENTID = %i""" % p_id
    row_symp = exec_db_command(command_query_symp_db, 1)[0]

    # lvl_nausea = row_symp['nausea']
    # lvl_skinirr = row_symp['skin_irritate']
    # lvl_diffswal = row_symp['diff_swallow']
    # lvl_diffbreath = row_symp['diff_breath']

    # TODO: query PATIENT_IMAGE using p_id

    return render_template('RT_symptoms.html', p_id=p_id, defKey=DEF_SORT_KEY,
                           row_info=row_info, row_symp=row_symp,
                           colNames=DASH_COLUMNS, colNamesSymp=SYMP_COLUMNS)


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
                            """ % (', '+str(p_weight), datetime.now(), p_id)
    exec_db_command(command_update_info, 0)

    return render_template("submitted.html", p_weight=p_weight,
                           p_nausea=p_nausea, p_skinirr=p_skinirr,
                           p_diffswall=p_diffswall, p_diffbreath=p_diffbreath)


# Function that posts plot of recorded weights to '/weights_plot.png'
@app.route('/weights_plot.png')
def plot_weights():
    fig = create_figure(REC_WEIGHTS)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


# Helper function that plots weights trend of chosen patient
def create_figure(rec_weights):
    # TODO: beautify plot
    fig = Figure()
    ax = fig.add_subplot(1, 1, 1)
    x_vals = [x+1 for x in range(len(rec_weights))]
    ax.plot(x_vals, rec_weights)
    ax.set_xlabel('Day Number')
    ax.set_ylabel('Weights [kg]')
    ax.set_xticks(x_vals)
    ax.grid()
    fig.tight_layout()
    return fig


# Helper function to extract and format weight info from rec_weights column
def build_weights(p_list):
    new_list = []
    for dictionary in p_list:
        p_dict = dictionary.copy()
        weights = p_dict["rec_weights"].split(", ")

        last_weight = float(weights[-2])
        current_weight = float(weights[-1])
        change_weight = current_weight - last_weight

        p_dict["last_weight"] = float('%.2f' % last_weight)
        p_dict["current_weight"] = float('%.2f' % current_weight)
        p_dict["change_weight"] = float('%.2f' % change_weight)

        # print(p_dict)
        new_list.append(p_dict)
    return new_list


# Helper function that executes given MySQL string command
def exec_db_command(command, withval):
    con = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD,
                           host=HOST, port=PORT)
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(command)
    con.commit()
    if withval:  # if withval has value, return fetchall data
        return cur.fetchall()


# Helper function to get formal name of database column name
def get_formalized(db_col_name):
    for pair in DASH_COLUMNS:
        if pair[1] == db_col_name:
            return pair[0]
    return "Undefined column name"


# Helper function that updates global sort info
def update_last_sort(sort_key):
    global LAST_SORT_KEY, REV_ORDER
    if LAST_SORT_KEY == sort_key:
        # just inverse sort order
        REV_ORDER = not REV_ORDER
    else:
        # update sort key and reset sort order
        LAST_SORT_KEY = sort_key
        REV_ORDER = False
    print("LAST_SORT_KEY updated to:", LAST_SORT_KEY)
    print("REV_ORDER updated to:", REV_ORDER)


if __name__ == '__main__':
    app.run()
