from sqlalchemy.orm import declarative_base, Session, relationship
from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.sql import text
Base = declarative_base()


class Clients(Base):
    __tablename__: str = "clients"
    id = Column(Integer, primary_key=True)
    cpf = Column(String(100), nullable=False)
    address = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    birtday = Column(Date, nullable=False)
    accounts = relationship("Accounts", back_populates="clients", cascade="all, delete-orphan")

    def get_clients(self):
        pass

    def create_client(self):
        pass


class Accounts(Base):
    __tablename__: str = "accounts"
    id = Column(Integer, primary_key=True)
    balance = Column(Float, nullable=False)
    number = Column(Integer, nullable=False)
    agency = Column(String(11), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    clients = relationship("Clients", back_populates="accounts")

    def get_accounts(self):
        pass

    def create_account(self):
        pass


engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)

Conn = engine.connect()
data = Conn.execute(text("select * from clients"))

print([result for result in data.fetchall()])