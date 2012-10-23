#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# +-----------------------------------------------------------------------------
# | File: tj_energy_notify.py
# | Author: clampist
# | E-mail: clampist[at]gmail[dot]com
# | Created: 2012-09-15
# | Last modified: 2012-10-23
# | Description:
# |     目前需求：电量不足，还剩三天的时候，邮件提醒多人，中文无乱码，数据记录
# |     crontab自动执行(10:30, 16:30)，now only for 406
# | Copyrgiht (c) 2012 by clampist. All rights reserved.
# | License: GPLv3
# +-----------------------------------------------------------------------------

import re, os, sys
import time, datetime
import urllib, urllib2, smtplib
import subprocess
from datetime import date
from email.header import Header
from email.mime.text import MIMEText

class getdata():
    def __init__(self):
        #record list for write data to log file
        self.record = []
        self.avg=0
        self.days=0
        self.notify=''
        self.result=''
        #DO NOT EDIT postdata
        self.postdata = urllib.urlencode({
            'BuildingDown':'西南二楼    ',
            'DistrictDown':'四平校区',
            'RoomnameText':'406',
            'Submit':'查询',
            '__LASTFOCUS':'',
            '__EVENTTARGET':'',
            '__EVENTARGUMENT':'',
            '__EVENTVALIDATION':'/wEWLQLT7ZjqBgKehO/XDgKS2sqQDQKbhO/XDgLvo6/WAQKchO/XDgKco5mFBAKo7ZuOCQKQtOGrAwLGtc2eAwKUkP3jDgKphpG2AgL3ot33AgL3ov2mCAKR/qiJBgLpo8D8CQLqit2DCAKmxb3NAwKagoO1DwL7l4KfDgLI+KbeDgLOpvM+ApOWxbkCAtfasrgPAp7mkOoLAvuXgsEPArS90Z0GAsaKq7AOAsj4poAOAqiThtMDAtqFzUwC3YXNTAKok9bEAQLX2rL6DAKq0IqHBwK1odOhBAKo0PbrBgLKs5euBgLqyrSJDQL+gaXtDgLqyriJDQL+gantDgLeuZHECgK8w4S2BAKjm5WMBkA4KGPC5AGia/k6EcKaav2KQR//',
            '__VIEWSTATE':'/wEPDwUKLTYwNjgwNDAyOQ8WBB4Jcm9vbXRhYmxlBQ9zcGRhdGFfcm9vbXZpZXceCWRhdGF0YWJsZQULc3BkYXRhX3ZpZXcWAgIDD2QWBgIDDxBkZBYBAgJkAgUPEA8WBB4NRGF0YVRleHRGaWVsZAUIUk9PTU5BTUUeC18hRGF0YUJvdW5kZ2QQFRwR6LWk5bOw6Lev5ZCO5YukMgAQ5ZCO5Yuk5bel5a+TICAgIBLlkI7li6Tlhazlr5PkuInnm7gP6Kej5pS+5qW8ICAgICAgD+mdkuW5tOalvCAgICAgIBDopb/ljJfkuozmpbwgICAgEOilv+WMl+S4iealvCAgICAQ6KW/5YyX5Zub5qW8ICAgIBDopb/ljJfkupTmpbwgICAgEOilv+WMl+S4gOalvCAgICAQ6KW/5Y2X5YWr5qW8ICAgIBDopb/ljZfkuozmpbwgICAgEOilv+WNl+S5nealvCAgICAQ6KW/5Y2X5LiD5qW8ICAgIBDopb/ljZfkuInmpbwgICAgEeilv+WNl+WNgeS6jOalvCAgEOilv+WNl+WNgealvEHmpbwQ6KW/5Y2X5Y2B5qW8QualvBHopb/ljZfljYHkuIDmpbwgIBDopb/ljZfkuIDmpbwgICAgD+WtpuS4iealvCAgICAgIA/lrablm5vmpbwgICAgICAP5a2m5LqU5qW8ICAgICAgEeeglOeptueUn+WFrOWvkzMgEeeglOeptueUn+WFrOWvkzQAEOeglOeptueUn+WFrOWvkzQR56CU56m255Sf5YWs5a+TNQAQ56CU56m255Sf5YWs5a+TNRUcEei1pOWzsOi3r+WQjuWLpDIAEOWQjuWLpOW3peWvkyAgICAS5ZCO5Yuk5YWs5a+T5LiJ55u4D+ino+aUvualvCAgICAgIA/pnZLlubTmpbwgICAgICAQ6KW/5YyX5LqM5qW8ICAgIBDopb/ljJfkuInmpbwgICAgEOilv+WMl+Wbm+alvCAgICAQ6KW/5YyX5LqU5qW8ICAgIBDopb/ljJfkuIDmpbwgICAgEOilv+WNl+WFq+alvCAgICAQ6KW/5Y2X5LqM5qW8ICAgIBDopb/ljZfkuZ3mpbwgICAgEOilv+WNl+S4g+alvCAgICAQ6KW/5Y2X5LiJ5qW8ICAgIBHopb/ljZfljYHkuozmpbwgIBDopb/ljZfljYHmpbxB5qW8EOilv+WNl+WNgealvELmpbwR6KW/5Y2X5Y2B5LiA5qW8ICAQ6KW/5Y2X5LiA5qW8ICAgIA/lrabkuInmpbwgICAgICAP5a2m5Zub5qW8ICAgICAgD+WtpuS6lOalvCAgICAgIBHnoJTnqbbnlJ/lhazlr5MzIBHnoJTnqbbnlJ/lhazlr5M0ABDnoJTnqbbnlJ/lhazlr5M0EeeglOeptueUn+WFrOWvkzUAEOeglOeptueUn+WFrOWvkzUUKwMcZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2dnZ2RkAhUPPCsADQBkGAEFCUdyaWRWaWV3MQ9nZHgErdmGetMBvkQIePhiXbAX+78H'
        })
        self.req = urllib2.Request(
            url = 'http://nyglzx.tongji.edu.cn/web/datastat.aspx',
            data = self.postdata
            )

    def get_energy(self):
        perday = []
        strdata = []
        htmldata = []
        timedata = []
        remainder = []
        try:
            self.result = urllib2.urlopen(self.req).read()
        except urllib2.URLError:
            print '估计同济网站又挂了'
            subprocess.call(['notify-send', '估计同济网站又挂了'])
            sys.exit()
        htmldata = re.compile(r'javascript:__doPostBack.*?colspan="4', re.DOTALL).search(self.result).group()
        #print type(htmldata)
        strdata = htmldata.split('</tr>')
        for line in  strdata:
            if '</td><td>' in line:
                #add raw data to record
                self.record.append(re.sub('<[^>]*>', ' ', line).strip())
                timedata.append(re.sub('<[^>]*>', ' ', line).split(' ')[3])
                remainder.append(re.sub('<[^>]*>', ' ', line).split(' ')[-3])
        #解决日期有间断，充电费成功之后剩余量remainder突然增加等问题
        for i in range(len(remainder)):
            if i > 0:
                #判断是否有充电费
                if  float(remainder[i])-float(remainder[i-1]) > 0:
                    #剩余量间隔/日期间隔：谨防日期间断（有跳跃)
                    perday.append((float(remainder[i]) - float(remainder[i-1])) / (dealdate(timedata[i-1]) - dealdate(timedata[i])).days)

        self.avg = sum(perday) / len(perday)
        self.days = float(remainder[0]) / self.avg
        self.notify = '{} {} 四平校区西南二楼 406\n剩余电量: {}kWh  日均消耗量: {}kWh  预计还能用: {}天'.format(datetime.datetime.now().strftime('%H:%M'), today.strftime('%a %d %b %Y'), str(round(float(remainder[0]), 2)), str(round(self.avg, 2)), str(int(self.days)))
        #self.notify = '四平校区西南二楼 406\n'+'剩余电量: '+str(round(float(remainder[0]), 2))+'kWh  日均消耗量: '+str(round(self.avg, 2)) +'kWh  预计还能用: '+str(int(self.days))+'天'

class sendmail():
    def __init__(self):
        self.mail_host = 'smtp.gmail.com'
        self.mail_user = 'nyglzx.tongji'
        self.mail_passwd = '***********'
        self.postfix = 'gmail.com'
        #self.mailto = ['00000000@qq.com']
        self.mailto = ['11111111@qq.com', '222222222@qq.com', '333333333@qq.com', '444444444@qq.com']

    def send_mail(self, sub, content):
        gmailuser = self.mail_user+'@'+self.postfix
        #添加邮件内容
        msg = MIMEText(content, 'plain', 'utf-8')
        #加邮件头
        msg['Subject'] = Header(sub, 'utf-8')
        msg['From'] = 'me'
        msg['To'] = ','.join(self.mailto)
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(self.mail_user, self.mail_passwd)
        s.sendmail(gmailuser, self.mailto, msg.as_string())
        s.close()

class timeline():
    def __init__(self):
        getinfo.get_energy()

    def sender(self):
        print getinfo.notify

        #小于三天则发邮件
        if getinfo.days < 3:
            #print 'sendmailing'
            list2str = '\n\n时间   已用电量（kWh）  已购电量（kWh）  剩余电量（kWh）\n'
            list2str += '\n'.join(getinfo.record)
            send.send_mail('同济大学能源管理中心 电量不足通知', getinfo.notify + list2str)
            #print 'sendoff'


if __name__ == '__main__':
    today = date.today()
    dateformat='%Y-%m-%d'
    #return a date that could + - directly
    #同时解决了月初日期与上个月月末30、31号之差的问题
    def dealdate(dater):
        return datetime.datetime.strptime(dater, dateformat)

    #set log dir and file path
    LOG_DIR = os.path.join(os.path.expanduser('~'), '.log')
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    LOG_PATH = os.path.join(LOG_DIR, 'tj_energy_notify.log')

    getinfo = getdata()
    send = sendmail()
    tl = timeline()
    tl.sender()

    with open(LOG_PATH, 'a') as f:
        f.write('\n{}'.format(getinfo.notify))
        f.write('\n时间   已用电量（kWh）  已购电量（kWh）  剩余电量（kWh）\n')
        for line in getinfo.record:
            f.write('{}\n'.format(line))
