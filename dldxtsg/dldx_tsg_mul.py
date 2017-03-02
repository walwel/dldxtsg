# encoding=utf-8
import json
import base64
import time
import requests
import pytesseract
from PIL import Image
from requests.exceptions import ConnectionError
import multiprocessing
from user_agents import userAgent 
from user_agents import chickip
from info import getInfo as getrReaderInfo
from info import closeDb,openDb
from userlist import getCode
"""
图书馆登陆
"""

is_proxy = 0
def getSession(account):
    """获取session"""
    '''
    #查看是否代理
    global is_proxy
    if not is_proxy:
        chickip()
        is_proxy = 1
    '''
    url = "http://202.199.159.130:8080/reader/login.php"
    header = {"User-Agent" : userAgent()}
    ts_session = requests.Session()
    ts_session.get(url, headers=header)
    print(">>>登陆加载完成...\n")
    getCookies(ts_session, header,account)

def getCookies(session, header,account):
    """ 获取Cookies """
    login_url = r'http://202.199.159.130:8080/reader/redr_verify.php'
    password = account
    capt = yanZheng(session, header)
    post_data = {
        "number": account,
        "passwd": password,
        "captcha": capt,
        'select':'cert_no',
        'returnUrl':''
    }
    try:
        r = session.post(login_url, data=post_data)
        r.encoding = 'utf-8'
        if len(r.text) > 10000:
            #print(">>>登陆成功...%s\n" % len(r.text))
            getInfo(session,header)
        else:
            print(">>>%s信息错误,尝试下一个...\n" % account)
    except ConnectionError:
        print(">>>连接异常...")
        return 0

def yanZheng(session,header):#识别验证码
    """识别验证码"""
    cap_url = "http://202.199.159.130:8080/reader/captcha.php"
    cap_html = session.get(cap_url, headers=header)
    pic_name = str(time.time()).replace('.','')[5:]
    with open("E:/python/tsg_images/%s.gif" % pic_name,'wb') as fp:
        fp.write(cap_html.content)
    image = Image.open("E:/python/tsg_images/%s.gif" % pic_name)
    vcode = pytesseract.image_to_string(image)
    print (">>>验证码识别完成...%s\n" % vcode)
    return vcode
    
def getInfo(session,header):
    """获取信息"""
    per_url = "http://202.199.159.130:8080/reader/redr_info_rule.php"
    books_url = "http://202.199.159.130:8080/reader/book_hist.php"
    debt_url = "http://202.199.159.130:8080/reader/fine_pec.php"
    per_session = session.get(per_url,headers=header)
    post_data = {
        "para_string": 'all',
        'topage': '1',
        }
    books_session = session.post(books_url,data=post_data)
    debt_session = session.get(debt_url,headers=header)
    per_session.encoding = 'utf-8'
    books_session.encoding = 'utf-8'
    debt_session.encoding = 'utf-8'
    html_debt = debt_session.text
    html_per = per_session.text
    html_books = books_session.text
    session.close()
    getrReaderInfo(html_per,html_books,html_debt)
    
if __name__ == "__main__":
    #start_time = time.time()
    #pool = Pool(processes=4)
    pool = multiprocessing.Pool(multiprocessing.cpu_count() + 4)
    for user in getCode():
        pool.apply_async(getSession, (user,))
    pool.close()
    pool.join()
    print(">>>列表为空，结束程序\n")
    ''''''
    #print(">>>获取失败用户",failed_user)
    #print("共耗时：%f" % (time.time() - start_time))
    