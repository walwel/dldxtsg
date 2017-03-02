#coding=utf-8

import xlrd

"""用户账号列表"""

def getClass():
    """获取班级学号及人数"""
    data = xlrd.open_workbook('C:/Users/welwel/Desktop/dldxtsg/13级学号人数.xls')
    table = data.sheets()[0] 
    col4 = table.col_values(4)
    col5 = table.col_values(5)
    co4 = [int(n) for n in col4]
    co5 = [int(n) for n in col5]
    dic = dict(zip(co4,co5))
    print(">>>获取班级字典，长度%d..." % len(dic))
    return dic
def userList():
    """生成用户账号,key、value为int类型"""
    dic = getClass()
    for key,value in dic.items():
        for n in range(1,value+1):
            n = str(n)
            print(n)
            num = (len(str(value)) - len(n)) * '0' + n
            yield str(key) + num
            
def getCode():
    """获取学号"""
    code = xlrd.open_workbook('20143986.xls')
    for table in code.sheets():
        col6 = table.col_values(6)
        co = [int(x) for x in list(filter(lambda x:len(str(x))==10 ,col6))]
        for user in co:
            yield str(user)
