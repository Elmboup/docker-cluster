################################ *** MODULES IMPORT *** ########################################

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import attr

################## Paramètres par défaut du DAG ###############################
default_args = {
   'owner': 'el_mboup',
   'depends_on_past': False,
   'start_date': datetime(2024, 2, 6),
   'retries': 1,
   'retry_delay': timedelta(minutes=5),
}


#################################### *** FUNCTIONS *** ########################################

# Fonction pour interroger la table et retourner une valeur
def query_table_and_return_value(**kwargs):
    # Connexion à la base de données
    engine = create_engine('postgresql://airflow:airflow@postgres/airflow')
    
    # Exécution de la requête SQL pour obtenir le nombre de candidats valides
    query = "SELECT COUNT(*) FROM candidatures_presidentielle WHERE satut_validation = 'validée';"
    result = engine.execute(query).scalar()
    
    # Stockage du résultat dans XCom
    kwargs['ti'].xcom_push(key='validated_candidates_count', value=result)
    
    # Fermeture de la connexion
    engine.dispose()


# Fonction pour enregistrer les candidats valides dans une nouvelle table
def save_valid_candidates_to_new_table(**kwargs):
   # Récupération de la valeur stockée dans XCom
    validated_candidates_count = kwargs['ti'].xcom_pull(task_ids='query_and_return_value', key='validated_candidates_count')
    
    # Vérification si la valeur est présente et non nulle
    if validated_candidates_count is not None and validated_candidates_count > 0:
        # Connexion à la base de données
        engine = create_engine('postgresql://airflow:airflow@postgres/airflow')
        
        # Création de la nouvelle table avec le nombre de lignes spécifié par la valeur dans XCom
        engine.execute(f"CREATE TABLE IF NOT EXISTS new_valid_candidates AS SELECT * FROM candidatures_presidentielle WHERE satut_validation = 'validée' LIMIT {validated_candidates_count};")
        
        # Fermeture de la connexion
        engine.dispose()
    else:
        print("Aucun candidat valide à copier. La nouvelle table ne sera pas créée.")

######################################### *** END *** ########################################


# Définition des paramètres du DAG
dag = DAG(
   'senegal_presidential_election_dag',
   default_args=default_args,
   description='DAG to manage Senegal Presidential Election Candidate Table',
   schedule_interval=timedelta(days=1),
)


# Définition des tâches dans le DAG
###################### *** TASK1 *** ########################################
create_candidate_table_task = PostgresOperator(
   task_id='create_candidate_table',
   sql="""
   CREATE TABLE IF NOT EXISTS candidatures_presidentielle (
       id SERIAL PRIMARY KEY,
       prenom VARCHAR(255),
       nom VARCHAR(255),
       parti VARCHAR(255),
       satut_validation VARCHAR(50)
   );
   """,
   postgres_conn_id='postgres_conn',
   dag=dag,
)
###################### *** END *** ########################################


###################### *** TASK2 *** ########################################

insert_candidates_task = PostgresOperator(
   task_id='insert_candidates',
   sql="""
   INSERT INTO candidatures_presidentielle (prenom, nom, parti, satut_validation) VALUES
   ('Amadou', 'Ba', 'APR', 'validée'),
   ('Ousmane', 'Sonko', 'ex-PASTEF', 'Rejetée'),
   ('Karim', 'Wade', 'PDS', 'Rejetée'),
   ('Pape Djibril', 'Fall', 'Serviteur', 'validée'),
   ('Anta Babacar', 'Ngom', 'Alternative Citoyenne', 'validée');
   """,
   postgres_conn_id='postgres_conn',
   dag=dag,
)
###################### *** END *** ########################################

###################### *** TASK3 *** ########################################

query_and_return_value_task = PythonOperator(
   task_id='query_and_return_value',
   python_callable=query_table_and_return_value,
   provide_context=True,
   dag=dag,
)
###################### *** END *** ########################################

###################### *** TASK4 *** ########################################

save_valid_candidates_task = PythonOperator(
   task_id='save_valid_candidates_to_new_table',
   python_callable=save_valid_candidates_to_new_table,
   provide_context=True,
   dag=dag,
)
###################### *** END *** ########################################

###################### *** TASK5 *** ########################################

delete_table_task = PostgresOperator(
   task_id='delete_invalid_candidates',
   sql="DROP TABLE IF EXISTS candidatures_presidentielle ;",
   postgres_conn_id='postgres_conn',
   dag=dag,
)
###################### *** END *** ########################################


###################### *** PIPELINE *** ########################################

# l'ordre d'exécution des tâches
create_candidate_table_task >> insert_candidates_task >> query_and_return_value_task >> save_valid_candidates_task >> delete_table_task
