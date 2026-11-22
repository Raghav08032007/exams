"""
Flask extensions — JWT and CORS only.
SQLAlchemy and Flask-Migrate have been removed; database access is
handled directly via PyMySQL in app/db.py.
"""
from flask_jwt_extended import JWTManager
from flask_cors import CORS

jwt  = JWTManager()
cors = CORS()
