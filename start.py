# -*- coding: utf8 -*-
import requests,json,pytesseract,hashlib,logging,os,time,smtplib,sys
import requests as req
from PIL import Image
from io import BytesIO
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.text import MIMEText

#智慧校园一键上报
start_time = time.time()
sckey = '' #service酱通知密钥
sess = requests.Session()
hashcode = '1596828473201'
headers = { 
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36', 
'Connection': 'close' } #伪装成PC用户

sys_info = os.popen('uname -o').read().replace('\n','') 
#判断系统平台生成log路径
if sys_info == "Android":
    fileName = '1.log'
else:
    fileName = sys.path[0] +'1.log'

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', filename=fileName, filemode='a')

codeurl= "http://api.hbei.com.cn/api/Login/GetCheckCodePic?hashcode="+ hashcode #验证码URL
user,password = '学号', '密码'
smtp_server,send_mail,mail_passwd, = "","","" #邮件服务器 用户名和密码
#例: send_user,mail_passwd = "smtp.163.com","xxxxxxxxx@163.com","邮箱授权码"
def passwd_md5(): #将密码进行MD5 32位加密
    md5 = hashlib.md5()
    md5.update(bytes(password,encoding='utf-8'))
    passmd5 = md5.hexdigest()
    return passmd5

def getcodeimage(): #处理验证码图片
    response = req.get(codeurl,headers=headers) #获取验证码对象
    image = Image.open(BytesIO(response.content))
    image = image.convert("L") #验证码转灰度
    return image

def iscode(): #识别验证码
    image = getcodeimage() 
    try:
        abcd=pytesseract.image_to_string(image, lang='eng', config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
    except Exception as e:
        logging.info('错误日志:', e)
        requests.get('https://sc.ftqq.com/' + sckey + '.send?text=程序抛出异常:'+ str(e)) #推送异常的原因到service酱
    return abcd #返回验证码

def isticket(): #获取ticket密钥
    passmd5 = passwd_md5() #获取加密后的密码
    abcd = iscode() #获取验证码
    post_login = { "CheckCode": abcd,"HashCode": hashcode,"LoginID": user,"Password": passmd5,"LoginWay": "手机WAP" } #登录表单
    try:
        login = sess.post(url='http://api.hbei.com.cn/api/Login/UserLoginValid', data=post_login, headers=headers)
        abc = login.json()
        ticket_data  = (abc["Ticket"]) #取出Ticket
        ticket_data = str(ticket_data)
    except Exception as f:
        logging.info('ticket获取异常:', f)
    return ticket_data

def mailsend(): #发送邮件通知
    mailmg = "上报健康状态:" + yq + "\n上报体温:" + tv
    message = MIMEText(mailmg, 'plain' , 'utf-8')
    message["From"] = send_user #谁来发
    message["To"] = "主人" #发给谁
    message['Subject'] = '智慧校园每日上报'
    try:
        a = smtplib.SMTP() #实例化一个smtp服务
        a.connect(smtp_server,25)
        a.login(send_mail,mail_passwd)
        a.sendmail(send_mail,receivers ,message.as_string())#发邮件
        print ("邮件发送成功!")
        a.quit() #关闭服务
    except Exception as k:
        logging.info('邮件发送异常:',k)

def start():
    checktk = sess.get('http://api.hbei.com.cn/api/Login/CheckApiTictetValid?ticket=' + ticket_data).text
    post_data = {'ticket': ticket_data,'ifhomeaddr': '1','yyqzdm': '00','selfgjdm': '0','familyyq': '0','provincedm': '420000','citydm': '421300','countydm': '421381'} #构造上报表单
    tempValue = sess.get(url='http://api.hbei.com.cn/api/HealthReport/SaveSelfTempValue?ticket='+ticket_data+'&tempvalue=36.1', headers=headers).text
    logging.info('上报体温:' + tempValue) #打印体温上报结果
    saveyqinfo = requests.post(url='http://api.hbei.com.cn/api/HealthReport/SaveYQinfo', data=post_data, headers=headers).text
    logging.info('上报健康状态:' + saveyqinfo) #打印健康上报结果
    requests.get('https://sc.ftqq.com/' + sckey + '.send?text=健康上报:'+ str(saveyqinfo) + '体温上报:'+ str(tempValue))
    return tempValue,saveyqinfo

ticket_data = isticket() #获取ticket密钥
if ticket_data == "None":
    print ('没有获取到ticket:' + ticket_data)
    os.system('python3 ' + sys.argv[0] )
elif ticket_data != "None":
    print ("ticket密钥:" + ticket_data)
    print ('自动模式获取密钥成功,正在上报...')
    tempValue,saveyqinfo = start() #运行上报函数并获取返回的上报状态
    tv = str(tempValue)
    yq = str(saveyqinfo)
    mailsend() #发送邮件通知
    end = time.time()
    end_time = end-start_time
    logging.info ('本次运行耗时:' +str(round(end_time,2)) + '秒')
else:
    print ("垃圾学校,玩尼玛")
