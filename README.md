Lamp3000
========

This script is indented to create a new virtual host with sftp and mysql access.

Usage: backend.py user domain [enableMySql=true] [enablePhpMyAdmin=false] [Alias 1] [Alias 2] [Alias x]

This script is indented to create a new virtual host with sftp and mysql access.
The backend server must have an 'sftp' group, an Apache web server with suexec enabled and MySql or MariaDB.
Your python interpreter must have the 'python-mysqldb' extension if you intend to use MySQL with the script.
Only tested on Linux systems with Python 2.7.x and Apache 2.2 and 2.4
