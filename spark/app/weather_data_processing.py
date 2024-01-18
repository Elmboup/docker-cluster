from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Initialiser la session Spark
spark = SparkSession.builder.appName("WeatherDataProcessing").getOrCreate()

# Lire les données météorologiques depuis l'API OpenWeatherMap (ex. en utilisant HTTP GET)
# Vous devrez adapter cette partie pour lire les données depuis l'API en utilisant une bibliothèque HTTP en Python

# Exemple de lecture de données depuis un fichier JSON local (à remplacer par la lecture de l'API)
data = spark.read.json("../sandbox/spark/resources/data/weather_data_{timestamp}.json")

# Sélectionner les colonnes pertinentes
selected_data = data.select(
    col("dt").alias("timestamp"),
    col("main.temp").alias("temperature"),
    col("main.pressure").alias("pressure"),
    col("main.humidity").alias("humidity"),
    col("wind.speed").alias("wind_speed"),
    col("wind.deg").alias("wind_direction"),
    col("weather[0].main").alias("weather_condition"),
)

# Afficher le schéma des données
selected_data.printSchema()

# Sauvegarder les données traitées dans un format adapté à votre entrepôt de données (ex. PostgreSQL)
# Vous pouvez ajuster le format de sauvegarde en fonction de votre entrepôt de données
selected_data.write.format("jdbc").options(
    url="jdbc:postgresql://postgres:5432/airflow",
    dbtable="weather_data",
    user="airflow",
    password="airflow",
).mode("overwrite").save()

# Arrêter la session Spark
spark.stop()

