import sqlite3

class Database(object):
  """This saves incoming EyeTracking data to a Sqlite3 database.
     """

  _insert = "INSERT INTO data VALUES (?, ?, ?, ?)"

  def __init__(self, index, db=":memory"):
    self._queue   = list()
    self._index   = index
    self._connect = sqlite3.connect(db)
    self._cursor  = self._connect.cursor()
    self._cursor.execute("CREATE TABLE IF NOT EXISTS data (time INT PRIMARY KEY, id TEXT NOT NULL, x REAL NOT NULL, y REAL NOT NULL)")
    self._connect.commit()

  def __setitem__(self, key, value):
    self._queue.append((key,self._index,) + value) #FIXME, untested code with index

  def generate(self):
    self._cursor.executemany(Database._insert, self._queue)
    self._connect.commit()
    self._queue = list()
