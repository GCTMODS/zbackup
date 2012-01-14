noinst_DATA=__init__.py zconfig.py zfs.py rsync.py zlog.py zvolume.py

all-local:
	rm -f config.py
	echo "RSYNC_BIN='rsync'" >> config.py
	echo "ZFS_BIN='zfs'" >> config.py
	echo "CONFFILE='${sysconfdir}/zbackup.conf'" >> config.py
	echo "CONFDIR='${sysconfdir}/zbackup.conf.d'" >> config.py

clean-local:
	rm -f config.py
