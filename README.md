# deviceShare

device B, which connect android devices
device A, which want to connect android devices plus on device B.

set host name in config

in device B
```shell
python main.py
```

device A
```shell
python server_callback.py
```

and then get IP of device B.   
visit http://IP:http_port , you can see devices on device B.  
adb connect it 

```shell
adb connect IP:port
```
