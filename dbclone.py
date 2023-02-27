import logging

from hdx.database import Database
from hdx.freshness.database.dbdataset import DBDataset
from hdx.freshness.database.dbresource import DBResource
from hdx.freshness.database.dbrun import DBRun

logger = logging.getLogger(__name__)


class DBClone:
    # Clone database but limit to 5 datasets per run
    def __init__(self, session):
        self.session = session

    def clone(self, params={"dialect": "sqlite", "database": "freshness.db"}):
        with Database(**params) as clone_session:
            run_numbers = self.session.query(DBRun).all()
            for run_number in run_numbers:
                clone_session.merge(run_number)
                run_no = run_number.run_number
                logger.info(f"Adding run {run_no}")
                dbdataset = self.session.query(DBDataset).filter_by(run_number=run_no).first()
                if not dbdataset:
                    logger.info(f"No datasets in run {run_no}")
                    continue
                clone_session.merge(dbdataset)
                dbresources = (
                    self.session.query(DBResource)
                    .filter_by(run_number=run_no, dataset_id=dbdataset.id)
                )
                for dbresource in dbresources:
                    clone_session.merge(dbresource)
                clone_session.commit()
