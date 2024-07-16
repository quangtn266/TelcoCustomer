import sys
sys.path.append("/opt/airflow")

import os
from datetime import timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
from airflow.utils.timezone import datetime

from src.processing.data_transformation import read_data, split_train_test, preprocess_data