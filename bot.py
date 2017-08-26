# encoding: utf-8

# ReportBot

# By Aer0

# www.ianyway.cn

# useradmin@ianyway.cn
import time
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64
import requests
import re
reportID = str(raw_input(u'输入嫌疑人的steam主页地址:'))
file = open("accounts.txt")
line = file.readline()
url = 'http://www.vacbanned.com/engine/check'
VACBANEDPOST = {
    'qsearch' : reportID
}
html = requests.post(url,data=VACBANEDPOST)
html = html.text.replace(' ', '').decode('gbk', 'ignore').replace(' ', '').replace('\r\n', '').replace('\t', '').replace('\r', '').replace('\n', '')
p1 = r'(?<=<tdcolspan="2"style="text-align:center"><ahref=").+?(?=">ViewSteamCommunityprofile</a>)'
pattern1 = re.compile(p1)
matcher1 = re.search(pattern1,html)
reportURL =  matcher1.group(0)
print u'已获得真实steamURL:%s'%reportURL
steamID = reportURL.strip('http://www.steamcommunity.com/profiles/')
i = 0
#print steamID
for line in open("accounts.txt"):
    if line.startswith('#'):
        continue
    else:
        p= True
        while p:
            uname= line.strip().split(':')[0]
            passwd= line.strip().split(':')[1]
            user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
            url = 'https://steamcommunity.com/login/getrsakey/'
            headers = { 'User-Agent' : user_agent }
            session = requests.session()
            post = {'username': uname, 'donotcache': str(int(time.time()*1000))}
            req = session.post(url,data=post,headers=headers)
            data =  req.json()
            mod = long(str(data["publickey_mod"]), 16)
            exp = long(str(data["publickey_exp"]), 16)
            rsa = RSA.construct((mod, exp))
            cipher = PKCS1_v1_5.new(rsa)
            # Login
            url2 = 'https://steamcommunity.com/login/dologin/'
            values2 = {
                    'username' : uname,
                    "password": base64.b64encode(cipher.encrypt(passwd)),
                    "emailauth": "",
                    "loginfriendlyname": "",
                    "captchagid": "-1",
                    "captcha_text": "",
                    "emailsteamid": "",
                    "rsatimestamp": data["timestamp"],
                    "remember_login": False,
                    "donotcache": str(int(time.time()*1000)),
            }
            headers2 = { 'User-Agent' : user_agent }
            req2 = session.post(url2,data=values2,headers=headers2)
            data2 = req2.json()
            if data2["success"]:
                    print u"bot:%s登陆成功"%uname
            else:
                    print u"错误,无法登陆:", data2["message"]
                    p =False
            reportURL = reportURL
            report = session.get(reportURL)
            p2 = r"(?<=sessionid=).+?(?=for)"

            pattern2 = re.compile(p2)
            matcher2 = re.search(pattern2,str(session.cookies))
            sessionID =  matcher2.group(0).strip(' ')
            values3 = {
                'abuseID' : steamID,
                'sessionid': sessionID,
                'ingameAppID': '730',
                'abuseType':'Cheating',
                'abuseDescription':'',
                'json' : '1'
            }
            reportBot = session.post('https://steamcommunity.com/actions/ReportAbuse/',data=values3,headers=headers2)
            #data3 = reportBot.json()
            #print data3
            if '25' in reportBot.text:
                print u"举报成功,bot:%s"%uname
                i = i + 1
                p = False
            elif '1' in reportBot.text:
                print u'原因1错误,正在重试'
                p = True
            else:
                print u'举报失败,bot:%s,原因:%s'%(uname,reportBot.text)
                p = False
            logoutURL = 'https://steamcommunity.com/login/logout/'
            logoutpost = {
                'sessionid': sessionID
            }
            logout = session.post(logoutURL,logoutpost)

print u'成功举报%d次'%i