from flask import Flask
from flasgger import Swagger
from api.controllers.ingestion_controller import ingestion_bp
from api.controllers.trip_controller import trip_bp
from api.controllers.analitycs_controller import analitycs_bp

def main():
    app = Flask(__name__)
    swagger = Swagger(app, template_file='swagger_ui/swagger.json')
    app.register_blueprint(ingestion_bp)
    app.register_blueprint(trip_bp)
    app.register_blueprint(analitycs_bp)
    app.run('0.0.0.0',port = 9091)

if __name__ == '__main__':
    main()