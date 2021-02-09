# Putter.py

## 简介

一款可以通过接收的反弹的shell，来传递文件的工具，支持windows和linux shell

原理很简单，把二进制文件通过base64编码，通过多个输出字符串命令输出到目标文件中，然后通过base64解码命令解码出二进制文件

> 使用前确保linux下有base64命令，以及windows下有certutil命令  
> 大部分系统都会自带

## 示例

监听本地8080端口，接收linux shell(默认)，传递portmap文件  
`python3 putter.py -f portmap -l 0.0.0.0:8080`  

监听本地8080端口，接收windows shell，传递lcx文件  
`python3 putter.py -f lcx -l 0.0.0.0:8080 --os win`  

## 注意事项

如果传输失败，可以通过调节参数--size每次发送的字节数，参数--delay每两次发送shell命令之间的延迟（秒）

传输文件后可自行通过md5校验文件hash，查看是否传输成功

传输完成后在服务端会残留xxx.tmp文件，需要自行删除
