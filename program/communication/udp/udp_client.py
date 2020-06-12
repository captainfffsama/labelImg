'''
@Author: lijun
@Date: 2020-06-09 17:58:23
@LastEditors: lijun
@LastEditTime: 2020-06-09 18:01:09
@Description: file content
'''
import socket
client = socket.socket(type=socket.SOCK_DGRAM)
send_data = b'hello lj'
client.sendto(send_data,('192.168.0.190',6666))
return_data,address = client.recvfrom(1024)
print('client>>{} {}'.format(len(return_data),return_data.decode('utf-8')))
client.close()