### API Trips (flask, swagger, sqlite3)
 API creation using swagger for UI, flask for backend and sqlite3 for storing

## Requirements
Python 3.5.2+

## Running in local
To run the server, please execute the following from the root directory:

```
pip3 install -r requirements.txt
python3 main.py
```
and open your browser to here:

```
http://127.0.0.1:9091/apidocs/
```

## Running with Docker

To run the server on a Docker container, please execute the following from the root directory:

```bash
# building the image
docker build -t api_trips .

# starting up a container
docker run -p 9091:9091 api_trips
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