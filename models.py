from sqlalchemy import Column, ForeignKey, Integer, String
from database import Base

class Lineup(Base):
    __tablename__ = 'lineups'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    map = Column(String(25))
    agent = Column(String(25))

    def __init__(self, name=None, map=None, agent=None):
        self.name = name
        self.map = map
        self.agent = agent

    def __str__(self) -> str:
        return self.name

    def __repr__(self):
        return f'<Lineup {self.name!r}>'

class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    lineup_name = Column(String(50), ForeignKey("lineups.name"))
    path = Column(String(100), unique=True)

    def __init__(self, lineup_name=None, path=None):
        self.lineup_name = lineup_name
        self.path = path

    def __str__(self) -> str:
        return self.path

    def __repr__(self):
        return f'<Lineup {self.path!r}>'