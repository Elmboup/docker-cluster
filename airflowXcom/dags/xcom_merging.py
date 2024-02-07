from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator

default_args = {
    'owner': 'el_mboup',
    'depends_on_past': False,
    'start_date': datetime(2024, 2, 7),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'dag_xcom_fusion_table',
    default_args=default_args,
    description='DAG complexe avec XCom et fusion de table',
    schedule_interval=timedelta(days=1),
)

# Création de deux tables PostgreSQL
create_table_1 = PostgresOperator(
    task_id='create_table_1',
    sql='CREATE TABLE IF NOT EXISTS table_1 (id SERIAL PRIMARY KEY, fname VARCHAR, lname VARCHAR);',
    postgres_conn_id='postgres_conn',
    dag=dag,
)

create_table_2 = PostgresOperator(
    task_id='create_table_2',
    sql='CREATE TABLE IF NOT EXISTS table_2 (id SERIAL PRIMARY KEY, age INT, fonction VARCHAR);',
    postgres_conn_id='postgres_conn',
    dag=dag,
)

# Insertion de données dans la première table
def insert_data_table_1(**kwargs):
    data = {
        'fname': 'Adama',
        'lname': 'Lo'
        
    }
    kwargs['ti'].xcom_push(key='data_table_1', value=data)

insert_data_task_1 = PythonOperator(
    task_id='insert_data_task_1',
    python_callable=insert_data_table_1,
    provide_context=True,
    dag=dag,
)

# Insertion de données dans la deuxième table
def insert_data_table_2(**kwargs):
    data = {
        'age': 21,
        'fonction': 'etudiant'
      
    }
    kwargs['ti'].xcom_push(key='data_table_2', value=data)

insert_data_task_2 = PythonOperator(
    task_id='insert_data_task_2',
    python_callable=insert_data_table_2,
    provide_context=True,
    dag=dag,
)

# Interrogation de la première table
def query_table_1(**kwargs):
    data_table_1 = kwargs['ti'].xcom_pull(task_ids='insert_data_task_1', key='data_table_1')
    # Logique pour interroger la table_1
    queried_data = f"Interrogation de table_1 avec données : {data_table_1}"
    kwargs['ti'].xcom_push(key='queried_data_1', value=queried_data)

query_table_task_1 = PythonOperator(
    task_id='query_table_task_1',
    python_callable=query_table_1,
    provide_context=True,
    dag=dag,
)

# Interrogation de la deuxième table
def query_table_2(**kwargs):
    data_table_2 = kwargs['ti'].xcom_pull(task_ids='insert_data_task_2', key='data_table_2')
    # Logique pour interroger la table_2
    queried_data = f"Interrogation de table_2 avec données : {data_table_2}"
    kwargs['ti'].xcom_push(key='queried_data_2', value=queried_data)

query_table_task_2 = PythonOperator(
    task_id='query_table_task_2',
    python_callable=query_table_2,
    provide_context=True,
    dag=dag,
)

# Fusion des données des deux tables pour créer une nouvelle table
def merge_data_and_create_table(**kwargs):
    data_table_1 = kwargs['ti'].xcom_pull(task_ids='insert_data_task_1', key='data_table_1')
    data_table_2 = kwargs['ti'].xcom_pull(task_ids='insert_data_task_2', key='data_table_2')

    # Logique pour fusionner les données et créer une nouvelle table
    merged_data = f"Données fusionnées : {data_table_1} + {data_table_2}"
    # Vous pouvez ajuster cette logique pour créer une nouvelle table ou effectuer d'autres opérations nécessaires.

merge_data_and_create_table_task = PythonOperator(
    task_id='merge_data_and_create_table_task',
    python_callable=merge_data_and_create_table,
    provide_context=True,
    dag=dag,
)

# Suppression des tables à la fin
drop_table_1 = PostgresOperator(
    task_id='drop_table_1',
    postgres_conn_id='postgres_conn',
    sql='DROP TABLE IF EXISTS table_1;',
    dag=dag,
)

drop_table_2 = PostgresOperator(
    task_id='drop_table_2',
    postgres_conn_id='postgres_conn',
    sql='DROP TABLE IF EXISTS table_2;',
    dag=dag,
)
# Définir l'ordre des tâches
create_table_1 >> insert_data_task_1 >> query_table_task_1
create_table_2 >> insert_data_task_2 >> query_table_task_2
[query_table_task_1, query_table_task_2] >> merge_data_and_create_table_task >> [drop_table_1, drop_table_2]