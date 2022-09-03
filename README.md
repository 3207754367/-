# 湖北工程职业学院 智慧校园 自动健康上报

## 这个脚本是用来干什么?
  答: 因为疫情的原因，学校要求我们每日上报自己的健康和体温状态，懒惰是第一生产力嘛，所以就有了这个脚本
## 运行环境
 - python3
## 如何使用?
 
 ``` python
 git clone https://github.com/sbmatch/zhihuixiaoyuan
 cd zhihuixiaoyuan
 pip install -r requirements.txt
 ```

除此之外，你还需要编辑`config.json`文件输入(studentID)学号，（password）智慧校园登录密码

以及前往百度智能云平台创建一个应用，传送门: [百度智能云](https://console.bce.baidu.com/ai/#/ai/speech/app/create)

应用类型选择 [文字识别] --> [通用文字识别(标准版)] 即可

创建完成后将获取到的 `AppID`  `ApiKey` `SecretKey` 填入`config.json` 配置文件中

在国家网站查找省市县的行政区划代码 [传送门](http://xzqh.mca.gov.cn/defaultQuery?shengji=%BA%FE%B1%B1%CA%A1%A3%A8%B6%F5%A3%A9&diji=-1&xianji=-1) 
并将其填入`config.json` 配置文件中

最后：`python start.py --c config.json`

## 如何定时运行?
 答: 通过linux端可通过`crontab`工具实现每日自动运行,windowns端可以通过创建计划任务实现
