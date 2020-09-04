from .api import app, db_drop_and_create_all

with app.app_context(): db_drop_and_create_all()
