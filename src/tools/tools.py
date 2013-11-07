
#You must change this information according to your MySQL server information !
mysql_user = "root"
mysql_password = "CHANGE ME"


def user_exists(name):
    import pwd
    exists = True
    try:
        return pwd.getpwnam(name)
    except KeyError:
        exists = False

    return exists


def create_database_user(user, password, database="null", server="localhost"):
    if database == "null":
        database = user
    query = "CREATE USER '" + user + "'@'" + server + "' IDENTIFIED BY '" + password + "';"
    query += "GRANT USAGE ON *.* TO '" + user + "'@'" + server + "' IDENTIFIED BY '" + password + "' WITH " \
             "MAX_QUERIES_PER_HOUR 0 MAX_CONNECTIONS_PER_HOUR 0 MAX_UPDATES_PER_HOUR 0 MAX_USER_CONNECTIONS 0;"
    query += "CREATE DATABASE IF NOT EXISTS `" + database + "`;"
    query += "GRANT ALL PRIVILEGES ON `" + database + "`.* TO '" + user + "'@'" + server + "';"

    import MySQLdb
    db = MySQLdb.connect("localhost", mysql_user, mysql_password)
    db.query(query)


def generate_password():
    import string
    from random import choice
    characters = string.ascii_letters + string.digits
    password = "".join(choice(characters) for x in range(16))
    return password