import smtplib
from email.header import Header
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart

class mailSender():
    def __init__(self, mail_host, mail_user, mail_pass):
        super().__init__()
        self.mail_host = mail_host
        self.mail_user = mail_user
        self.mail_pass = mail_pass

    def sendmail(self, receiver, msg, title, player_id):
        # msg = MIMEText(message, 'plain', 'utf-8')
        # msg['Subject'] = Header(title, 'utf-8').encode()
        # msg['From']=formataddr(["竹萌IMYVM",self.mail_user])
        # msg['To']=formataddr([player_id, receiver])
        MESSAGE = MIMEMultipart('alternative')
        MESSAGE['subject'] = title
        MESSAGE['To'] = formataddr([player_id, receiver])
        MESSAGE['From'] = formataddr(["竹萌IMYVM",self.mail_user])
        MESSAGE.preamble = ""
        MESSAGE.attach(msg)
        server = smtplib.SMTP_SSL(self.mail_host, 465)
        # 登陆服务器
        server.login(self.mail_user, self.mail_pass)
        # 发送邮件及退出
        server.sendmail(self.mail_user, [receiver], MESSAGE.as_string())
        server.quit()