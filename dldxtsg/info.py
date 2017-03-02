#coding=utf-8
from bs4 import BeautifulSoup
import pymysql
import re

def openDb():
    """打开数据库"""
    #连接配置信息
    config = {
          'host':'127.0.0.1',
          'port':3306,
          'user':'root',
          'password':'',
          'db':'tsg',
          'use_unicode':True,
          'charset':"utf8"
          }
    # 创建连接
    try:    
        conn = pymysql.connect(**config)
        return conn
    except:
        print(">>>数据库打开失败...")
        return 0
def closeDb(conn):
    """关闭数据库"""
    conn.commit()
    conn.close()
def getDebt(html_debt):
    """处理超期图书信息"""
    debt_list = []
    soup_debt = BeautifulSoup(html_debt,'html.parser')
    tr_list = soup_debt.find_all("tr")[1:]
    for tr in tr_list:
        #遍历图书列表
        td_list = tr.find_all("td")
        #获取图书信息:条形码、书名、作者、借阅时间、归还时间、所属库
        if len(td_list) == 10:
            #re.sub('[\'|"|(|)|\'|{|}|\[|\]]','',)
            bar_code = td_list[0].text
            book_name = re.sub('[ \'|"|(|)|\'|{|}|\[|\]|,]','',td_list[2].text)
            book_name = book_name[:21] if len(book_name) > 21 else book_name 
            author = re.sub('[ \'|"|(|)|\'|{|}|\[|\]|,]','',td_list[3].text)
            loandate = td_list[4].text
            returndate = td_list[5].text
            lib = td_list[7].text +'-'+ td_list[8].text +'>'+ td_list[6].text
            debt_list.append([bar_code,book_name,author,loandate,returndate,lib])
            #print(bar_code,book_name,author,loandate,returndate,lib)
    return debt_list
    
def getBooks(html_books):
    """处理借阅历史书籍"""
    books_list = []
    soup = BeautifulSoup(html_books,"html.parser")
    #获取所有图书列表
    tr_list = soup.find_all("tr")[1:]
    for tr in tr_list:
        #遍历图书列表
        td_list = tr.find_all("td")
        #获取图书信息:条形码、书名、作者、借阅时间、归还时间、所属库
        if len(td_list) == 7:
            #格式化数据
            #no = re.sub('[ |\'|"|(|)|\'|{|}|\[|\]]','',td_list[0].text)
            bar_code = re.sub('[ \'|"|(|)|\'|{|}|\[|\]]','',td_list[1].text)
            book_name = re.sub('[ \'|"|(|)|\'|{|}|\[|\]]','',td_list[2].text)
            book_name = book_name[:21] if len(book_name) > 21 else book_name 
            author = re.sub('[ \'|"|(|)|\'|{|}|\[|\]]','',td_list[3].text)
            loandate = re.sub('[ \'|"|(|)|\'|{|}|\[|\]]','',td_list[4].text)
            returndate = re.sub('[ \'|"|(|)|\'|{|}|\[|\]]','',td_list[5].text)
            lib = re.sub('[ \'|"|(|)|\'|{|}|\[|\]]','',td_list[6].text)
            #print(no,bar_code,book_name,author,loandate,returndate,lib)
            books_list.append([bar_code,book_name,author,loandate,returndate,lib])
        else:
            print(">>>图书%s信息有误,%d" % (td_list[0].text, len(td_list)))
    return books_list
    
def getInfo(html_per,html_books,html_debt):
    """获取信息"""
    conn = openDb()
    soup_per = BeautifulSoup(html_per,'html.parser')
    #print(">>>文档加载成功...\n")
    spans = soup_per.find_all(class_="bluetext")
    if len(spans) == 29:
    #姓名、学号、失效期、生效期、最大可借、读者类型、借阅等级、借阅数量、违章次数、欠款金额、身份证、院系、性别
        name = spans[0].find_parent().text[3:]
        code_num = spans[1].find_parent().text[5:]
        ex_date = spans[3].find_parent().text[5:]
        ef_date = spans[5].find_parent().text[5:]
        max_bl_num = spans[6].find_parent().text[7:]
        reader_type = spans[9].find_parent().text[5:]
        bl_level = spans[10].find_parent().text[5:]
        bl_num = spans[11].find_parent().text[5:]
        vi_num = spans[12].find_parent().text[5:]
        debt = spans[13].find_parent().text[5:]
        id_card = spans[16].find_parent().text[5:]
        depaetment = spans[17].find_parent().text[5:]
        sex = spans[20].find_parent().text[3:]
        # 执行sql语句
        cursor = conn.cursor()
        # 执行sql语句，插入记录
        sql = 'INSERT INTO user_info_14 (name, code_num,\
            ex_date, ef_date, max_bl_num, reader_type,\
            bl_level, bl_num, vi_num, debt, id_card,\
            depaetment, sex) VALUES (%s, %s, %s, %s,\
            %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(sql, (name, code_num,\
            ex_date, ef_date, max_bl_num, reader_type,\
            bl_level, bl_num, vi_num, debt, id_card, depaetment, sex));
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        print(">>>%s数据写入成功...\n" % name)
        conn.commit()
        #表名
        code_num = 'u' + code_num
        books = getBooks(html_books) + getDebt(html_debt)
        for book in books:
            bar_code,book_name,author,loandate,returndate,lib = book
            #创建book表
            create_sql = 'create table if not exists %s (\
                bar_code varchar(20),book_name varchar(255),\
                author varchar(250),loandate varchar(30),\
                returndate varchar(30),lib varchar(30))' % code_num
            cursor.execute(create_sql)
            conn.commit()
            #写入图书信息
            books_sql = "INSERT INTO %s (bar_code, book_name,author,\
            loandate, returndate, lib) VALUES ('%s', '%s', '%s','%s',\
            '%s', '%s')" % (code_num,bar_code, book_name,author,\
            loandate, returndate, lib)
            #print(books_sql)
            cursor.execute(books_sql);
            conn.commit()
            
        print('>>>%s图书数据写入完成...' % code_num)
        closeDb(conn)
    else:
        print("文档解析异常>>>\n",len(spans),'\n',spans)
        