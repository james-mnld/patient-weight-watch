import psycopg2
import os
import pandas as pd

DATABASE = "weight_watcher"
USER = "weight_watcher"
PASSWORD = "letmewatch"
HOST = "127.0.0.1"
PORT = "5432"

"""
This script builds all required database and populates them with mock data
"""

# create PATIENT_INFO database
con = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD,
                       host=HOST, port=PORT)
print("Database opened successfully")
cur = con.cursor()
tab_name = 'PATIENT_INFO'
cur.execute("DROP TABLE IF EXISTS %s CASCADE" % tab_name)
cur.execute('''CREATE TABLE %s
      (PATIENTID       INT PRIMARY KEY     NOT NULL,
      LASTNAME         TEXT         NOT NULL,
      FIRSTNAME        TEXT         NOT NULL,
      SEX              CHAR(1)      NOT NULL,
      AGE              INT          NOT NULL,
      LAST_APPOINTMENT DATE         NOT NULL,
      LAST_SUBMIT      DATE         NOT NULL,
      TREATMENT        TEXT         NOT NULL,
      REC_WEIGHTS      TEXT         NOT NULL);''' % tab_name)
print("%s table created" % tab_name)
con.commit()


# create PATIENT_SYMPTOMS database
con = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD,
                       host=HOST, port=PORT)
print("Database opened successfully")
cur = con.cursor()
tab_name = 'PATIENT_SYMPTOMS'
cur.execute("DROP TABLE IF EXISTS %s CASCADE" % tab_name)
cur.execute('''CREATE TABLE %s
      (PATIENTID     INT     NOT NULL,
      PRIMARY KEY (PATIENTID),
      FOREIGN KEY (PATIENTID)
          REFERENCES PATIENT_INFO (PATIENTID)
          ON UPDATE CASCADE ON DELETE CASCADE,
      NAUSEA             INT    NOT NULL,
      SKIN_IRRITATE      INT    NOT NULL,
      DIFF_SWALLOW       INT    NOT NULL,
      DIFF_BREATH        INT    NOT NULL);''' % tab_name)
print("%s table created" % tab_name)
con.commit()


# create PATIENT_IMAGES database
con = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD,
                       host=HOST, port=PORT)
print("Database opened successfully")
cur = con.cursor()
tab_name = 'PATIENT_IMAGES'
cur.execute("DROP TABLE IF EXISTS %s CASCADE" % tab_name)
cur.execute('''CREATE TABLE %s
      (PATIENTID     INT     NOT NULL,
      PRIMARY KEY (PATIENTID),
      FOREIGN KEY (PATIENTID)
          REFERENCES PATIENT_INFO (PATIENTID)
          ON UPDATE CASCADE ON DELETE CASCADE,
      CT_PATH        TEXT    NOT NULL,
      CTcont_PATH    TEXT    NOT NULL,
      RT_PATH        TEXT    NOT NULL);''' % tab_name)
print("%s table created" % tab_name)
con.commit()


# populate PATIENT_INFO database
csv_path = 'data/PATIENT_INFO.csv'
DAT_patient_info = pd.read_csv(csv_path).values
con = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD,
                       host=HOST, port=PORT)
print("Database opened successfully")
cur = con.cursor()
for row in DAT_patient_info:
    cur.execute("""INSERT INTO PATIENT_INFO (PATIENTID,LASTNAME,FIRSTNAME,SEX,
                AGE,TREATMENT,LAST_APPOINTMENT,LAST_SUBMIT,REC_WEIGHTS) \
                VALUES (%i, '%s', '%s', '%c', %i, '%s', '%s', '%s', '%s') \
                """ % (row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                       row[7], row[8]))
con.commit()


# populate PATIENT_SYMPTOMS database
DAT_patient_symp = [
    [1, 3, 7, 4, 2],
    [2, 7, 4, 1, 2],
    [3, 7, 2, 6, 6],
    [4, 5, 1, 0, 1],
    [5, 4, 8, 0, 2],
    [6, 6, 7, 3, 2],
    [7, 7, 1, 5, 6],
    [8, 3, 0, 1, 3],
    [9, 4, 1, 3, 4]
    ]
con = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD,
                       host=HOST, port=PORT)
print("Database opened successfully")
cur = con.cursor()
for row in DAT_patient_symp:
    cur.execute("""INSERT INTO PATIENT_SYMPTOMS (PATIENTID,NAUSEA,
                SKIN_IRRITATE,DIFF_SWALLOW,DIFF_BREATH) \
                VALUES (%i, %i, %i, %i, %i)""" % (row[0], row[1], row[2],
                                                  row[3], row[4]))
con.commit()


# populate PATIENT_IMAGES database
path_img_root = 'static/patient_images/'
N_patients = 9
paths_list = []
# grab all image paths and store it in paths_list
for i in range(N_patients):
    pname = 'p'+str(i+1)
    pfolder = os.path.join(path_img_root, pname)
    tfolders = [os.path.join(pfolder, x) for x in os.listdir(pfolder)]
    pdict_paths = {'CT': [], 'CT_contours': [], 'RT_dose': []}
    for tfolder in tfolders:
        CT_folder = os.path.join(tfolder, 'CT')
        for fname in os.listdir(CT_folder):
            fpath = os.path.join(CT_folder, fname)
            pdict_paths['CT'].append(fpath)

        CTcont_folder = os.path.join(tfolder, 'CT_contours')
        for fname in os.listdir(CTcont_folder):
            fpath = os.path.join(CTcont_folder, fname)
            pdict_paths['CT_contours'].append(fpath)

        RTdose_folder = os.path.join(tfolder, 'RT_dose')
        for fname in os.listdir(RTdose_folder):
            fpath = os.path.join(RTdose_folder, fname)
            pdict_paths['RT_dose'].append(fpath)
    paths_list.append(pdict_paths)
# convert lists to strings
for patient in paths_list:
    patient['CT'] = ', '.join(patient['CT'])
    patient['CT_contours'] = ', '.join(patient['CT_contours'])
    patient['RT_dose'] = ', '.join(patient['RT_dose'])
# send database update command
con = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD,
                       host=HOST, port=PORT)
print("Database opened successfully")
cur = con.cursor()
for ind, patient in enumerate(paths_list):
    cur.execute("""INSERT INTO PATIENT_IMAGES (PATIENTID,CT_PATH,
                CTcont_PATH,RT_PATH) \
                VALUES (%i, '%s', '%s', '%s')""" % (ind+1, patient['CT'],
                                                    patient['CT_contours'],
                                                    patient['RT_dose']))
con.commit()
