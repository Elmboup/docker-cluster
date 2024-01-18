from pyspark.sql import SparkSession
import os


def save_to_hdfs():
    # Chemin du répertoire contenant les fichiers CSV
    directory_path = '/usr/local/spark/resources/'

    # Récupérer tous les fichiers dans le répertoire
    files = os.listdir(directory_path)

    # Filtrer les fichiers CSV
    csv_files = [file for file in files if file.endswith('.csv')]

    # Sélectionner le fichier CSV le plus récent (ou le fichier selon vos critères)
    latest_csv_file = max(csv_files, key=os.path.getctime)

    # Chemin complet du fichier CSV le plus récent
    file_path = os.path.join(directory_path, latest_csv_file)

   # Initialisez ou récupérez votre SparkSession
    spark = (SparkSession
            .builder
            .appName("Save Weather Data to HDFS")
            .getOrCreate())


   # Lire le fichier CSV ou créer le DataFrame météo à partir d'une source
    weather_data = spark.read.csv('/usr/local/airflow/dags/data/weather_data.csv', header=True)


# Écrivons les données sous forme de fichiers Parquet dans HDFS
    weather_data.write.option('header', True) \
       .partitionBy('region') \
       .mode('overwrite') \
       .parquet('hdfs://namenode:9000/sen_weather/weather_data.parquet')
