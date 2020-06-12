import time
import datetime
import random
import redis

# r = redis.StrictRedis('192.168.0.213', 8001, 12, None, True, 3)
# output = r.blpop('robot_cruise_detect_list_GONGWK12652_13851')
# print(output)
a = [(1, 2), (5, 8)]
# for i, val in enumerate(a) :
#     a +=[4,]
for i in a:
    print(i)
    i += (4,)
print(a)