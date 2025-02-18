# Excel2Caldav

This project is designed to parse Excel shift schedules, generate the shift information for specific individuals, and then upload it to a CalDav service. Once the CalDav service is configured on the mobile phone, the shift information can be directly viewed in the calendar, making daily work more convenient.

这个项目是用于解析Excel排班表，生成指定人的排班信息，然后上传到CalDav服务中。
手机上配置了CalDav服务后，就可以直接在日历中看到排班信息，方便日常工作。

## 部署CalDav服务
我使用的是radicale作为CalDav服务

可以通过`apt install radicale`安装，也可以使用pip安装

配置文件 `/root/.config/radicale/config`
```
[server]
hosts = 0.0.0.0:5232, [::]:5232
[auth]
type = htpasswd
htpasswd_filename = /root/.config/radicale/passwd
htpasswd_encryption = md5
```
这里的htpasswd用命令生成即可，作为用户名密码登录CalDav

运行命令
```
python3 -m radicale --storage-filesystem-folder=~/radicale/collections
```

通过`netstat -apn | grep 5232`可以看到监听的程序，代表程序正常启动

## 运行脚本
* `config.py`里有基础的一些配置，按需修改
```
caldav_url = 'http://127.0.0.1:5232'
username = 'admin'
password = '123456'
vip_name = 'AAA'
```
* `make_event.py `脚本可以预解析脚本，看下解析的对不对
* `main.py` 脚本用于实际的生成和上传
* `caldav_client.py` 封装了一些方法
* `all_event.py` 可以查询过滤日程，方便做清理