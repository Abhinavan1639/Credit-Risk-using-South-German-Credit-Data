from sklearn.model_selection import train_test_split, cross_val_score,KFold, RepeatedStratifiedKFold
from sklearn.ensemble import RandomForestClassifier,GradientBoostingClassifier,AdaBoostClassifier
from sklearn.metrics import accuracy_score,confusion_matrix,precision_score,recall_score
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.linear_model import SGDClassifier,LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import BaggingClassifier
from imblearn.over_sampling import ADASYN
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier
from collections import Counter
from scipy.stats import randint
from sklearn.svm import SVC
import pandas as pd
import numpy as np
import warnings
import pickle


pd.set_option('display.max_columns',None)
warnings.filterwarnings('ignore')


df = pd.read_csv(r"C:\Users\Lenovo\PycharmProjects\GermanBankCreditCard\SouthGermanCredit\Final_Model.csv")
df.drop(['Unnamed: 0'],axis=1,inplace=True)


X=df.drop(['credit_risk'],axis=1)
y=df['credit_risk']


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


def model(X=X_train, y=y_train):
    
    models=[]
    models.append(('GradientBoostingClassifier',GradientBoostingClassifier()))
    models.append(('XGBClassifier',XGBClassifier(eval_metric='mlogloss')))
    models.append(('DecisionTreeClassifier',DecisionTreeClassifier()))
    models.append(('RandomForestClassifier',RandomForestClassifier()))
    models.append(('AdaBoostClassifier',AdaBoostClassifier()))
    models.append(('LogisticRegression',LogisticRegression()))
    models.append(('BaggingClassifier',BaggingClassifier()))
    models.append(('LGBMClassifier',LGBMClassifier()))
    models.append(('SGDClassifier',SGDClassifier()))
    models.append(('SVC',SVC()))
    
    results =[]
    names   =[]
    scoring ='accuracy'
    
    for name, model in models:
        #kfold = KFold(n_splits=10, random_state=42)
        kfold = RepeatedStratifiedKFold(n_splits=10, random_state=42, n_repeats=3)
        cross = cross_val_score(model, X, y, cv=kfold, scoring=scoring)
        results.append(cross)
        names.append(name)
        print (f'Model:{name},Mean: {cross.mean()},Std Dev: {cross.std()}')
        print('---'*25)

model(X_train,y_train)


ada = ADASYN(sampling_strategy='minority',random_state=42,n_neighbors=7)
X_res,y_res = ada.fit_resample(X_train,y_train)
Counter(y_res)


model(X_res,y_res)


param_distribs = {'n_estimators': randint(low=1, high=500),
                  'max_depth': randint(low=1, high=10),
                  'max_features':randint(low=1,high=10),
                 }

rnd_RF = RandomizedSearchCV(RandomForestClassifier(),param_distributions=param_distribs,n_iter=10,cv=5,scoring='accuracy', 
                            random_state=42)

rnd_RF.fit(X_res,y_res)
rnd_RF.best_params_


RFClassifier = RandomForestClassifier(max_depth=8, max_features=5, n_estimators=103, random_state=42)
RFClassifier.fit(X_res,y_res)


param_grid = [{'n_estimators': [3, 10, 30], 'max_depth': [2, 4, 6, 8],'booster': ['gbtree','dart'],
              'learning_rate':[0.3,0.5,0.01,0.1]}]

grid_xgb = GridSearchCV(XGBClassifier(eval_metric='mlogloss'), param_grid=param_grid, cv=5, scoring='accuracy', 
                        return_train_score=True)

grid_xgb.fit(X_res,y_res)
grid_xgb.best_params_


XGClassifier=XGBClassifier(booster='gbtree', learning_rate=0.5, max_depth=8, n_estimators=30, eval_metric='mlogloss')
XGClassifier.fit(X_res,y_res)


BClassifier = BaggingClassifier(base_estimator=XGBClassifier(eval_metric='mlogloss'),random_state=42)
BClassifier.fit(X_res,y_res)


LGBClassifier=LGBMClassifier(random_state=42)
LGBClassifier.fit(X_res,y_res)


GBClassifier=GradientBoostingClassifier(random_state=42)
GBClassifier.fit(X_res,y_res)


prediction_RF = RFClassifier.predict(X_test)

prediction_XGB = XGClassifier.predict(X_test)

prediction_Bagg = BClassifier.predict(X_test)

prediction_LGBM = LGBClassifier.predict(X_test)

prediction_GB = GBClassifier.predict(X_test)


print('Accuracy RForest...{}'.format(accuracy_score(y_test,prediction_RF)))
print('---'*25)
print('Accuracy XGBoost...{}'.format(accuracy_score(y_test,prediction_XGB)))
print('---'*25)
print('Accuracy Bagging...{}'.format(accuracy_score(y_test,prediction_Bagg)))
print('---'*25)
print('Accuracy LightGBM...{}'.format(accuracy_score(y_test,prediction_LGBM)))
print('---'*25)
print('Accuracy Gradient...{}'.format(accuracy_score(y_test,prediction_GB)))
print('---'*25)


print('Precision RForest...{}'.format(precision_score(y_test,prediction_RF)))
print('---'*25)
print('Precision XGBoost...{}'.format(precision_score(y_test,prediction_XGB)))
print('---'*25)
print('Precision Bagging...{}'.format(precision_score(y_test,prediction_Bagg)))
print('---'*25)
print('Precision LightGBM...{}'.format(precision_score(y_test,prediction_LGBM)))
print('---'*25)
print('Precision Gradient...{}'.format(precision_score(y_test,prediction_GB)))
print('---'*25)


print('Recall RForest...{}'.format(recall_score(y_test,prediction_RF)))
print('---'*25)
print('Recall XGBoost...{}'.format(recall_score(y_test,prediction_XGB)))
print('---'*25)
print('Recall Bagging...{}'.format(recall_score(y_test,prediction_Bagg)))
print('---'*25)
print('Recall LightGBM...{}'.format(recall_score(y_test,prediction_LGBM)))
print('---'*25)
print('Recall Gradient...{}'.format(recall_score(y_test,prediction_GB)))
print('---'*25)


print('Confusion Matrix RForest... \n {}'.format(confusion_matrix(y_test,prediction_RF)))
print('---'*25)
print('Confusion Matrix XGBoost... \n {}'.format(confusion_matrix(y_test,prediction_XGB)))
print('---'*25)
print('Confusion Matrix Bagging... \n {}'.format(confusion_matrix(y_test,prediction_Bagg)))
print('---'*25)
print('Confusion Matrix LightGBM... \n {}'.format(confusion_matrix(y_test,prediction_LGBM)))
print('---'*25)
print('Confusion Matrix Gradient... \n {}'.format(confusion_matrix(y_test,prediction_GB)))
print('---'*25)


file = 'Credit_Data_RF.pkl'

pickle.dump(RFClassifier,open(file,'wb'))
