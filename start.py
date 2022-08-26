# -*- coding: utf8 -*-
import requests,json,hashlib,logging,time,smtplib,sys
import requests as req
from aip import AipOcr
from PIL import Image
from io import BytesIO
from email.mime.text import MIMEText

##智慧校园一键上报
start_time = time.time()
sess = req.Session()
hashcode = '1596828473201'
headers = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36', 'Connection': 'close' }

fileName = sys.path[0] + '/1.log'
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', filename=fileName, filemode='a')

codeurl= "http://api.hbei.com.cn/api/Login/GetCheckCodePic?hashcode="+ hashcode

user,password = '201901990', '011207' #学号，密码
send_user,mail_passwd = "maping@mpcloud.top","H6xrtdXPpmVXUptM" # 邮箱，授权码

options = {}
options["language_type"] = "ENG"
options["detect_direction"] = "true"

client = AipOcr("21926012", "zQVSB7Oo0QEZjHio6kPI3bRs", "8mgMCBONXUtr0sKVL8kftkmhYrjZ1GcE")

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

def baidu_ocr(): #baidu识别接口 
    img = getcodeimage()
    img.save("a.jpg")
    with open('a.jpg', 'rb') as img_file:
        img2 = client.basicGeneral(img_file.read(),options)
    baidu_pass =  img2["words_result"][0]["words"]
    return baidu_pass

# def local_ocr(): #本地识别验证码
#     image = getcodeimage() 
#     try:
#         abcd=pytesseract.image_to_string(image, lang='eng', config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
#     except Exception as e:
#         logging.error(e)
#         print ('识别验证码时出现错误,请查看log --> ' + fileName)
#         requests.get('https://sc.ftqq.com/' + sckey + '.send?text=程序抛出异常:'+ str(e)) #推送异常的原因到service酱
#     return abcd #返回验证码

def isticket(): #获取ticket密钥
    passmd5 = passwd_md5() #获取加密后的密码
    vcode = baidu_ocr() #获取百度识别的验证码
    post_login = {
        "CheckCode": vcode,"HashCode": hashcode,"LoginID": user,"Password": passmd5,"LoginWay": "手机WAP" } #登录表单
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
    message["From"] = send_user #谁来发
    message["To"] = "" #发给谁
    message['Subject'] = '智慧校园每日上报'
    try:
        a = smtplib.SMTP() #实例化一个smtp服务
        a.connect('smtp.exmail.qq.com')
        a.login(send_user,mail_passwd)
        a.sendmail(send_user, "3207754367@qq.com",message.as_string())#发邮件
        print ("已发送邮件通知")
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
    twApi = "http://wapapi.hbei.com.cn/api/HealthReport/SaveSelfTempValue" #http://api.hbei.com.cn/api/HealthReport/SaveSelfTempValue
    tempValue = sess.get(url=twApi+'?ticket='+ticket_data+'&tempvalue=36.1', headers=headers).text
    logging.info('上报体温:' + tempValue) #打印体温上报结果
    saveyqinfo = sess.post(url='http://wapapi.hbei.com.cn/api/HealthReport/SaveYQinfo', data=post_data, headers=headers).text
    logging.info('上报健康状态:' + saveyqinfo) #打印健康上报结果
    mailsend("","\n上报健康状态:"+saveyqinfo,"\n上报体温:"+tempValue) #发送邮件通知
    listAPi = "http://wapapi.hbei.com.cn/api/HealthReport/GetTodaySelfTempList?ticket="+ticket_data
    deleteItem = "http://wapapi.hbei.com.cn/api/HealthReport/DelSelfTempRecord/"
    listInfo= sess.get(listAPi).text
    for i in json.loads(listInfo):
        strii = requests.get(deleteItem+i["id"],headers).text
        mailsend("已删除于 "+str(i['checktime']) +"上报的体温信息, 返回状态："+strii+" \nID:"+i["id"] +" \n体温: "+str(i["tempvalue"]),"","")
    

def run():
    print ("ticket密钥:" + ticket_data)
    print ('接口测试成功,正在上报...')
    start() #上报
    end = time.time()
    end_time = end-start_time
    print ('本次运行耗时:' +str(round(end_time,2)) + '秒')
    logging.info ('本次运行耗时:' +str(round(end_time,2)) + '秒')

ticket_data = isticket()

while ticket_data == "None":
    try:
        print ('正在扫描ticket')
        ticket_data = isticket()
    except Exception as o:
        logging.error(o)
        print ('程序出现错误,请查看log --> ' + fileName)
        mailsend("啊哈哈哈哈，鸡汤来咯！"+o,"","")
else:
    run()
