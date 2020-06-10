'''
@Author: lijun
@Date: 2020-06-10 14:26:29
@LastEditors: lijun
@LastEditTime: 2020-06-10 15:30:40
@Description: file content
'''
import socket
server = socket.socket(socket.AF_INET,type=socket.SOCK_STREAM)
server.bind(('192.168.0.190',6666))
server.listen(5)
print('服务已开启，等待被连接.....')
#!此处接收客户端连接，返回地址信息和端口
client,client_address = server.accept()
receive_data = client.recv(1024)
print('server >> {} {} '.format(len(receive_data),receive_data))
print('客户端连接的sockt地址：',client_address)
client.send(b'thisisserver')
client.close()
# server.shutdown()
server.close()