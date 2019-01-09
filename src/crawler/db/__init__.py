import os
import shutil

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# ----------------------------------------------------------------------------

# create sqlite database
if os.environ.get('DATABASE_URL') is None:
  engine = create_engine('sqlite:////tmp/gwas.sql', convert_unicode=True)
else:
  engine = create_engine(os.environ['DATABASE_URL'], convert_unicode=True)

# create folder to store papers
if os.environ.get('DATABASE_FILE_DIR') is None:
  db_dir = '/tmp/gwaskb/'
else:
  db_dir = os.environ.get('DATABASE_FILE_DIR') + '/'
if os.path.exists(db_dir):
  shutil.rmtree(db_dir)
db_dir = os.makedirs(db_dir)

# create session to database
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()