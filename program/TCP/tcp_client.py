'''
@Author: lijun
@Date: 2020-06-10 14:26:12
@LastEditors: lijun
@LastEditTime: 2020-06-10 15:23:32
@Description: file content
'''
import socket
client = socket.socket(socket.AF_INET,type=socket.SOCK_STREAM)
send_data  =b'hello lj'
client.connect(('192.168.0.190',6666))
client.send(send_data)
return_data,address = client.recvfrom(1024)
print('client >> {} {}'.format(len(return_data),return_data.decode('utf-8')))
client.close()