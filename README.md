# Splice Machine Apache Zeppelin notebooks

## Updating your Zeppelin instance with all notebooks in this repo
If you would like to load these notebooks in your current zeppelin cluster you can use the load-notebooks.py script.  It takes several optional parameters:
* -z: The Zeppelin URL ie http://localhost:8080.  It defaults to localhost:8080
* -n: The directory containing the notebook folders.  It defaults to the directory where this script is located. 
* -d: Flag to indicate you want to delete existing notebooks whose id and/or name matches
* -u: If your zeppelin expects credentials, then this should be the user id
* -p: If your zeppelin expects credentials, then this should be the password

## Importing specific notebooks
Copy the "json" link URL from the table below and paste it into Zeppelin's import from URL tool.

## Adding notebooks
You can add notebooks by making Github pull request, but we request you also update the table below by adding a record for your notebook.

## Notebooks
|Id|Description|Interpreter / Component|Code|Comments|
|-------------|-------------|-----|----------|--------|
|2CTV7H6FU|1.  Getting Started - README|Markup|[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2CTV7H6FU/note.json) | |
|2CTKW7A6U|2.1 Notebook Basics Tutorial|Splicemachine|[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2CTKW7A6U/note.json) | |
|2CUA8V2RK|2.2 Copying to S3 Tutorial|Splicemachine|[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2CUA8V2RK/note.json) | |
|2CSKWGZ8P|2.3 Importing Data Tutorial|Splicemachine|[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2CSKWGZ8P/note.json) | |
|2CU1SNACA|2.4 Running Queries Tutorial|Splicemachine|[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2CU1SNACA/note.json) | |
|2CS27TE2A|2.5 Tuning for Performance Tutorial|Splicemachine|[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2CS27TE2A/note.json) | |
|2CVPHXRZN|2.6 Using the Database Console UI Tutorial|Splicemachine / SparkUI|[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2CVPHXRZN/note.json) | |
|2CU4BJJDS|2.7 Explaining and Hinting Tutorial|Splicemachine|[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2CU4BJJDS/note.json) | |
|2CFY9Q6NS|2.8 TPCH-1 Tutorial|Splicemachine|[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2CFY9Q6NS/note.json) | |
|2CFMYDAYJ|2.9 Common Utilities|Splicemachine|[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2CFMYDAYJ/note.json) | |
|2D76NPKV6|3. Splice Deep Dive / 1. Introduction|Splicemachine|[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2D76NPKV6/note.json) | |
|2D6ZFHE9U|3. Splice Deep Dive / 2. The Life of a Query|Splicemachine|[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2D6ZFHE9U/note.json) | |
|2D93Y56QJ|3. Splice Deep Dive / 3. Monitoring Queries|Splicemachine / SparkUI|[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2D93Y56QJ/note.json) | |
|2D9M6ZUAW|3. Splice Deep Dive / 4. Visualizing Results with Zeppelin|Splicemachine|[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2D9M6ZUAW/note.json) | |
|2D89MQA89|3. Splice Deep Dive / 5. Transactions with Spark & JDBC|Splicemachine|[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2D89MQA89/note.json) | |
|2D8PMSAPJ|3. Splice Deep Dive / 6. Creating Applications|Splicemachine Interpreter|[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2D8PMSAPJ/note.json) | |
|2D96GBY2P|3. Splice Deep Dive / 7. Using our Spark Adapter|Splicemachine / Spark Python|[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2D96GBY2P/note.json) | |
|2DFY9ZKYB|3. Splice Deep Dive / 8. Python MLlib example|Splicemachine / Spark Python |[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2DFY9ZKYB/note.json) | |
|2D7P8BMMS|3. Splice Deep Dive / 9. Scala MLlib example|Splicemachine / Scala / Spark|[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2D7P8BMMS/note.json) | |
|2CD73PAF8|4. Data Engineering / 1. ETL Pipeline Example|Spark|[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2CD73PAF8/note.json) | |
|2CKKJKSK8|5. Reference Applications / 1. Supply Chain - Predicting Shortages|Splicemachine / Spark|[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2CKKJKSK8/note.json) | |
|2CH931JT4|5. Reference Applications / 2. IoT / 1. Overview| |[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2CH931JT4/note.json) | |
|2CHVYSK7B|5. Reference Applications / 2. IoT / 2. Database Setup| |[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2CHVYSK7B/note.json) | |
|2CG53XQM7|5. Reference Applications / 2. IoT / 3. Kafka| |[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2CG53XQM7/note.json) | |
|2CGVRH6SF|5. Reference Applications / 2. IoT / 4.SparkStream| |[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2CGVRH6SF/note.json) | |
|2CG6KVZJ2|5. Reference Applications / 2. IoT / 5. Splice Query| |[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2CG6KVZJ2/note.json) | |
|2D2RM85JF|6. Advanced Tutorials / 1. Creating Custom Stored Procedures| |[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2D2RM85JF/note.json) | |
|2CSGDX1CW|7. Benchmarks / 1. TPCH-100| |[json](https://github.com/splicemachine/zeppelin-notebooks/raw/master/2CSGDX1CW/note.json) | |

## Updating your HDP Zeppelin to use the Splice Machine Native Spark Datasource
* Create a directory such as /tmp/splicemachine on each server to store 1 jar files needed by this setup.
* Get the Splice Machine Native Spark Datasource for HDP for the version you are using ie (splicemachine-hdp2.6.3-2.2.0.2.6.3.0-235_2.11-2.7.0.1828.jar) for your cluster and place it in the /tmp/splicemachine directory on each server
* Copy the configure-spark-interpreter.py from the zeppelin-notebook repo to a server that is running hortonworks and run the following command where:
** The z parameter is the zeppelin server url - update the server and port to match your environment.
** The a parameter is HDP
** The s parameter is the directory from the step above
** The v parameter is the version of zeppelin
** The u parameter is the user if your zeppelin expects credentials
** The p parameter is the password if your zeppelin expects credentials
** The i parameter is the name of the Native Spark Datasource jar
* Run a command like the following to configure your HDP Zeppelin

```
python configure-spark-interpreter.py -z "http://localhost:9995" -a "HDP" -s "/tmp/zeppelin" -v "0.7.3" -u admin -p admin -i splicemachine-hdp2.6.3-2.2.0.2.6.3.0-235_2.11-2.7.0.1828.jar
```
