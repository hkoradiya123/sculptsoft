import os
from pathlib import Path
from alembic.config import Config
from alembic import command

# Use PostgreSQL URL provided by the user for autogeneration.
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://postgres:Hkoradiya@localhost/fastapidb'

project_dir = Path(__file__).resolve().parent
cfg = Config(str(project_dir / 'alembic.ini'))

# set absolute script_location and sqlalchemy.url
cfg.set_main_option('script_location', str(project_dir / 'alembic'))
cfg.set_main_option('sqlalchemy.url', os.environ['DATABASE_URL'])

# run autogenerate revision
command.revision(cfg, message='initial', autogenerate=True)
