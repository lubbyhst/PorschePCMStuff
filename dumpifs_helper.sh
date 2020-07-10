#dumpifs_helper.sh
IMAGE=$1
TMPDIR=./
EXTRDIR=./ifs_extracted
mkdir $EXTRDIR
echo "Dumping content of $IMAGE... to $EXTRDIR"
dumpifs -z $IMAGE |awk '{print $3}' >$TMPDIR/ifscont.txt
dumpifs -z $IMAGE |grep "\->" |awk '{print $3" -> "$5}' >$TMPDIR/ifslinks.txt
for i in `cat $TMPDIR/ifscont.txt`; do dirname $i; done |sort -u >$TMPDIR/dirlist.txt
for i in `cat $TMPDIR/dirlist.txt`; do mkdir -p $EXTRDIR/$i; done
cd $EXTRDIR
dumpifs -zx $IMAGE
cd ../
echo "done !"
