'''
@Author: lijun
@Date: 2020-06-09 17:51:55
@LastEditors: lijun
@LastEditTime: 2020-06-10 14:59:30
@Description: file content
'''
import socket
server = socket.socket(type=socket.SOCK_DGRAM)
server.bind(('192.168.0.190',6666))
print('服务已经开启，等待被连接...')
data,address = server.recvfrom(1024)
with open('data.txt','wb') as f:
    f.write(data)
# f.close()
print('server>>{} {}'.format(len(data),data))
print('客户端连接的socket地址：',address)
server.sendto(b'drink more water!',address)
# server.close()