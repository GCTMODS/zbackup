import datetime

from .rsync import rsync
from .zlog import zloginfo 
from .zfs import zfsSnapshot, zfsDestroy, ZFSError, zfsMount

def backupVolume(volname, config, dosnap=True, dryrun=False):
   vconfig = config[volname]
   files = vconfig['files']
   servurl = vconfig['servurl']
   zfs = vconfig['zfs']
   zfsname = zfs['name']
   destpath = zfs['mountpoint']
   mounted = zfs['mounted']

   zloginfo("")
   zloginfo("===========================================")
   zloginfo("Backing up Volume `%s' at mountpoint `%s'" % (volname, destpath))

   if mounted != 'yes':
      raise ZFSError("ZFS Filesystem `%s' is not mounted!" % zfsname)
   
   for path in files:
      src = '%s:"%s"' % (servurl, path)
      dest = "%s/" % destpath
      if not dryrun:
         rsync(src, dest)
      else:
         zloginfo("DRYRUN: rsync %s %s" % (src, dest))
   
   if dosnap:
      now = datetime.datetime.now()
      snapname = "%s@zbackup-%04d%02d%02d-%02d%02d%02d" % (zfsname, now.year, now.month, now.day, now.hour, now.minute, now.second)
      if not dryrun:
         zfsSnapshot(snapname)
      else:
         zloginfo("DRYRUN: zfs snapshot %s" % snapname)
   else:
      zloginfo("Not taking snapshot...")

def pruneSnapshots(volname, config, doprune=True, dryrun=False):
   vconfig = config[volname]
   zfs = vconfig['zfs']
   zfsname = zfs['name']
   sconfig = zfs['snapshots']
   snaplist = sconfig.keys()
   snaplist.sort()
   maxsnaps = vconfig['maxsnapshots']
   delsnaps = len(snaplist) - maxsnaps

   if doprune:
      zloginfo("Pruning old snapshots...")

      for x in xrange(0, delsnaps):
         if not dryrun:
            zfsDestroy(snaplist[x])
         else:
            zloginfo("DRYRUN: zfs destroy %s" % snaplist[x])
   else:
      zloginfo("Not pruning snapshots...")


