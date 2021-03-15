# https://wtforms-alchemy.readthedocs.io/en/latest/introduction.html#installation

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///:memory:')
Base = declarative_base(engine)
db_session = sessionmaker(bind=engine)


class Project(Base):
    __tablename__ = 'project'

    id = sa.Column(sa.BigInteger, autoincrement=True, primary_key=True)
    name = sa.Column(sa.Unicode(100), nullable=False)
    description = sa.Column(sa.Unicode(255), nullable=False)
