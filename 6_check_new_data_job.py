from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.model_selection import train_test_split
import pandas as pd
import pickle
import cdsw
import os
import requests
import json
import datetime

## Creating the Jobs
# You need to create to jobs in the Jobs interface for this to work. The first job is called "Check Model"
# This job uses this python file `6_check_new_data_jpb.py` and will evaluate the performance of the current 
# model and if needed star the retrain process.
# The second job is called is called "Retail Model" which uses the `8_retrain_model.py` file. The "Check Model" 
# job launches the "Retrain Model" job using the REST API

# You need to provide the details below which you can read about here: 
# https://docs.cloudera.com/cdsw/1.9.0/jobs-pipelines/topics/cdsw-starting-a-job-run-using-python.html
# The JOB_ID is for the "Retrain Model" Job and can be obtained from the URL of the job.

HOST = "https://" + os.environ['CDSW_DOMAIN']
USERNAME = "nismaily"
API_KEY = "uyjx5yjpmcykb8zbwmd7wm3ekcestcxl"
PROJECT_NAME = "cc-fraud"
JOB_ID = "202"
NEW_DAY = datetime.datetime.today().weekday()

url = "/".join([HOST, "api/v1/projects", USERNAME, PROJECT_NAME, "jobs", JOB_ID, "start"])
job_params = {"DAY": str(NEW_DAY)}

print(url)

cc_data = pd.read_pickle("resources/credit_card_dataframe.pkl",compression="gzip")


X = cc_data[cc_data.Day == NEW_DAY].iloc[:,3:len(cc_data.columns)-1]
y = cc_data[cc_data.Day == NEW_DAY].iloc[:,len(cc_data.columns)-1]

X_train, X_test, y_train, y_test = train_test_split(
  X, y, test_size=0.3, random_state=42
)

randF = pickle.load(open("resources/cc_model.pkl","rb"))

predictions_rand=randF.predict(X_test)
auroc = roc_auc_score(y_test, predictions_rand)
ap = average_precision_score(y_test, predictions_rand)

print("auroc =",auroc)
print("ap =",ap)

if auroc < 0.99:
  print("model needs retraining")
  res = requests.post(
    url,
    headers = {"Content-Type": "application/json"},
    auth = (API_KEY,""),
    data = json.dumps({"environment": job_params})
  )
  print("URL", url)
  print("HTTP status code", res.status_code)
  print("Engine ID", res.json().get('engine_id'))
else:
  print("model is fine")