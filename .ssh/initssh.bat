echo off

IF NOT EXIST .\id_rsa (ssh-keygen -b 2048 -V +520w -f .\id_rsa)
IF NOT EXIST .\id_rsa.pub (ssh-keygen -b 2048 -V +520w -f .\id_rsa)
IF NOT EXIST .\id_rsa (echo Have no private key && pause && exit)
IF NOT EXIST .\id_rsa.pub (echo Have no public key && pause && exit)

set /p User=Please input username of LINUX:
set /p Host=Please input IP of LINUX:
set /P PubkeyContent=<id_rsa.pub

echo "%User%@^%Host%"
ssh %User%^@%Host% "rm -Rf .ssh; mkdir -p .ssh; echo \"%PubkeyContent%\" >>.ssh/authorized_keys; chmod 700 .ssh; chmod 600 .ssh/authorized_keys"

pause
