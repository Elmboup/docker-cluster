from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
#from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

#from airflow.providers.apache.spark.hooks.spark_submit import
from airflow.utils.dates import days_ago


spark_master = " spark://09e38a89944b:7077"
spark_app_name = "Spark Hello World"
file_path = "/usr/local/spark/resources/data/test.csv"

args = {
    'owner': 'el_mboup',
}

with DAG(
    dag_id='test_spark_submit_operator',
    default_args=args,
    schedule_interval=None,
    start_date=days_ago(2),
    tags=['test'],
) as dag:

    start = DummyOperator(task_id="start", dag=dag)

    spark_job = SparkSubmitOperator(
        task_id="spark_job",
        application="/usr/local/spark/app/hello-world-spark.py",
        name=spark_app_name,
        conn_id="spark_default",
        verbose=1,
        conf={"spark.master":spark_master},
        application_args=[file_path],
        dag=dag
    )

    end = DummyOperator(task_id="end", dag=dag)

    start >> spark_job >> end
    
