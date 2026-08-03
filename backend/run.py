"""Flask 后端入口"""
import os
from app import create_app

FLASK_ENV = os.getenv("FLASK_ENV", "development")
app = create_app(config_name=FLASK_ENV)

if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = FLASK_ENV == "development"
    app.run(host=host, port=port, debug=debug)

'''
python run.py
flask run
'''
