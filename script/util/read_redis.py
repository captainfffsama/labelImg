'''
@Author: lijun
@Date: 2020-05-18 18:42:26
@LastEditors: lijun
@LastEditTime: 2020-05-20 16:56:05
@Description: file content
'''
import redis
class Redis(object):
    """[summary]

    Args:
        object ([type]): [description]
    """    
    def __init__(self):
        pass
    def read_redis(self, host:'str',port:'str',db:'str'):
        """[summary]

        Args:
            host ([str]): [this is redis ip]
            port ([str]): [this is redis port]
            db ([str]): [this is redis db]

        Returns:
            [type]: [return redis ]
        """        
        pool = redis.ConnectionPool(host=host,port=port,db=db)
        r = redis.Redis(connection_pool=pool)
        return r
    
    def ana_redis(self,redis_data,key_info:'str'):
        """[summary]

        Args:
            redis_data ([type]): [this is redis]
            key_info ([str]): [this is redis file name,such as image,crupt_info ie.]

        Returns:
            [list]: [this is file's name ]
        """        
        infos = sorted(redis_data.keys(key_info))
        return infos

    def ana_all_redis(self,redis_data,key_info:'str'):
        """[summary]

        Args:
            redis_data ([type]): [this is redis]
            key_info ([str]): [this is redis file name,such as image,crupt_info ie.]

        Returns:
            [list]: [return a map contians key and value]
        """        
        info_datas = []
        infos = sorted(redis_data.keys(key_info))
        for info in infos:
            key_datas = redis_data.hgetall(info)
            info_datas.append(key_datas)
        return info_datas

if __name__ == "__main__":
    host = 'localhost'
    port = 8001
    db = 7
    key_info = 'image:*'
    redis_ = Redis()
    redis_data = redis_.read_redis(host,port,db)
    infos = redis_.ana_redis(redis_data,key_info)
    #key_datas = redis_.ana_redis(redis_data,key_info)
    #print(key_data)
    #for key_data in key_datas:
    #    print(key_data)
    for info in infos:
        key_datas = redis_data.hgetall(info)
        for key,value in key_datas.items():
            key_data = key.decode('gbk')
            value_data = value.decode('gbk')
            key_data = int(key_data)+476106
            print(key_data,value_data)
            redis_data.hset(info,key_data,value_data)
