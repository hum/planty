import psycopg2

from psycopg2 import pool
from urllib.parse import urlparse
from contextlib import contextmanager

class Db:
  def __init__(self):
    self.pool = None

  @contextmanager
  def _get_conn(self):
    con = self.pool.getconn()
    cur = con.cursor()
    try:
      yield con, cur
    finally:
      cur.close()
      self.pool.putconn(con)
  
  @classmethod
  async def create_pool(self, _min: int, _max: int, conf: str):
    if conf is None:
      return None

    config = urlparse(conf) 
    pool = psycopg2.pool.SimpleConnectionPool(
              _min, 
              _max, 
              user = config.username,
              password = config.password,
              host = config.hostname,
              port = config.port,
              database = config.path[1:]
            )

    return pool


  # TODO:
  # Proper select/insert funcs, because this is a terrible way to do it
  def select_query(self, query: str):
    with self._get_conn() as (conn, cursor):
      cursor.execute(query) 
      result_set = cursor.fetchall()

      if len(result_set) > 0:
        conn.commit()
        return result_set
      else:
        conn.rollback()
        return None

  def insert_query(self, query: str):
    row_id = -1

    with self._get_conn() as (conn, cursor):
      cursor.execute(query) 
      row_id = cursor.fetchone()

      if cursor.rowcount == 1:
        conn.commit()
      else:
        conn.rollback()
    return row_id
