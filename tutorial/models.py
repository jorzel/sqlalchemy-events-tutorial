from xml.dom.domreg import registered
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    MetaData,
    create_engine,
)
from sqlalchemy.orm import (
    configure_mappers,
    declarative_base,
    relationship,
    sessionmaker,
)
from contextlib import contextmanager

DB_URI = "sqlite://"

engine = create_engine(DB_URI)
metadata = MetaData()
Base = declarative_base(metadata=metadata)


@contextmanager
def transaction_scope(session):
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise


def get_session(bind):
    Session = sessionmaker(bind)
    return Session()


def add_user(session) -> int:
    with transaction_scope(session):
        user = User(name="Test", username="test", password="secret")
        session.add(user)
        session.flush()
    return user.id


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    username = Column(String(128), unique=True, nullable=False)
    password = Column(String(128), nullable=False)

    def __str__(self):
        return f"User(id={self.id}, username={self.username})"

    __repr__ = __str__


class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User")

    registered_at = Column(DateTime(timezone=True), nullable=False)
    quantity = Column(Integer(), default=0)
    value = Column(Float(), default=0.0)

    def __str__(self):
        return f"Transaction(id={self.id}, user_id={self.user_id}, quantity={self.quantity}, value={self.value}, registerd_at={self.registered_at})"

    __repr__ = __str__


class Holding(Base):
    __tablename__ = "holding"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User")

    registered_at = Column(DateTime(timezone=True), nullable=False)
    value = Column(Float(), default=0.0)

    def __str__(self):
        return f"Holding(id={self.id}, user_id={self.user_id}, value={self.value}, registerd_at={self.registered_at})"

    __repr__ = __str__

    @classmethod
    def create(cls, transaction: Transaction) -> "Holding":
        return Holding(
            user_id=transaction.user_id,
            value=transaction.value * transaction.quantity,
            registered_at=transaction.registered_at,
        )


configure_mappers()

metadata.drop_all(engine)
metadata.create_all(engine)
