set User=%1
set Host=%2

echo "%User%@^%Host%"

IF NOT EXIST ./id_rsa (ssh-keygen -b 2048 -V +520w -f ./id_rsa)
IF NOT EXIST ./id_rsa.pub (ssh-keygen -b 2048 -V +520w -f ./id_rsa)

IF NOT EXIST ./id_rsa (echo "Have no private key")
IF NOT EXIST ./id_rsa.pub (echo "Have no public key")

IF EXIST ./id_rsa (ssh %User%^@%Host% "rm -Rf .ssh")
IF EXIST ./id_rsa (ssh %User%^@%Host% "mkdir -p .ssh")
IF EXIST ./id_rsa (ssh %User%^@%Host% "mkdir -p .ssh")
IF EXIST ./id_rsa (scp ./id_rsa.pub %User%^@%Host%:~\.ssh\authorized_keys)
IF EXIST ./id_rsa (ssh %User%^@%Host% "chmod 700 .ssh")
IF EXIST ./id_rsa (ssh %User%^@%Host% "chmod 600 .ssh/authorized_keys")

pause