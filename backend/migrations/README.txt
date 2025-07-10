This folder is for Alembic or Flask-Migrate migration scripts. If you use Flask-Migrate, run:

flask db init
flask db migrate -m "multi-tenant support"
flask db upgrade

Or, if you want to manually reset the DB, you can drop and recreate tables using the updated models.
