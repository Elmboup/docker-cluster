# Projet Data Engineering avec Docker

Ce projet vise à créer un environnement Docker complet pour le développement de pipelines de données avec des technologies telles qu'Airflow, Spark, Hive, Hadoop, PostgreSQL, Jupyter, Superset, et Zoho Analytics.
![weather data pipeline image](https://github.com/Elmboup/docker-cluster/blob/main/pipeline.jpg?raw=true)

## Configuration requise
- Docker
- Docker Compose

## Installation et exécution

1. Clonez ce référentiel :
   ```bash
   git clone https://github.com/Elmboup/docker-cluster.git
   cd docker-cluster

1. Lancer les conteneurs Docker :
   ```bash
   docker-compose up -d

2. Accéder aux interfaces utilisateur web des services :
  
- Airflow: http://localhost:8080
- Spark Master: http://localhost:8081
- hadoop Namenode: http://localhost:9870
- Superset: http://localhost:8088
- Jupyter: http://localhost:8888
- Zoho Analytics: http://localhost:8087
Adapter les ports en fonction de la configuration. 

## Services inclus
- Airflow: Orchestration des tâches du pipeline de données.
- Spark: Traitement des données en mode distribué.
- Hive: Stockage des métadonnées et requêtage des données.
- Hadoop: Stockage distribué des données.
- PostgreSQL: Stockage des métadonnées Airflow et Hive.
- Jupyter: Environnement de notebook pour l'exploration des données.
- Superset: Création de tableaux de bord et visualisation des données.
- Zoho Analytics: Outil BI.


