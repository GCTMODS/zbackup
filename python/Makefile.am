SUBDIRS=zbackup

all-local:
	${PYTHON} ./setup.py build

install-data-local:
	${PYTHON} ./setup.py install --prefix=${prefix}
	install -d ${sysconfdir}/zbackup.conf.d

clean-local:
	${PYTHON} ./setup.py clean
