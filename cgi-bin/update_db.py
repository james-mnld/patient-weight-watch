#!/usr/bin/python3
"""
This script is called by webform upon submission to update the database
"""

import cgi
import psycopg2

DATABASE = "weight_watcher"
USER = "weight_watcher"
PASSWORD = "letmewatch"
HOST = "127.0.0.1"
PORT = "5432"

# grab fields from form sent
formData = cgi.FieldStorage()

p_id = formData.getvalue("p_id")
p_weight = formData.getvalue("p_weight")
p_nausea = formData.getvalue("p_nausea")
p_skinirr = formData.getvalue("p_skinirr")
p_diffswall = formData.getvalue("p_diffswall")
p_diffbreath = formData.getvalue("p_diffbreath")

print(p_id, p_nausea, p_skinirr, p_diffswall, p_diffbreath)

# command_update_symp = """INSERT INTO PATIENT_SYMPTOMS (PATIENTID,NAUSEA,SKIN_IRRITATE,DIFF_SWALLOW,DIFF_BREATH) \
#                         VALUES (%i, %i, %i, %i, %i)""" % (p_id, p_nausea, p_skinirr, p_diffswall, p_diffbreath)
# command_update_info =
#
# con = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
# cur = con.cursor()
# cur.execute(update_command)
# con.commit()
