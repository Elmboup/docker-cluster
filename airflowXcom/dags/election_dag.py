######################################### *** Modules import *** ########################################

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator
from sqlalchemy import create_engine
import pandas as pd


######################################## Paramètres par défaut du DAG ################################
default_args ={
   'owner': 'El_mboup',
   'depends_on_past': False,
   'start_date': datetime(2024, 2, 6),
   'retries':1,
   'retry_delay': timedelta(minutes=3)
}
candidatures_validees = []


############################################ Définition du DAG ###########################################
dag = DAG(
   'airflow-postgres-dag',
   default_args = default_args,
   description ='DAG pour manipuler une table postgreSQL',
   schedule_interval = timedelta(days=1)
)


######################################### *** Tasks definitions *** ########################################

################ Tâche 1: Création d'une table PostgreSQL ####################

# Fonction pour créer la table des candidats
def create_candidate_table():
   # Création de la table des candidats avec les colonnes spécifiées
   create_table_query = """
   CREATE TABLE IF NOT EXISTS candidatures_presidentielle (
       id SERIAL PRIMARY KEY,
       prenom VARCHAR(255),
       nom VARCHAR(255),
       parti VARCHAR(255),
       satut_validation VARCHAR(50)
   );
   """
   # Utilisation de l'opérateur PostgresOperator pour exécuter la requête SQL
   PostgresOperator(
       task_id='create_candidate_table',
       sql=create_table_query,
       postgres_conn_id='postgres_conn',
       dag=dag,
   ).execute(context=None)


create_table_task = PythonOperator(
   task_id='create_table',
   python_callable=create_candidate_table,
   dag=dag,
)

################# Tâches 2 : Insertion de données dans la table ###################

# Fonction pour insérer des données de candidats dans la table
def insert_candidates():
   # Insérez les données des candidats dans la table
   insert_query = """
   INSERT INTO candidatures_presidentielle (prenom, nom, parti, satut_validation) VALUES
   ('Amadou', 'Ba', 'APR', 'validée'),
   ('Ousmane', 'Sonko', 'ex-PASTEF', 'Rejetée'),
   ('Karim', 'Wade', 'PDS', 'Rejetée'),
   ('Pape Djibril', 'Fall', 'Serviteur', 'validée'),
   ('Anta Babacar', 'Ngom', 'Alternative Citoyenne', 'validée');
   """
   # Utilisation de l'opérateur PostgresOperator pour exécuter la requête SQL
   PostgresOperator(
       task_id='insert_candidates',
       sql=insert_query,
       postgres_conn_id='postgres_conn',
       dag=dag,
   ).execute(context=None)

insert_data_task = PythonOperator(
   task_id='insert_data',
   python_callable=insert_candidates,
   dag=dag,
)

######################## Tâche 3: Interrogeons la table#######################

# Fonction pour interroger la table et retourner une valeur
def query_table_and_store_value():
    # Connexion à la base de données
    engine = create_engine('postgresql://airflow:airflow@postgres/airflow')
    
    # Exécution de la requête SQL pour obtenir le nombre de candidats valides
    query = "SELECT COUNT(*) FROM candidatures_presidentielle WHERE satut_validation = 'validée';"
    result = engine.execute(query).scalar()
    
   # Timestamp actuel
    current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Stockage du résultat et du timestamp dans la table result_table
    engine.execute("CREATE TABLE IF NOT EXISTS resultat_table (validated_candidates_count INT, timestamp TIMESTAMP);")
    engine.execute("INSERT INTO resultat_table (validated_candidates_count, timestamp) VALUES (%s, %s);", result, current_timestamp)
    print(query)
    # Fermeture de la connexion
    engine.dispose()

query_and_return_value_task = PythonOperator(
   task_id='query_and_return_value',
   python_callable=query_table_and_store_value,
   dag=dag,
)

###################### Tâche 4 pour enregistrer les candidatures valides dans une autre table ###########################

def make_decision_based_on_value():
    # Connexion à la base de données
    engine = create_engine('postgresql://airflow:airflow@postgres/airflow')
    
    # Exécution de la requête SQL pour obtenir la valeur stockée
    query = "SELECT validated_candidates_count FROM resultat_table;"
    result = engine.execute(query).scalar()
    
    # Fermeture de la connexion
    engine.dispose()
    
    # Prise de décision en fonction de la valeur
    if result is not None and 2 <= result <= 7:
        print("La valeur est comprise entre 2 et 7. Création d'une nouvelle table pour les candidats valides.")
        # Création de la nouvelle table avec le nombre de lignes spécifié par la valeur dans XCom
        engine.execute(f"CREATE TABLE IF NOT EXISTS valid_candidates AS SELECT * FROM candidatures_presidentielle WHERE satut_validation = 'validée';")
        
    elif result is not None and result > 7:
        print("La valeur est supérieure à 7. Conseil : renforcer le parrainage.")
    else:
        print("Aucun candidat valide à copier. Aucune action requise.")


save_valid_candidates_task = PythonOperator(
   task_id='save_valid_candidates_to_new_table',
   python_callable=make_decision_based_on_value,
   dag=dag,
)

################# Tâche 5 : Suppression de l'ancienne table #######################
# Fonction pour supprimer l'ancienne table
def delete_table():
   
   delete_query = "DROP TABLE IF EXISTS candidatures_presidentielle ;"
   # Utilisation de l'opérateur PostgresOperator pour exécuter la requête SQL
   PostgresOperator(
       task_id='delete_invalid_candidates',
       sql=delete_query,
       postgres_conn_id='postgres_conn',
       dag=dag,
   ).execute(context=None)


delete_table_task = PythonOperator(
   task_id='delete_table',
   python_callable=delete_table,
   dag=dag,
)

######################################### *** Pipeline *** ########################################

# Pipeline d'exécution des tâches
create_table_task >> insert_data_task >>query_and_return_value_task >> save_valid_candidates_task >> delete_table_task

















