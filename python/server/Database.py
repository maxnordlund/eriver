import sqlite3

class Database(object):
  """This saves incoming EyeTracking data to a Sqlite3 database.
     """

  _insert = "INSERT INTO data (?, ?, ?)"

  def __init__(self, db=":memory"):
    self._connect = sqlite3.connect(db)
    self._cursor  = self._connect.cursor()
    self._cursor.execute("CREATE TABLE IF NOT EXISTS data (time INT PRIMARY KEY, x REAL NOT NULL, y REAL NOT NULL)")

  def __setitem__(self, key, value):
    self._cursor.execute(Database._insert, (key,) + value)

  def generate(self):
    pass
