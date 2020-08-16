# -*- coding: utf8 -*-
import requests,json,pytesseract,hashlib,logging,os,time,smtplib,sys,base64
import requests as req
from PIL import Image
from io import BytesIO
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.text import MIMEText

start_time = time.time()
sckey = '' #service酱密钥
sess = requests.Session()
hashcode = '1596828473201'
headers = { 
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36', 
'Connection': 'close' } #伪装成PC用户
#sys_info = os.popen('uname -o').read().replace('\n','')
fileName = sys.path[0] + '/1.log'
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', filename=fileName, filemode='a')
##智慧校园一键上报
codeurl= "http://api.hbei.com.cn/api/Login/GetCheckCodePic?hashcode="+ hashcode
ak,sk = '','' #分别填入从百度云获取的API Key和Secret Key
user,password = '', '' #分别填入学号和密码
send_user,mail_passwd,recipient = "","",""  
#分别填入发件人QQ邮箱,邮箱授权码及收件人邮箱
imgtoimg = 'https://s4.aconvert.com/convert/convert-batch-win.php'
imgfull = 'https://s4.aconvert.com/convert/p3r68-cdx67/'
headers_b = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36 Edg/84.0.522.59',
    'Referer': 'https://www.aconvert.com/cn/image/'
    }
post_data = {
        'file': codeurl,'targetformat': 'jpg','imagesize': 'option1', 'code': '83000','filelocation': 'online'}

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

def baidu_ocr(): #baidu识别接口
    a = requests.post(imgtoimg,data = post_data,headers= headers_b).json()["filename"]
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id='+ ak +'&client_secret=' + sk
    response = requests.get(host)
    if response:
        access_token = response.json()['access_token'] #获取access_token
    request_api_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
    img = imgfull +a
    params = {"url":img,"language_type":"ENG"}
    request_url = request_api_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response_b = requests.post(request_url, data=params, headers=headers).json()
    baidu_pass =  response_b["words_result"][0]["words"]
    return baidu_pass

def local_ocr(): #识别验证码
    image = getcodeimage() 
    try:
        abcd=pytesseract.image_to_string(image, lang='eng', config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
    except Exception as e:
        logging.error(e)
        print ('识别验证码时出现错误,请查看log --> ' + fileName)
        requests.get('https://sc.ftqq.com/' + sckey + '.send?text=程序抛出异常:'+ str(e)) #推送异常的原因到service酱
    return abcd #返回验证码

def isticket(): #获取ticket密钥
    passmd5 = passwd_md5() #获取加密后的密码
    abcd = local_ocr() #获取本地识别的验证码
    #baidu_pass = baidu_ocr() #获取百度识别的验证码
    post_login = { "CheckCode": abcd,"HashCode": hashcode,"LoginID": user,"Password": passmd5,"LoginWay": "手机WAP" } #登录表单
    try:
        login = sess.post(url='http://api.hbei.com.cn/api/Login/UserLoginValid', data=post_login, headers=headers)
        abc = login.json()
        ticket_data  = str(abc["Ticket"]) #取出Ticket
       # if ticket_data:
       #     print ("本地识别验证码失败，正在调用百度云接口...")
       # else:
       #     abcd = baidu_pass
    except Exception as f:
        logging.error(f)
        print ('获取密钥时出现错误,请查看log --> ' + fileName)
    return ticket_data

def mailsend(): #发送邮件通知
    mailmg = "\n上报健康状态:" + yq + "\n上报体温:" + tv
    message = MIMEText(mailmg, 'plain' , 'utf-8')
    message["From"] = send_user #谁来发
    message["To"] = "主人" #发给谁
    message['Subject'] = '智慧校园每日上报'
    try:
        a = smtplib.SMTP() #实例化一个smtp服务
        a.connect('smtp.qq.com',25)
        a.login(send_user,mail_passwd)
        a.sendmail(send_user, recipient ,message.as_string())#发邮件
        print ("邮件发送成功!")
        a.quit() #关闭服务
    except Exception as k:
        logging.error(k)
        print ('发送邮件时出现错误,请查看log --> ' + fileName)

def start():
    checktk = sess.get('http://api.hbei.com.cn/api/Login/CheckApiTictetValid?ticket=' + ticket_data).text
    post_data = {'ticket': ticket_data,'ifhomeaddr': '1','yyqzdm': '00','selfgjdm': '0','familyyq': '0','provincedm': '420000','citydm': '421300','countydm': '421381'}
    tempValue = sess.get(url='http://api.hbei.com.cn/api/HealthReport/SaveSelfTempValue?ticket='+ticket_data+'&tempvalue=36.1', headers=headers).text
    logging.info('上报体温:' + tempValue) #打印体温上报结果
    saveyqinfo = requests.post(url='http://api.hbei.com.cn/api/HealthReport/SaveYQinfo', data=post_data, headers=headers).text
    logging.info('上报健康状态:' + saveyqinfo) #打印健康上报结果
    requests.get('https://sc.ftqq.com/' + sckey + '.send?text=健康上报:'+ str(saveyqinfo) + '体温上报:'+ str(tempValue))
    return tempValue,saveyqinfo

def run():
    print ("ticket密钥:" + ticket_data)
    print ('获取密钥成功,正在上报...')
    tempValue,saveyqinfo = start() 
    tv = str(tempValue)
    yq = str(saveyqinfo)
    #mailsend() #发送邮件通知
    end = time.time()
    end_time = end-start_time
    print ('本次运行耗时:' +str(round(end_time,2)) + '秒')
    logging.info ('本次运行耗时:' +str(round(end_time,2)) + '秒')

ticket_data = isticket()

while ticket_data == "None":
    try:
        print ('正在重新获取ticket')
        ticket_data = isticket()
    except Exception as o:
        logging.error(o)
        print ('程序异常,请查看log --> ' + fileName)
else:
    run()

