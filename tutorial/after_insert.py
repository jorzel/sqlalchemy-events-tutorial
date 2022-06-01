from sqlalchemy import event
from datetime import datetime
from tutorial.models import Transaction, Holding, transaction_scope, engine, add_user, get_session





@event.listens_for(Transaction, "after_insert")
def receive_after_insert(mapper, connection, target):
    print('Event handling')
    with get_session(connection) as session:
        with transaction_scope(session):
            holding = Holding.create(target)
            session.add(holding)



def tutorial_after_insert(with_raise=False):
    with get_session(engine) as session:
        user_id = add_user(session)
        with transaction_scope(session):
            transaction = Transaction(
                quantity=10,
                value=11.2,
                user_id=user_id,
                registered_at=datetime.utcnow(),
            )
            session.add(transaction)
            session.flush()  # after that event should be handled
            if with_raise:
                raise Exception("Exception")


try:
    tutorial_after_insert(True)
except Exception as e:
    print(e)
finally:
    with get_session(engine) as session:
        print(session.query(Holding).all())
        print(session.query(Transaction).all())
