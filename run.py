"""Entry point to start data freshness emailer
"""
import argparse
import logging
from os import getenv
from typing import Optional

from dbclean import DBClean
from dbclone import DBClone
from hdx.database import Database
from hdx.utilities.dateparse import now_utc
from hdx.utilities.dictandlist import args_to_dict
from hdx.utilities.easy_logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def main(
    db_url: Optional[str] = None, db_params: Optional[str] = None, action: str = "clean"
) -> None:
    """Run freshness database cleaner. Either a database connection string (db_url) or database
    connection parameters (db_params) can be supplied. If neither is supplied, a local
    SQLite database with filename "test_freshness.db" is assumed.

    Args:
        db_url (Optional[str]): Database connection string. Defaults to None.
        db_params (Optional[str]): Database connection parameters. Defaults to None.
        action (bool): What action to take. "clone" to copy prod db for testing. Default is clean.

    Returns:
        None
    """

    logger.info(f"> Data freshness database clean 1.0")
    if db_params:  # Get freshness database server details
        params = args_to_dict(db_params)
    elif db_url:
        params = Database.get_params_from_sqlalchemy_url(db_url)
    else:
        params = {"driver": "sqlite", "database": "test_freshness.db"}
    logger.info(f"> Database parameters: {params}")
    with Database(**params) as session:
        now = now_utc()
        if action == "clean":
            cleaner = DBClean(session, now)
            cleaner.clean()
            logger.info("Freshness database clean completed!")
        elif action == "clone":
            cloner = DBClone(session)
            cloner.clone()
            logger.info("Freshness database clone completed!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data Freshness Database Clean")
    parser.add_argument(
        "-db", "--db_url", default=None, help="Database connection string"
    )
    parser.add_argument(
        "-dp",
        "--db_params",
        default=None,
        help="Database connection parameters. Overrides --db_url.",
    )
    parser.add_argument(
        "-a",
        "--action",
        default="clean",
        help="Action to perform.",
    )
    args = parser.parse_args()
    db_url = args.db_url
    if db_url is None:
        db_url = getenv("DB_URL")
    if db_url and "://" not in db_url:
        db_url = f"postgresql://{db_url}"
    main(
        db_url=db_url,
        db_params=args.db_params,
        action=args.action,
    )
