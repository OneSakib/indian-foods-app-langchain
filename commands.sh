# Run makemigratiosn
alembic revision --autogenerate -m "Add created_at to session"
# Migrate the database
alembic upgrade head