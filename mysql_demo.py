# -*— coding:UTF-8 -*-
import MySQLdb

class Database:
    '''
    def __init__(self, host, user, pwd, name, charset="utf8"):
        self.isConnected = True
        self.errorMsg = ""
        try:
            self.connection = MySQLdb.connect(host, user, pwd, name, charset=charset)
        except Exception as e:
            self.connection = None
            self.isConnected = False
            self.errMsg = e[1]
            print e
        else:
            self.cursor = self.connection.cursor()
    '''
    def __init__(self, host, user, pwd, charset="utf8"):
        self.isConnected = True
        self.errMsg = ""
        try:
            self.connection = MySQLdb.connect(host, user, pwd, charset=charset)
        except Exception as e:
            self.connection = None
            self.isConnected = False
            self.errorMsg = e[1]
        else:
            self.cursor = self.connection.cursor()
    
    def createDb(self, dbName):
        self.errMsg = "";
        try:
            sql = "create database if not exists " + dbName + " character set utf8";
            self.cursor.execute(sql)
            return True
        except Exception as e:
            self.errMsg = e[0]
            return False
    
    def createTable(self):
        self.errMsg = "";
        try:
            self.connection.select_db("demoDb") # 选择数据库
            sql = "create table if not exists student(Name varchar(32), Age integer, Sex varchar(4)) charset utf8"
            self.cursor.execute(sql)
            return True
        except Exception as e:
            self.errMsg = e[1]
            return False
    
    def insert(self, name="", age=0, sex="男"):
        self.errMsg = "";
        sql = "INSERT into student(Name,Age,Sex) values(%s,%s,%s)"
        try:
            self.connection.select_db("demoDb") # 选择数据库
            self.cursor.execute(sql, [name,age,sex])
            self.connection.commit()
            return True
        except Exception as e:
            self.errMsg = e[1]
            self.connection.rollback()
            return False
	
    def query(self, obj):
        self.errMsg = ""
        for key in obj:
            value = obj[key]
        try:
            self.connection.select_db("demoDb") # 选择数据库
            sql = "select Name,Age,Sex from student where " + key + "=%s";
            cursor = self.connection.cursor(MySQLdb.cursors.DictCursor) #查询的返回值会变成字典格式
            cursor.execute(sql, [value])
            return cursor.fetchall()
        except Exception as e:
            self.errMsg = e[1]
            return ""
        
    def update(self, data, condition):
        self.errMsg = "";       
        tmp = "";
        params = [];
        for key in data:
            tmp = tmp + key + "=%s,"
            params.append(data[key])       
        sql = "update student set " + tmp[:-1] + " where " + condition[0] + condition[1] + "%s"
        params.append(condition[2]) 
        try:
            self.connection.select_db("demoDb") # 选择数据库
            self.cursor.execute(sql, params)
            self.connection.commit()
            return True
        except Exception as e:
            self.errMsg = e[1]
            self.connection.rollback()
            return False

    def delete(self, condition):
        self.errMsg = ""
        sql = "delete from student where " + condition[0] + condition[1] + "%s"
        try:
            self.connection.select_db("demoDb") # 选择数据库
            self.cursor.execute(sql, [condition[2]])
            self.connection.commit()
            return True
        except Exception as e:
            self.errMsg = e[1]
            self.connection.rollback()
            return False
    
    def __del__(self):
        if self.connection:
            self.connection.close()

 
if __name__ == "__main__":
    mysql = Database("127.0.0.1", "root", "123456",  "utf8")
    if not mysql.isConnected:
        print mysql.errorMsg
    else:
        print "数据库连接成功！"
    #mysql.createDb("demoDb")

    select = input( """请选择：
    1.添加数据
    2.删除数据
    3.查询数据
    4.修改数据
    """)
    
    if select == 1:
        name = raw_input("姓名：")
        age  = raw_input("年龄：")
        sex  = raw_input("性别：")
        if mysql.insert(name, age, sex):
            print "数据添加成功"
        else:
            print mysql.errMsg
    elif select == 2:
        field = raw_input("删除条件：")
        tmp = raw_input()
        value = raw_input()
        if mysql.delete([field, tmp, value]):
            print "数据删除成功"
        else:
            print mysql.errMsg         
    elif select == 3:
        result = mysql.query({"Name":"诸葛亮"})
        for student in result:
            for key in student:
                print student[key],
            print "\n"
    elif select == 4:
        if mysql.update({"Age":330}, ["Name", "=", "貂蝉"]):
            print "数据更新成功"
        else:
            print mysql.errMsg 
    else:
        pass
   