#!/usr/bin/env python
# -*- coding: utf-8 -*-
# +-----------------------------------------------------------------------------
# | File: tj_energy_notify_gae.py
# | Author: clampist
# | E-mail: clampist[at]gmail[dot]com
# | Created: 2012-10-21
# | Last modified: 2012-10-23
# | Description:
# |     将 tj_energy_notify.py 移植到 GAE, 后续将支持更多寝室
# |     Demo: http://notify.archpy.info
# | Copyrgiht (c) 2012 by clampist. All rights reserved.
# | License: GPLv3
# +-----------------------------------------------------------------------------
import re, cgi
import webapp2
import time, datetime
import urllib, urllib2
from datetime import date
from google.appengine.ext import db
from google.appengine.api import mail

import sys
reload(sys)
sys.setdefaultencoding('utf8')

class InfoData(db.Model):
    notify = db.StringProperty()

info = InfoData()

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write("""
                                <html>
                                <body>
                                <p>目前仅支持 四平校区 西南二楼</p>
                                <form action="/ask" method="post">
                                房间号:<br />
                                <input type="text" name="roomno" /><br />
                                <input type="submit" value="查询">
                                <input type="reset" value="重置">
                                </form>
                                </body>
                                </html>""")

    def post(self):
        self.avg=0
        self.days=0
        self.notify=''
        self.result=''
        self.roomno = cgi.escape(self.request.get('roomno'))
        #DO NOT EDIT postdata
        self.postdata = urllib.urlencode({
            'BuildingDown':'西南二楼    ',
            'DistrictDown':'四平校区',
            'RoomnameText':self.roomno,
            #'RoomnameText':'406',
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

        perday = []
        strdata = []
        htmldata = []
        timedata = []
        remainder = []
        today = date.today()
        dateformat='%Y-%m-%d'
        def dealdate(dater):
            return datetime.datetime.strptime(dater, dateformat)
        try:
            self.result = urllib2.urlopen(self.req).read()
        except urllib2.URLError:
            print '估计同济网站又挂了！'
            sys.exit(1)   # 有错误的退出用exit(1)
        try:
            htmldata = re.compile(r'javascript:__doPostBack.*?colspan="4', re.DOTALL).search(self.result).group()
        except AttributeError:
            print '没有这个房间号！'
            sys.exit(1)
        #print type(htmldata)
        strdata = htmldata.split('</tr>')
        for line in  strdata:
            if '</td><td>' in line:
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
        self.notify = '{} {} 四平校区西南二楼 {} 剩余电量: {}kWh  日均消耗量: {}kWh  预计还能用: {}天'.format(datetime.datetime.now().strftime('%H:%M'), today.strftime('%a %d %b %Y'), str(self.roomno), str(round(float(remainder[0]), 2)), str(round(self.avg, 2)), str(int(self.days)))

        self.response.out.write("""
                                <html>
                                <body>
                                """)
        self.response.out.write('<p>'+self.notify+'</p>')
        self.response.out.write("""
                                <form action="/mail" method="post">
                                E-mail:<br>
                                <input type="text" name="email_address"><br />
                                <input type="submit" value="发送">
                                <input type="reset" value="重置">
                                </form>
                                </body>
                                </html>""")

        info.notify = self.notify
        #info.notify = unicode(self.notify).encode('utf-8')
        info.put()
        body = db.get(info.key())

class SendMail(webapp2.RequestHandler):
    def post(self):
        user_address = cgi.escape(self.request.get("email_address"))

        if not mail.is_email_valid(user_address):
            pass

        else:
            sender_address = "Energy Notify <notify@archpy.info>"
            subject = "Tongji Energy Notify"
            body = db.get(info.key())

            #self.response.out.write(body.notify)
            mail.send_mail(sender_address, user_address, subject, body.notify)
            self.response.out.write("""
                                    <html>
                                    <body>
                                    <p>Mail Sent!</p>
                                    </body>
                                    </html>""")


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/ask', MainPage),
                               ('/mail', SendMail)],
                              debug = True)
