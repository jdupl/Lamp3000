#!/bin/bash
#@author Justin Duplessis

if [ $# -lt 3 ]
then
   echo "Usage: $0 user home password";
   exit 2
fi
User=$1;
Home=$2;
Password=$3;

$(useradd $User -d $Home -s /bin/false -G sftp)

$(echo $User:$Password > /tmp/$User)
$(chpasswd < /tmp/$User)
$(rm /tmp/$User)
echo "[Script] User $User was created with password $Password";