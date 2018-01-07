import pymysql
import pymysql.cursors


# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='zhjlsyjh123',
                             db='movie',
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)

try:
    with connection.cursor() as cursor:
        # Create a new record
        sql = "INSERT INTO `movies2` (`movieID`, `movieName`, `genres`, `rank`) VALUES (%s, %s, %s, %s)"
        sql = "SELECT * FROM `movies2` order by RAND() limit 0, 5"
        cursor.execute(sql)
        result = cursor.fetchall()
        print(result)

    # connection is not autocommit by default. So you must commit to save
    # your changes.
    connection.commit()

finally:
    connection.close()