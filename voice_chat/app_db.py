import os
from contextlib import contextmanager

import psycopg2
import json
import decimal
import datetime


class AppDb:
    _conn = None

    @classmethod
    def connect(cls):
        if cls._conn is None or cls._conn.closed:
            print("Connecting to database")
            cls._conn = psycopg2.connect(
                host=os.environ.get("DB_HOST"),
                port=os.environ.get("DB_PORT"),
                database=os.environ.get("DB_NAME"),
                user=os.environ.get("DB_USER"),
                password=os.environ.get("DB_PASS"),
            )
            cls._conn.autocommit = True

    @classmethod
    def close_connection(cls):
        if cls._conn:
            cls._conn.close()
            cls._conn = None
        print("Closed proxy connection")

    @classmethod
    @contextmanager
    def get_cursor(cls):
        if cls._conn is None or cls._conn.closed:
            cls.connect()
        try:
            with cls._conn.cursor() as cur:
                yield cur
        except psycopg2.OperationalError:
            print("Connection lost, reconnecting...")
            cls.connect()
            with cls._conn.cursor() as cur:
                yield cur

    @classmethod
    def json_serializer(_, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    @classmethod
    def exec_query(cls, query):
        query = query.replace("\n", " ")
        print("Start exec_query")
        with cls.get_cursor() as cur:
            # todo:
            cur.execute(query)
            res = cur.fetchall()

        print("Finished exec_query")
        
        columns = [desc[0] for desc in cur.description]
        data = [dict(zip(columns, row)) for row in res]

        json_string = json.dumps(data, default=cls.json_serializer, indent=4)

        return json_string

    @classmethod
    def load_session(cls, user_id: str) -> dict:
        cls.connect()
        with cls.get_cursor() as cur:
            cur.execute("SELECT session_state FROM session_state WHERE user_id = %s", (user_id,))
            row = cur.fetchone()
            if row:
                return row[0]
            return {'messages': []}
        
    @classmethod
    def save_session(cls, user_id: str, state: dict):
        cls.connect()
        with cls.get_cursor() as cur:
            cur.execute("""
                INSERT INTO session_state (user_id, session_state)
                VALUES (%s, %s)
                ON CONFLICT (user_id)
                DO UPDATE SET session_state = EXCLUDED.session_state;
            """, (user_id, json.dumps(state)))
