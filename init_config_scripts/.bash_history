losetuo
losetup
LOOPD="$(losetup -f)"
echo $LOOPD
umount /media/pi/ROOT-A 
losetup -d "$LOOPD"
ls /dev/lo*
losetup -f
losetup -h
losetup -d loop0
losetup -d /dev/loop0
ls
exit
exit
cd ~
ls
ls -la
sudo rm -r .ssh 
ls -la
exit
exit
