# Airflow DAG - Gestion des Candidatures Présidentielles: Xcoms practice

## Introduction
Ce projet utilise Apache Airflow pour automatiser la gestion des candidatures présidentielles. Le DAG (Directed Acyclic Graph) est conçu pour accomplir les tâches suivantes :
1. Interroger la base de données pour obtenir le nombre de candidats validés.
2. Stocker ce nombre dans une nouvelle table avec un timestamp.(avec une table postgresql externe). Mais Xcom peut vous épargner ça.
3. Prendre des décisions basées sur le nombre de candidats validés.

## XCom - Échange de Données entre Tâches
[XCom](https://airflow.apache.org/docs/apache-airflow/stable/concepts/xcoms.html) est un mécanisme intégré dans Apache Airflow permettant l'échange de données entre les différentes tâches d'un DAG. Il est utilisé dans ce projet pour transmettre le nombre de candidats validés d'une tâche à une autre.

### Avantages de l'utilisation de XCom :
1. **Simplicité de Configuration :** En utilisant XCom, nous évitons la configuration supplémentaire d'une base de données externe pour stocker des données intermédiaires. Cela simplifie le déploiement et la maintenance du système.

2. **Réduction de la Complexité :** En éliminant la nécessité de gérer des connexions de base de données externes, nous réduisons la complexité du DAG. Il n'est pas nécessaire de gérer l'ouverture et la fermeture de connexions, ni de gérer les dépendances avec une base de données externe.

3. **Temps d'Exécution :** En utilisant XCom, les données sont échangées en mémoire à l'intérieur de Airflow, ce qui peut réduire les temps d'exécution globaux par rapport à l'utilisation d'une base de données externe, qui impliquerait des opérations d'entrée/sortie supplémentaires.

### Limitations de XCom :
1. **Taille des Données :** XCom est plus adapté pour échanger des petites quantités de données. Pour des volumes de données importants, d'autres mécanismes de stockage comme une base de données externe peuvent être plus appropriés.
NB :  Xcom size limit
 SQLite—Stored as BLOB type, 2GB limit
 PostgreSQL—Stored as BYTEA type, 1 GB limit
 MySQL—Stored as BLOB type, 64 KB limit
2. **Synchronisation :** XCom fonctionne de manière synchrone, ce qui peut entraîner des problèmes de performances si les tâches dépendent les unes des autres et prennent beaucoup de temps.

3. **Complexité :** Dans des cas complexes, la gestion des dépendances entre les tâches peut devenir complexe avec XCom.

## Instructions d'Exécution
1. Assurez-vous qu'Apache Airflow est correctement configuré et que le DAG est placé dans le répertoire approprié.
2. Exécutez le DAG selon la planification définie.
3. Exécuter airflow avec docker-desktop (Suivez ce tuto pour l'installation: https://youtu.be/aTaytcxy2Ck)

N'hésitez pas à explorer le code source pour des détails plus spécifiques sur les tâches et les fonctions utilisées.

Pour toute question ou problème, veuillez contacter mboupeh@ept.sn.
