# backend.py user domain [enableMySql=true] [enablePhpMyAdmin=false] [Alias 1] [Alias 2] [Alias x]

# This script is indented to create a new virtual host in the local (backend) web server.
# The backend server must have an 'sftp' group, an Apache web server with suexec enabled and MySql or MariaDB.
# Your python interpreter must have the 'python-mysqldb' extension if you intend to use MySQL with the script.
# Only tested on Linux systems with Python 2.7.x and Apache 2.2 and 2.4
# Author Justin Duplessis <drfoliberg@gmail.com>

__version__ = "0.1.1"
apache_user = "www-data"

def print_help():
    print "Usage " + args[0] + " user domain [enableMySql=true] [enablePhpMyAdmin=false] [Alias 1] [Alias 2] [Alias x]"
    print ""
    print "This script is indented to create a new virtual host in the local (backend) web server."
    print "The backend server must have an 'sftp' group, an Apache web server with suexec enabled and MySql or MariaDB."
    print "Your python interpreter must have the 'python-mysqldb' extension if you intend to use MySQL with the script."
    print "Only tested on Linux systems with Python 2.7.x and Apache 2.2 and 2.4"
    print "Author Justin Duplessis <drfoliberg@gmail.com>"
    print "Version: " + __version__


def generate_config():
    str = "<VirtualHost *:80>\n"
    str += "ServerName " + domain + "\n"
    for alias in aliases:
        str += "ServerAlias " + alias + "\n"
    str += "DocumentRoot " + base_path + "/www\n"
    str += "SuexecUserGroup " + user + " " + user + "\n"
    str += "HostNameLookups off\n"
    str += "UseCanonicalName off\n"
    str += """LogFormat "%h %l %u %t \"%r\" %>s %b" common"""
    str += "\nCustomLog " + base_path +"/logs/log common\n"
    if phpmyadmin_enabled:
        str += "Alias /phpmyadmin /var/www/phpmyadmin\n"
    str += "</VirtualHost>"
    return str


from genericpath import exists
import os
from os import mkdir
import pwd
from tools import tools
import sys

args = sys.argv
if len(args) == 2 and args[1] == "--help":
    print_help()
    exit(0)

if len(args) < 3:
    print "Usage " + args[0] + " user domain [enableMySql=true] [enablePhpMyAdmin=false] [Alias 1] [Alias 2] [Alias x]"
    print "For complete help: " + args[0] + " --help "
    sys.exit(2)

if os.geteuid() != 0:
    print "[Error] Are you root ? (no) I thought so...\nCome back later when you are !"
    exit(1)

#arg 1 username
user = args[1]
print "[Info] The user of the web host will be '" + user + "'"

#arg 2 domain name
domain = args[2]
print "[Info] The main domain of the web host will be '" + domain + "'"

#arg 3 Enable mysql generation ?
#default = True
mysql_enabled = True
if len(args) > 3:
    if args[3] == "false":
        mysql_enabled = False

if mysql_enabled:
    print "[Info] A MySql database and user will be generated."
    if tools.mysql_password == "CHANGE ME":
        print "[Error] Please change the mysql information to connect to the database in /tools/tools.py !"
        exit(1)

#arg 4 Enable an alias to PhpMyAdmin ?
#default = True
phpmyadmin_enabled = True
if len(args) > 4:
    if args[4] == "false":
        phpmyadmin_enabled = False

if phpmyadmin_enabled:
    print "[Info] An alias to PhpMyAdmin will be created"

#args 5+ All the other arguments are the domain aliases
#default = []
aliases = []
if len(args) > 5:
    for i in range(5, len(args)):
        print "[Info] '" + args[i] + "' will be used as a domain alias"
        aliases.append(args[i])
else:
    print "[Info] No aliases will be associated with the main domain !"

#The base path for the virtual host
base_path = "/var/www/" + user
print "[Info] The base path of the web host will be '" + base_path + "'"

#Confirm the information
choice = raw_input("\nAre these information correct ? [y/N]")
if choice == "y" or choice == "Y":
    print "Proceeding..."
else:
    print "[Error] Aborted by user !\n[Info] Nothing was changed on the system."
    exit(3)


#Checking if the web root already exists
if exists(base_path):
    print "[Error] The base directory for the web host already exists !"
    sys.exit(1)

#Checking if the user already exists
if tools.user_exists(user):
    print "[Error] The user already exist !"
    sys.exit(1)

#Checking if the apache virtual host configuration already exists
if os.path.isfile("/etc/apache2/sites-available/" + user):
    print "[Error] A configuration file already exists for this virtual host !"
    sys.exit(1)

#Generate a password for the user
password = tools.generate_password()

#Create the MySQL user
if mysql_enabled:
    tools.create_database_user(user, password)

#Create the UNIX user
os.system("scripts/createUserWebHost.bash " + user + " " + base_path + " " + password)

#Retreive the gid and uid of the UNIX user
user_uid = pwd.getpwnam(user).pw_uid
user_gid = pwd.getpwnam(user).pw_gid

#Get the uid of apache log user
apache_uid = pwd.getpwnam(apache_user).pw_uid

#Proceeding to create the root
mkdir(base_path, 0755)

#/www of the user. RW for user
mkdir(base_path+"/www", 0755)
os.chown(base_path+"/www", user_uid, user_gid)

#/logs only read access for the user and write for apache log user
mkdir(base_path+"/logs", 0750)
os.chown(base_path+"/logs", apache_uid, user_gid,)

#/backups only read access for the user
mkdir(base_path+"/backups", 0750)
os.chown(base_path+"/backups", 0, user_gid)

#Generate the Apache configuration and add a new site to sites-available
f = open("/etc/apache2/sites-available/"+user, 'w')
f.write(generate_config())

#activate the site with a2ensite
os.system("a2ensite " + user)

#restart apache server
os.system("service apache2 reload")

print "\n\n[Success] The virtual host seems to be completed !"
print "Please connect to the SFTP server with these credentials: "
print "User: '" + user + "'\nPassword: '" + password + "'"
if mysql_enabled:
    print "The MySql credentials are the same\nYour database is '"+ user +"' and the sql server is 'localhost'"