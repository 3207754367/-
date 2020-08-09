# 自动上报学校规定的那该死的健康和体温

## 这个脚本是用来干什么?
  答: 因为疫情的原因，学校要求我们每日上报自己的健康和体温状态，懒惰是第一生产力嘛，所以就有了这个脚本
## 运行环境
 - Linux
 - python3
 - tesseract
## 如何使用?
 答:  克隆项目到你的设备中, 进入文件夹,运行`pip install -r requirements.txt` 安装`requirements.txt` 中的依赖库 ，命令行输入`sudo apt install tesseract -y` 安装`tesseract` ，依赖库安装完成后修改`start.py`文件，将学号和密码修改成自己的即可

``` python
user,password = '学号', '密码'
```
## 如何定时运行?
 答: 通过linux端的`crontab`工具实现每日自动运行一次，具体的操作请自行百度
