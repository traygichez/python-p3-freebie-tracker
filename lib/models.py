from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, MetaData
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

convention = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}
metadata = MetaData(naming_convention=convention)

Base = declarative_base(metadata=metadata)
engine = create_engine('sqlite:///:memory:', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer(), primary_key=True)
    name = Column(String())
    founding_year = Column(Integer())
    
    devs = relationship('Dev', back_populates='company', cascade="all, delete-orphan")
    freebies = relationship('Freebie', back_populates='company', cascade="all, delete-orphan")

    def give_freebie(self, dev, item_name, value):
        freebie = Freebie(item_name=item_name, value=value, dev=dev)
        self.freebies.append(freebie)
        session.commit()

    @classmethod
    def oldest_company(cls):
        return session.query(cls).order_by(cls.founding_year).first()

    def __repr__(self):
        return f'<Company {self.name}>'


class Dev(Base):
    __tablename__ = 'devs'

    id = Column(Integer(), primary_key=True)
    name = Column(String())
    companies = relationship('Company', back_populates='devs', secondary='freebies')
    freebies = relationship('Freebie', back_populates='dev', cascade="all, delete-orphan")

    def received_one(self, item_name):
        return any(freebie.item_name == item_name for freebie in self.freebies)

    def give_away(self, other_dev, freebie):
        if freebie.dev == self:
            freebie.dev = other_dev
            session.commit()

    def __repr__(self):
        return f'<Dev {self.name}>'


class Freebie(Base):
    __tablename__ = 'freebies'

    id = Column(Integer(), primary_key=True)
    item_name = Column(String())
    value = Column(Integer())
    
    dev_id = Column(Integer(), ForeignKey('devs.id'))
    dev = relationship('Dev', back_populates='freebies')
    
    company_id = Column(Integer(), ForeignKey('companies.id'))
    company = relationship('Company', back_populates='freebies')

    def print_details(self):
        return f'{self.dev.name} owns a {self.item_name} from {self.company.name}'

    def __repr__(self):
        return f'<Freebie {self.item_name}>'

Base.metadata.create_all(engine)
