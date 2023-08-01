### API Trips (flask, swagger, sqlite3)
 API creation using swagger for UI, flask for backend and sqlite3 for storing

## Requirements
Python 3.5.2+

## Running in local
To run the server, please execute the following from the root directory:

```bash
# install libraries
pip3 install -r requirements.txt

# run app
python3 main.py
```
and open your browser to here:

```
http://127.0.0.1:9091/apidocs/
```
First run the route /ingest-data to populate the tables

## Running with Docker

To run the server on a Docker container, please execute the following from the root directory:

```bash
# building the image
docker build -t api_trips .

# starting up a container
docker run -p 9091:9091 api_trips
```
and open your browser to here:

```
http://127.0.0.1:9091/apidocs/
```
First run the route /ingest-data to populate the tables

## Test performance

100 records
```
  "execution_time": 0.015006303787231445,
  "total_items": 100,
  "total_pages": 10
```
10000 records
```
  "execution_time": 0.035006303787231445,
  "total_items": 1000,
  "total_pages": 100
```
1M records
```
  "execution_time": 0.115006303787231445,
  "total_items": 1000000,
  "total_pages": 10000
```
## Structure Folder
```
├───api
│   ├───common          -> funtions to be used in general
│   └───controllers     -> routes for the api with their logics
├───create_database     -> fucntions for model and database
├───data_source         -> file input
├───etl_process         -> functions to transform data
├───sql_scripts         -> bonus
├───swagger_ui          -> json file Swagger desing
├───database.db         -> database created
├───Dockerfile          -> configurations for dockerfile
├───requirements.txt    -> libreries used
└───main.py             -> run app
```