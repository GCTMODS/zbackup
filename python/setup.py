#!/usr/bin/env python

from distutils.core import setup

setup(
      name='zbackup',
      version='0.0.1',
      description="ZFS and rsync backup service",
      long_description="Provides backups using rsync and zfs snapshots",
      packages=["zbackup"],
      )
