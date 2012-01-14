import subprocess

from .zlog import zloginfo, zlogerr, zlogdebug
from .config import ZFS_BIN

class ZFSError(Exception):
   def __init__(self, msg):
      self.msg = msg
   def __str__(self):
      return str(self.msg)

FIELDS=['name', 'used', 'avail', 'refer', 'mountpoint', 'usedbysnapshots', 'mounted']

class ZFS(dict):
   def __init__(self):
      p = subprocess.Popen([ZFS_BIN, "list", "-H", "-o", ','.join(FIELDS), "-t", "filesystem,snapshot"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      r = p.wait()
      if r != 0:
         raise ZFSError("zfs list failed: %s", p.stderr.read());
      p.stderr.close()

      for line in p.stdout:
         l = line.split()
         if '@' in l[0]:
            #This is a snapshot
            zfsbase = l[0].split('@')[0]
            if not self.has_key(zfsbase):
               self[zfsbase] = {}
            zobj = self[zfsbase]
            if not zobj.has_key("snapshots"):
               zobj['snapshots'] = {}
            sobj = zobj['snapshots']
            ss = sobj[l[0]] = {}
            #Populate the fields
            for x in xrange(0, len(FIELDS)):
               ss[FIELDS[x]] = l[x]
         else:
            #This is a filesystem
            if not self.has_key(l[0]):
               zobj = self[l[0]] = {}
            #Populate the fields
            for x in xrange(0, len(FIELDS)):
               zobj[FIELDS[x]] = l[x]
      p.stdout.close()

def zfsCall(function, target):
   p = subprocess.Popen(["zfs", function, target], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   for line in p.stdout:
      zloginfo(line.strip())
   p.stdout.close()
   if p.wait() != 0:
      raise ZFSError("zfs %s `%s' failed : %s" % (function, target, p.stderr.read()))
   p.stderr.close()

def zfsCall2(function, t1, t2):
   p = subprocess.Popen(["zfs", function, t1, t2], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   for line in p.stdout:
      zloginfo(line.strip())
   p.stdout.close()
   if p.wait() != 0:
      raise ZFSError("zfs %s `%s' `%s' failed : %s" % (function, t1, t2, p.stderr.read()))
   p.stderr.close()

def zfsDestroy(target):
   zfsCall("destroy", target)
   zloginfo("Destroyed ZFS object `%s'" % target)

def zfsCreate(target):
   zfsCall("create", target)
   zloginfo("Created ZFS filesystem `%s'" % target)

def zfsSnapshot(target):
   zfsCall("snapshot", target)
   zloginfo("Created ZFS snapshot `%s'" % target)

def zfsRename(old, new):
   zfsCall2("rename", old, new)
   zloginfo("Renamed ZFS targets `%s'->`%s'", old, new)

def zfsMount(target):
   zfsCall("mount", target)
   zloginfo("Mounted ZFS filesystem `%s'", target)




