import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import time
import hashlib

EMAIL_CONFIG = {
    'sender': '2952108703@qq.com',  # 发
    'password': 'nypfcsumkeaydhbh',  # 授权码
    'receiver': '1670600889@qq.com',  # 收
    'smtp_server': 'smtp.qq.com',  # SMTP服务器
    'smtp_port': 465  # SMTP端口
}

CHECK_INTERVAL = 60  # 检查间隔(秒)，1分钟
TARGET_URL = "https://iat.ustc.edu.cn/iat/x198/"
TARGET_KEYWORD = "中国科大先研院2025年硕士研究生招生复试分数线及复试名单"


def get_page_content(url):
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        return response.text
    except Exception as e:
        print(f"获取网页失败: {str(e)}")
        return None


def check_keyword_update(html, keyword):
    soup = BeautifulSoup(html, 'html.parser')

    articles = soup.select('li a')

    for article in articles:
        if keyword in article.text.strip():
            return True, article['href']  # 返回找到的链接
    return False, None


def send_email(subject, content):
    """发送邮件通知"""
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = EMAIL_CONFIG['sender']
    msg['To'] = EMAIL_CONFIG['receiver']

    try:
        server = smtplib.SMTP_SSL(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.login(EMAIL_CONFIG['sender'], EMAIL_CONFIG['password'])
        server.sendmail(EMAIL_CONFIG['sender'], [EMAIL_CONFIG['receiver']], msg.as_string())
        server.quit()
        print("邮件发送成功")
    except Exception as e:
        print(f"邮件发送失败: {str(e)}")


def monitor():
    last_hash = None  # 存储上一次页面特征值

    while True:
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} 正在检查更新...")

        html = get_page_content(TARGET_URL)
        if html:
            # 计算当前页面特征值
            current_hash = hashlib.md5(html.encode('utf-8')).hexdigest()

            # 双重检查机制：先检查页面变化，再检查关键词
            if current_hash != last_hash:
                found, link = check_keyword_update(html, TARGET_KEYWORD)
                if found:
                    message = f"检测到研究生复试通知已发布！\n访问地址：{link}"
                    send_email("【重要】研究生复试通知已发布", message)
                    return  # 找到后停止监控
                last_hash = current_hash
            else:
                print("页面内容未发生变化")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    print("启动网页监控...")
    monitor()
