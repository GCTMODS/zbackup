import subprocess

from .zlog import zloginfo, zlogdebug, zlogerr, zlogwarn
from .config import RSYNC_BIN

RSYNC_ARGS = ["-avz", "--protocol=29", "--delete"]

class RsyncError(Exception):
   def __init__(self, msg):
      self.msg = msg
   def __str__(self):
      return str(self.msg)

def rsync(srcpath, destpath):
   p = subprocess.Popen([RSYNC_BIN] + RSYNC_ARGS + [srcpath, destpath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   for line in p.stdout:
      zloginfo(line.strip())
   p.stdout.close()
   if p.wait() != 0:
      raise RsyncError("rsync failure: %s" % p.stderr.read())
   p.stderr.close()
