import TimeList
import random
import datetime
tl = TimeList.TimeList()

for i in range(20):
  tl[datetime.datetime.now()] = (i,i)
  #tl[random.randint(0,10)] = (i,i)
  #print(tl) 

for t in tl:
  print(t)
