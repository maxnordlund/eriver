import sqlite3

class Database(object):
  """This saves incoming EyeTracking data to a Sqlite3 database.
     """

  _insert = "INSERT INTO data (?, ?, ?)"

  def __init__(self, db=":memory"):
    self._queue   = list()
    self._connect = sqlite3.connect(db)
    self._cursor  = self._connect.cursor()
    self._cursor.execute("CREATE TABLE IF NOT EXISTS data (time INT PRIMARY KEY, x REAL NOT NULL, y REAL NOT NULL)")

  def __setitem__(self, key, value):
    self._queue.append((key,) + value)

  def generate(self):
    self._cursor.executemany(Database._insert, self._queue)
    self._queue = list()
