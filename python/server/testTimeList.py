from TimeList import TimeList
from datetime import datetime, timedelta
import random

def randList(n, a, b):
  nu = datetime.now()
  for i in range(n):
    yield i, i, nu + timedelta(seconds=random.randint(a,b))

randGen  = randList(1000,0,200)

tl = TimeList()

for x, y, ts in randGen:
  tl[ts] = (x,y)

#for t in tl:
# print t

for t in tl[datetime.now()+timedelta(seconds=60):datetime.now()+timedelta(seconds=120)]:
  print t
