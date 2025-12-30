from flask import Flask
from config import Config
from flask_cors import CORS
from middleware import init_middleware
from auth_routes import auth_bp
from kota_routes import kota_bp
from cuaca_routes import cuaca_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # CORS FIX FINAL
    CORS(app,
         resources={r"/*": {"origins": "*"}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    )

    # Middleware JWT
    init_middleware(app)

    # Register routes
    app.register_blueprint(auth_bp)
    app.register_blueprint(kota_bp)
    app.register_blueprint(cuaca_bp)

    # Global response CORS handler
    @app.after_request
    def apply_cors(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, DELETE, OPTIONS"
        return response

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
