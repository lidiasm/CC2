from datetime import timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
import requests

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(2), # Comienza inmediatamente.
    'email': ['lidiasm96@correo.ugr.es'], # Email al que enviar el informe si hay error.
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5), # Cada cuanto se reintenta la ejecución.
}

# Inicializamos el grafo de tareas.
dag = DAG(
    'practica2',
    default_args=default_args,
    description='Grafo de tareas de la practica 2',
    schedule_interval=timedelta(days=1),
)
# PrepararEntorno es una tarea encargada de crear el direcotorio donde almacenar
# los ficheros de datos que se descargarán a continuación.
PrepararEntorno = BashOperator(
                    task_id='preparar_entorno',
                    depends_on_past=False,
                    bash_command='mkdir -p /tmp/workflow/', # Con la opción "-p" intentará crear el directorio si no existe. Si existe no lanza error.
                    dag=dag
                    )
# CapturaDatosHumedad: se encarga de descargar el fichero de datos que contiene la humedad.
CapturaDatosHumedad = BashOperator(
                        task_id='captura_datos_hum',
                        depends_on_past=False,
                        bash_command='wget --output-document /tmp/workflow/humidity.csv.zip https://raw.githubusercontent.com/manuparra/MaterialCC2020/master/humidity.csv.zip',
                        dag=dag
                        )
# CapturaDatosTemperatura: tarea encargada de descargar el otro fichero de datos con las temperaturas.
CapturaDatosTemperatura = BashOperator(
                            task_id='captura_datos_temp',
                            depends_on_past=False,
                            bash_command='wget --output-document /tmp/workflow/temperature.csv.zip https://raw.githubusercontent.com/manuparra/MaterialCC2020/master/temperature.csv.zip',
                            dag=dag
                            )
# DescomprimirDatos: tarea encargada de descomprimir ambos ficheros.
# Con la opción "-d" especificamos la ruta donde queremos que descomprima los ficheros
DescomprimirDatos = BashOperator(
                        task_id='descomprimir_datos',
                        depends_on_past=False,
                        bash_command='unzip /tmp/workflow/temperature.csv.zip -d /tmp/workflow ; unzip /tmp/workflow/humidity.csv.zip -d /tmp/workflow',
                        dag=dag
                        )

## ORDEN DE EJECUCIÓN DE TAREAS
PrepararEntorno >> [CapturaDatosHumedad, CapturaDatosTemperatura] >> DescomprimirDatos