import redis
from enum import Enum, unique
import time
import datetime
import threading
from abc import ABCMeta, abstractmethod
import json
import os
import socket
import random


@unique
class DB_INDEX_FUNC(Enum):
    STM32_DB = 0
    CBV7700_ServiceCall_DB = 12
    CBV7700_PARA_DB = 13

    def __int__(self):
        return self.value


@unique
class DB_PORT(Enum):
    DEFAULT_DB_PORT = 8001

    def __int__(self):
        return self.value

message_list = []


def MsgHandle(message):
    message_list.append(message)


class ServiceProvider(object):
    def __init__(self):
        pass

    def setServiceFuncNames(self, *args, ip='localhost'):
        self.r = redis.StrictRedis(host=ip, port=int(DB_PORT.DEFAULT_DB_PORT),
                                   db=int(DB_INDEX_FUNC.CBV7700_ServiceCall_DB),
                                   password=None,
                                   socket_keepalive=True, max_connections=3)
        self.sub = self.r.pubsub()
        dict = {}
        for arg in args:
            dict[arg] = MsgHandle
        self.sub.subscribe(**dict)
        conn = self.sub.get_message(timeout=2)
        if conn is None:
            print('subscribe failed!')
            return None
        thread = self.sub.run_in_thread(sleep_time=1)
        return thread

    @abstractmethod
    def doServiceLogic(self, channel, input, output):
        print("parent logic")

    def consume(self):
        while True:
            time.sleep(0.05)
            if len(message_list) > 0:
                msg = message_list.pop(0)
                input = json.loads(str(msg['data'], encoding='utf8'), encoding='utf-8')
                print(input)
                output = {'ret':0}
                ServiceRequireReturn = input['ServiceRequireReturn']
                input.pop('ServiceRequireReturn')
                ServiceCallTime = input['ServiceCallTime']
                input.pop('ServiceCallTime')
                ServiceCallPid = input['ServiceCallPid']
                input.pop('ServiceCallPid')
                UseJson = input['UseJson']
                input.pop('UseJson')
                self.doServiceLogic(str(msg['channel'], 'utf8'), input, output)
                retListName = str(msg['channel'], 'utf8') + '_list_' + ServiceCallPid
                output['ServiceCallTime'] = ServiceCallTime
                if ServiceRequireReturn == '1':
                    rets = json.dumps(output)
                    print(rets)
                    self.r.rpush(retListName, rets)
                    self.r.expire(retListName,time=300)
            else:
                print("waiting...")

class ServiceCall(object) :
    def __init__(self, ip, port = int(DB_PORT.DEFAULT_DB_PORT), passwd = None) :
        self.r = redis.StrictRedis(ip, port, int(DB_INDEX_FUNC.CBV7700_ServiceCall_DB), passwd, True, 3)
    def excute(self, func, input, timeout = 600, require_return = True):
        pid = os.getpid()
        hostname = socket.gethostname()
        random.seed(time.time())
        n = random.randint(0, 65536)
        headinfo = []
        headinfo.append(hostname)
        headinfo.append(str(pid))
        headinfo.append('_')
        headinfo.append(str(n))
        headinfo = ''.join(headinfo)
        if ('ServiceRequireReturn' in input  or 'ServiceCallPid' in input or 'ServiceCallTime' in input):
            print('ServiceRequireReturn/ServiceCallPid/ServiceCallTime is used.')
            return -1, None
        if require_return :
            input['ServiceRequireReturn'] = 1
        else:
            input['ServiceRequireReturn'] = 0
        curtime = datetime.datetime.now().strftime('%H:%M:%S.%f')
        input['ServiceCallPid'] = headinfo
        input['ServiceCallTime'] = curtime
        msg = json.dumps(input)
        ret = self.r.publish(func, msg)
        if ret < 0 :
            print('publish {} failed. '.format(func))
            return ret, None
        lstkey = []
        lstkey.append(func)
        lstkey.append('_list_')
        lstkey.append(headinfo)
        lstkey = ''.join(lstkey)
        while require_return:
            output = self.r.blpop(lstkey, timeout)
            result = json.loads(str(output[1], encoding='utf8'), encoding='utf-8')
            return 0, result