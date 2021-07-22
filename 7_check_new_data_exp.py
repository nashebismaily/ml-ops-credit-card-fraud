from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.model_selection import train_test_split
import pandas as pd
import pickle
import cdsw
import sys
from pyspark.sql import SparkSession


cc_data = pd.read_pickle("resources/credit_card_dataframe.pkl",compression="gzip")

new_day = int(sys.argv[1])

X = cc_data[cc_data.Day == new_day].iloc[:,3:len(cc_data.columns)-1]
y = cc_data[cc_data.Day == new_day].iloc[:,len(cc_data.columns)-1]

X_train, X_test, y_train, y_test = train_test_split(
  X, y, test_size=0.3, random_state=42
)

randF = pickle.load(open("resources/cc_model.pkl","rb"))

predictions_rand=randF.predict(X_test)
auroc = roc_auc_score(y_test, predictions_rand)
ap = average_precision_score(y_test, predictions_rand)

print("auroc =",auroc)
print("ap =",ap)

cdsw.track_metric("auroc", round(auroc,2))
cdsw.track_metric("ap", round(ap,2))

if auroc < 0.9:
  cdsw.track_metric("retrain", "Yes")
else:
  cdsw.track_metric("retrain", "No")