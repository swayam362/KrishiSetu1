import os
import sys

# Ensure project root is in Python sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

from backend.config import Config
from backend.database import get_db
from backend.routes.auth_routes import auth_bp
from backend.routes.product_routes import product_bp
from backend.routes.order_routes import order_bp
from backend.routes.message_routes import message_bp
from backend.routes.review_routes import review_bp
from backend.routes.ai_routes import ai_bp
from backend.routes.smart_selling_routes import smart_selling_bp
from backend.routes.admin_routes import admin_bp

def create_app():
    app = Flask(
        __name__,
        static_folder=Config.FRONTEND_DIR,
        static_url_path=""
    )
    app.config.from_object(Config)
    
    # Enable CORS for cross-origin API integration
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register API Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(message_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(smart_selling_bp)
    app.register_blueprint(admin_bp)
    
    # Root & Static Page Routes
    @app.route("/")
    def index():
        return send_from_directory(Config.FRONTEND_DIR, "index.html")

    # Secure Uploads Serving
    @app.route("/uploads/<path:filename>")
    def serve_uploaded_file(filename):
        safe_path = os.path.normpath(os.path.join(Config.UPLOAD_FOLDER, filename))
        if not safe_path.startswith(Config.UPLOAD_FOLDER):
            return jsonify({"error": "Forbidden"}), 403
        
        dir_name = os.path.dirname(safe_path)
        base_name = os.path.basename(safe_path)
        if os.path.exists(safe_path) and os.path.isfile(safe_path):
            return send_from_directory(dir_name, base_name)
        return jsonify({"error": "File not found"}), 404

    @app.route("/<path:filename>")
    def serve_frontend_pages(filename):
        # Prevent path traversal
        safe_path = os.path.normpath(os.path.join(Config.FRONTEND_DIR, filename))
        if not safe_path.startswith(Config.FRONTEND_DIR):
            return jsonify({"error": "Forbidden"}), 403
            
        if os.path.exists(safe_path) and os.path.isfile(safe_path):
            return send_from_directory(Config.FRONTEND_DIR, filename)
        
        # HTML fallback if filename has no extension
        if not os.path.splitext(filename)[1]:
            html_candidate = safe_path + ".html"
            if os.path.exists(html_candidate):
                return send_from_directory(Config.FRONTEND_DIR, filename + ".html")
                
        return send_from_directory(Config.FRONTEND_DIR, "index.html")

    # Production Security Headers
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        if not Config.DEBUG:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    # Safe Global Error Handlers (Zero Stack Trace Leaks)
    @app.errorhandler(400)
    def handle_bad_request(e):
        return jsonify({"success": False, "error": "Bad request. Please verify your input parameters."}), 400

    @app.errorhandler(401)
    def handle_unauthorized(e):
        return jsonify({"success": False, "error": "Authentication required. Invalid or missing credentials."}), 401

    @app.errorhandler(403)
    def handle_forbidden(e):
        return jsonify({"success": False, "error": "Access forbidden. Insufficient permissions."}), 403

    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({"success": False, "error": "The requested resource could not be found."}), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        return jsonify({"success": False, "error": "Method not allowed on this endpoint."}), 405

    @app.errorhandler(413)
    def handle_payload_too_large(e):
        return jsonify({"success": False, "error": "Uploaded file or payload exceeds maximum allowable size (16MB)."}), 413

    @app.errorhandler(500)
    def handle_internal_error(e):
        # Log generic error on server without leaking details to client
        return jsonify({"success": False, "error": "An internal server error occurred. Please try again later."}), 500

    # API Healthcheck
    @app.route("/api/health", methods=["GET"])
    def health_check():
        db_health = get_db().check_health()
        is_healthy = db_health.get("connected", False)
        return jsonify({
            "status": "healthy" if is_healthy else "degraded",
            "backend": "running",
            "database": {
                "status": db_health.get("status", "disconnected"),
                "healthy": is_healthy
            },
            "app": "KrushiSetu Backend",
            "version": "1.0.0",
            "environment": "development" if Config.DEBUG else "production",
            "security_features": {
                "jwt_auth": True,
                "bcrypt_passwords": True,
                "data_minimization": True,
                "input_sanitization": True,
                "admin_authorization": True
            }
        }), 200 if is_healthy else 503

    return app

if __name__ == "__main__":
    app = create_app()
    print("=" * 60)
    print("KRUSHISETU - Smart Farming Marketplace")
    print("Server running on: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
