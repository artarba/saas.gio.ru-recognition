import mysql.connector
import os
import shutil
from database import most_pop_file
#import MySQLdb
#import dotenv

# token_path = dotenv.find_dotenv()
# dotenv.load_dotenv(dotenv_path=token_path)
# DB_PASS = os.getenv('db_pass')
# DB_NAME = os.getenv('database')
# DB_USER = os.getenv('db_user')

DB_NAME = 'bmc'
DB_USER = 'artem'
DB_PASS = '898989qW!'

print(DB_PASS, DB_NAME, DB_USER)

main_path = os.getenv('main_path')

fds = os.listdir(main_path + '/result')

#mydb = MySQLdb.connect(host="rc1a-zuyqcvblbiqlxj7m.mdb.yandexcloud.net",
#                       port=3306,
#                       user="artem",
#                       passwd="898989qW!",
#                       db="bmc",
#                       # ssl={'ca': '~/.mysql/root.crt'})
#                       ssl={'ca': '/Users/artem/.mysql/root.crt'}
#                       )

mydb = mysql.connector.connect(
     host="rc1a-l7mf9thjhi1qacrh.mdb.yandexcloud.net",
     user=DB_USER,
     password=DB_PASS,
     database=DB_NAME,
)

mycursor = mydb.cursor()


def remove_file(filename):
    mycursor.execute("SELECT filename, COUNT(*) FROM users GROUP BY filename")
    myresult = mycursor.fetchall()
    for x in myresult:
        count = x[-1]
        if count > 5:
            filename = str(filename)
            shutil.copyfile(main_path + '\\for_bonus\\' + filename + '.jpg',
                            main_path + '\\result\\' + filename + '.jpg')
            os.remove(main_path + '\\for_bonus\\' + filename + '.jpg')
            sql = "DELETE FROM users WHERE filename = '{}'".format(filename)
            mycursor.execute(sql)
            mydb.commit()
            print(mycursor.rowcount, "record(s) deleted")


def insert_sql(user_id, filename):
    sql = "INSERT INTO users (user_id, filename) VALUES (%s, %s)"
    val = (user_id, filename)
    mycursor.execute(sql, val)
    mydb.commit()
    print(mycursor.rowcount, "record inserted.")


def validation(user_id, filename):
    mycursor.execute("SELECT * FROM users WHERE user_id = '{}' "
                     "AND filename = '{}'".format(user_id, filename))
    myresult = mycursor.fetchone()
    print(myresult)
    return myresult


def insert_for_work(user_id, filename):
    sql = "INSERT INTO users (user_id, filename) VALUES (%s, %s)"
    val = (user_id, filename)
    mycursor.execute(sql, val)
    mydb.commit()
    print(mycursor.rowcount, "record inserted.")


def check(user_id):
    files = os.listdir(main_path + '/for_bonus')
    for img in files:
        filename = img.replace('.jpg', '')
        if filename.startswith('box_'):
            record_exists = validation(user_id, filename=filename)
            if record_exists is None:
                mycursor.execute(
                    "SELECT * FROM users")
                myresult = mycursor.fetchall()
                if myresult == []:
                    insert_for_work(949191326, 'boxyyyyy')
                superstar = most_pop_file()
                mycursor.execute(
                    "SELECT * FROM users WHERE filename = '{}'".format(superstar))
                myresult = mycursor.fetchall()
                if myresult[0][1] != None:
                    return 'ok', filename
                # else:
