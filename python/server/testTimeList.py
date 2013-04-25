import TimeList
import random
from datetime, timedelta import datetime

def randList(n):
  nu = datetime.now()
  for i in range(n):
    yield nu + timedelta(sec=randdom.randint)

a = randList(20)

tl = TimeList.TimeList()
