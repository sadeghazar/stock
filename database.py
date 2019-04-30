from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session


class Database:
    engine = None

    def __init__(self):
        self.engine = create_engine("sqlite:///dbase")
        self.Base = declarative_base()

    def add(self, instance):
        session = Session(bind=self.engine)
        try:
            session.add(instance)
            session.commit()
            session.flush()
        except Exception as ex:
            session.rollback()
            session.close()
        finally:
            session.close()
            return instance

    def delete(self, instance):
        session = Session(bind=self.engine)
        try:
            session.delete(instance)
            return session.commit()
        except Exception as ex:
            pass

    def update(self, instance):
        try:
            session = Session(bind=self.engine)
            return session.commit()
        except Exception as ex:
            pass

    def insert_or_update(self,model):
        session = Session(bind=self.engine)
        results = None
        try:
            results = session.merge(model)
            session.commit()
            session.flush()
        except Exception as ex:
            session.rollback()
            session.close()
            pass
        finally:
            return results

    def add_bulk(self, models, return_defaults=False):
        session = Session(bind=self.engine)
        results = None
        try:
            session.bulk_save_objects(models, return_defaults=return_defaults)
            results = session.commit()
            session.flush()
        except Exception as ex:
            session.rollback()
            session.close()
        finally:
            return results

    def call_proc(self, procname, params=None):
        connection = self.engine.raw_connection()
        results = None
        try:
            cursor = connection.cursor()
            if params:
                cursor.callproc(procname, params)
            else:
                cursor.callproc(procname)
            results = list(cursor.fetchall())
            cursor.close()
            connection.commit()
        except Exception as ex:
            pass
        finally:
            connection.close()
        return results
