from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.apache.hive.operators.hive import HiveOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.ssh.operators.ssh import SSHOperator

#from airflow.providers.email.operators.email import EmailOperator
import requests
import os
import json
import pandas as pd
from pyspark.sql import SparkSession
import psycopg2
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType, IntegerType
from pyspark.sql.functions import to_timestamp
from pyspark.sql import HiveContext


default_args = {
    'owner': 'El hadi Mboup',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email': ['ehmboup27@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

dag = DAG('weather_data_pipeline', default_args=default_args, schedule_interval='@daily')

# Task 1: Check availability of weather data API
check_weather_api = HttpSensor(
    task_id='check_weather_api',
    http_conn_id='weather_api',
    method='GET',
    endpoint='current.json?key=...................&q=Dakar&aqi=no',  # Replace with WeatherAPI endpoint with you key
    response_check=lambda response: True if response.status_code == 200 else False,
    poke_interval=60 * 60 * 24,  # Check once a day
    timeout=20,
    dag=dag
)

# Task 2: Download weather data from WeatherAPI
def download_weather_data(**kwargs):
    api_endpoint = "http://api.weatherapi.com/v1/forecast.json?key=74e0a587956544829b9120259233011&q="
    regions = [ "Dakar", "Diourbel", "Fatick", "Kaffrine", "Kaolack", "Kédougou", "Kolda", "Louga", "Matam", "Saint-Louis", "Sédhiou", "Tambacounda", "Thiès", "Ziguinchor"]
    
    # Fetch data and save to file
    with open('/usr/local/airflow/dags/data/weather_data.csv', 'w') as file:
        for region in regions:
            response = requests.get(f"{api_endpoint}{region}")
            weather_data = response.json()
            current_weather = weather_data.get('current', {})
            humidity = current_weather.get('humidity')
            longitude = weather_data.get('location', {}).get('lon')
            latitude = weather_data.get('location', {}).get('lat')
            localtime = weather_data.get('location', {}).get('localtime')
            
            forecast_data = weather_data.get('forecast', {}).get('forecastday', [])

            for forecast in forecast_data:
                day_forecast = forecast.get('day', {})
                max_temp_c = day_forecast.get('maxtemp_c')
                min_temp_c = day_forecast.get('mintemp_c')
           

                # Écrivons les données récupérées dans le fichier 
                file.write(f"{region},{latitude}, {longitude}, {localtime}, {max_temp_c}, {min_temp_c},{humidity}\n")


download_weather_task = PythonOperator(
    task_id='download_weather_data',
    python_callable=download_weather_data,
    dag=dag
)

# Task 3: Check availability of the .csv file 
def check_csv_file(): 
    return os.path.isfile('/usr/local/airflow/dags/data/weather_data.csv')

csv_file_availabity_task = PythonOperator(
    task_id='csv_file_availability',
    python_callable=check_csv_file,
    dag=dag
)



# Task 4: Process weather data with Spark
#Data processing with spark
def process_weather_data_with_spark(**kwargs):
    # Spark session & context
    spark = (SparkSession
         .builder
         .master("local")
         .config("hive.metastore.uris", "thrift://localhost:9083")
         .appName("weatherDataProcessing")
         .getOrCreate())
#    sc = spark.sparkContext
    
    # Définition du schéma pour les données à écrire dans le fichier 
    schema = StructType([ 
    	StructField('_c0', StringType(), True), 
    	StructField('_c1', DoubleType(), True), 
    	StructField('_c2', DoubleType(), True), 
    	StructField('_c3', TimestampType(), True), 
    	StructField('_c4', DoubleType(), True), 
    	StructField('_c5', DoubleType(), True), 
    	StructField('_c6', IntegerType(), True), 
    	])

    # Load data from file with Spark
    df = spark.read.csv('/usr/local/airflow/dags/data/weather_data.csv', header=False, schema=schema)
    
     # Select columns
    selected_data = df.select('_c0', '_c1', '_c2', '_c3', '_c4', '_c5', '_c6') # Adjust column names accordingly
    
    from pyspark.sql.functions import col

    # Renommer les colonnes dans le DataFrame Spark
    selected_data = selected_data.withColumnRenamed('_c0', 'region') \
        .withColumnRenamed('_c1', 'latitude') \
        .withColumnRenamed('_c2', 'longitude') \
        .withColumnRenamed('_c3', 'localtime') \
        .withColumnRenamed('_c4', 'max_temp_c') \
        .withColumnRenamed('_c5', 'min_temp_c') \
        .withColumnRenamed('_c6', 'humidity')


    # Convertir Spark DataFrame en une liste de lignes 
    rows = selected_data.collect() # Construire un Pandas DataFrame à partir de la liste de lignes 
    pd.DataFrame.iteritems = pd.DataFrame.items
    pandas_df = pd.DataFrame(rows, columns=['region', 'latitude', 'longitude', 'localtime', 'max_temp_c', 'min_temp_c', 'humidity'])
    



    # Convert Pandas DataFrame back to Spark DataFrame
    processed_spark_df = spark.createDataFrame(pandas_df)
    #processed_spark_df = selected_data
    
    # save processed data back to spark/resources
    processed_spark_df.repartition(1).write.mode('overwrite').format('csv').save('/usr/local/spark/resources/sen_weather', header=True)


process_with_spark_task = PythonOperator(
    task_id='process_with_spark',
    python_callable=process_weather_data_with_spark,
    dag=dag
)


#task 5 : Save weather_data to hdfs

save_to_hdfs_task = SparkSubmitOperator( 
    task_id='save_to_hdfs', 
    application='//usr/local/spark/app/save_to_spark.py', # Chemin vers le script Python 
    conn_id='spark_default', # Connexion Spark dans Airflow 
    verbose=False, 
    dag=dag, )



# tash 6 : Tâche pour créer une table Hive à partir du fichier CSV dans HDFS
hql_query = """
CREATE TABLE IF NOT EXISTS weather_data_table (
    region STRING,
    latitude DOUBLE,
    longitude DOUBLE,
    localtime STRING,
    max_temp_c DOUBLE,
    min_temp_c DOUBLE,
    humidity DOUBLE
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/hdfs/weather_data/processed_weather_data.csv'; -- Remplace avec le bon chemin dans HDFS

"""

 #   bash_command="beeline -u jdbc:hive2:// -e '{hql_query}';",
create_hive_table_task = HiveOperator(
    task_id='create_hive_table',
    hql=hql_query,
    hive_cli_conn_id='hive_cli_default',
    schema='default',
    hiveconfs=None,
    dag=dag
)




# Task 7: Send an Email Notification
send_email_notification_task = DummyOperator(
    task_id='send_email_notification', dag=dag)

# Define task dependencies
check_weather_api >> download_weather_task >> csv_file_availabity_task >> process_with_spark_task >> save_to_hdfs_task >> create_hive_table_task >> send_email_notification_task

