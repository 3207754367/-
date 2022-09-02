# -*- coding: utf8 -*-
import requests,json,hashlib,logging,time,smtplib,sys,os
import requests as req
from aip import AipOcr
from PIL import Image
from io import BytesIO
from email.mime.text import MIMEText

########################################################
#          
#                    @湖北工程职院
#
#
#            智慧校园  每日自动上报健康状态
#
#
#   免责声明：本脚本只做学习和交流使用，版权归原作者所有，请在下载后24小时之内自觉删除，若作商业用途，由此发生的任何侵权行为，与作者无关。
#
#########################################################
start_time = time.time()
sess = req.Session()

headers = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36', 'Connection': 'close' }

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', filename=sys.path[0]+"/1.log", filemode='a')

codeurl= "http://api.hbei.com.cn/api/Login/GetCheckCodePic?hashcode=1596828473201" #验证码接口

twApi = "http://wapapi.hbei.com.cn/api/HealthReport/SaveSelfTempValue" #体温接口

jkApi = "http://wapapi.hbei.com.cn/api/HealthReport/SaveYQinfo" #健康状态接口

options = {}
options["language_type"] = "ENG"
options["detect_direction"] = "true"

with open('config.json', 'r', encoding='utf8') as json_file:
    json_data = json.load(json_file)
    user = json_data["studentID"]
    password = json_data["password"]
    baiduocr = json_data["baiduocr"][0]
    AppID = baiduocr["AppID"]
    ApiKey = baiduocr["ApiKey"]
    SecretKey = baiduocr["SecretKey"]
    mail_conf = json_data["mail_conf"][0]
    mail_stmp = mail_conf["stmp地址"]
    mail_from = mail_conf["发件人邮箱"]
    mail_passwd = mail_conf["邮箱授权码"]
    recipient = mail_conf["收件人邮箱"]
    
    


client = AipOcr(AppID,ApiKey,SecretKey)

def passwd_md5(): #将密码进行MD5 32位加密
    md5 = hashlib.md5()
    md5.update(bytes(password,encoding='utf-8'))
    passmd5 = md5.hexdigest()
    return passmd5

def getcodeimage(): #处理验证码图片
    response = sess.get(codeurl,headers=headers) #获取验证码对象
    image = Image.open(BytesIO(response.content))
    image.tell()
    if image.mode == 'P' or image.mode == 'RGBA':
        image = image.convert('RGB')
    return image

def baidu_ocr(): #baidu验证码识别接口 
    img = getcodeimage()
    img.save("a.jpg")
    with open('a.jpg', 'rb') as img_file:
        img2 = client.basicGeneral(img_file.read(),options)
        os.remove(sys.path[0] + '/a.jpg')
    return img2["words_result"][0]["words"] #验证码

# def local_ocr(): #本地识别验证码
#     image = getcodeimage() 
#     try:
#         abcd=pytesseract.image_to_string(image, lang='eng', config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
#     except Exception as e:
#         logging.error(e)
#         print ('识别验证码时出现错误,请查看log --> ' + fileName)
#         requests.get('https://sc.ftqq.com/' + sckey + '.send?text=程序抛出异常:'+ str(e)) #推送异常的原因到service酱
#     return abcd #返回验证码

def getTicket(): #获取ticket密钥
    passmd5 = passwd_md5() #获取加密后的密码
    vcode = baidu_ocr() #获取百度识别的验证码
    post_login = {
        "CheckCode": vcode,"HashCode": "1596828473201","LoginID": user,"Password": passmd5,"LoginWay": "手机WAP" } #登录表单
    try:
        login = sess.post(url='http://api.hbei.com.cn/api/Login/UserLoginValid', data=post_login, headers=headers)
        abc = login.json()
        ticket_data  = str(abc["Ticket"]) #取出Ticket
    except Exception as f:
        logging.error(f)
        print ('获取密钥时出现错误,请查看log --> ' + fileName)
    return ticket_data

def mailsend(title,yq,tv): #发送邮件通知
    mailmg = title + yq  + tv
    message = MIMEText(mailmg, 'plain' , 'utf-8')
    message["From"] = mail_from #谁来发
    message["To"] = "" #发给谁
    message['Subject'] = '智慧校园每日上报'
    try:
        a = smtplib.SMTP() #实例化一个smtp服务
        a.connect(mail_stmp)
        a.login(mail_from,mail_passwd)
        a.sendmail(mail_from, recipient, message.as_string())#发邮件
        print ("已发送邮件通知")
        os.remove(sys.path[0] + '/1.log')
        a.quit() #关闭
    except Exception as k:
        logging.error(k)
        print ('发送邮件时出现错误,请查看log --> ' + fileName)

def start():
    post_data = {
        'ticket': ticket_data,
        'ifhomeaddr': '1',
        'yyqzdm': '00',
        'selfgjdm': '0',
        'familyyq': '0',
        'provincedm': '420000',
        'citydm': '421300',
        'countydm': '421381',
        'lat': '0',
        'lng': '0',
        'addrname': '0',
        'addrnameb': '0',
        'addrcitydm': '0',
        'addrcitymc': '0'
    }
    tempValue = sess.get(url=twApi+'?ticket='+ticket_data+'&tempvalue=36.1', headers=headers).text
    logging.info('上报体温:' + tempValue) #体温上报结果
    saveyqinfo = sess.post(url=jkApi, data=post_data, headers=headers).text
    logging.info('上报健康状态:' + saveyqinfo) #打印健康上报结果
    mailsend("","\n上报健康状态:"+saveyqinfo,"\n上报体温:"+tempValue) #发送邮件通知
    #listAPi = "http://wapapi.hbei.com.cn/api/HealthReport/GetTodaySelfTempList?ticket="+ticket_data
    #deleteItem = "http://wapapi.hbei.com.cn/api/HealthReport/DelSelfTempRecord/"
    #listInfo= sess.get(listAPi).text
    #for i in json.loads(listInfo):
    #    strii = requests.get(deleteItem+i["id"],headers).text
     #   mailsend("已删除于 "+str(i['checktime']) +"上报的体温信息, 返回状态："+strii+" \nID: "+i["id"] +" \n体温: "+str(i["tempvalue"]),"","")
    

def run():
    print ("ticket密钥:" + ticket_data)
    print ('接口测试成功,正在上报...')
    start() #上报
    end = time.time()
    end_time = end-start_time
    print ('本次运行耗时:' +str(round(end_time,2)) + '秒')
    logging.info ('本次运行耗时:' +str(round(end_time,2)) + '秒')

ticket_data = getTicket()

while ticket_data == "None":
    try:
        print ('正在扫描ticket')
        ticket_data = getTicket()
    except Exception as o:
        logging.error(o)
        print ('程序出现错误,请查看log\n'+o)
        mailsend("啊哈哈哈哈，鸡汤来咯！"+o,"","")
else:
    run()
