import sys
from .zfs import ZFS, ZFSError, zfsCreate
from .zlog import zloginfo, zlogerr, zlogwarn, zlogdebug

class ConfigError(Exception):
   def __init__(self, msg):
      self.msg = msg
   def __str__(self):
      return "Config Error: %s" % str(self.msg)

class ConfigParseError(ConfigError):
   def __init__(self, linenum, value):
      self.value = value
      self.ln = linenum
   def __str__(self):
      return "Config Parsing Error(%d): %s" % (self.ln, str(self.value))


#Valid keys for each section
SECKEYS = {}
SECKEYS['volume'] = ['zfs', 'maxsnapshots']
SECKEYS['global'] = ['servurl', 'user', 'group', 'maxsnapshots', 'nosnapshots', 'noprune', 'email:to', 'email:from', 'email:smtpsrv']
#Required keys for global section
GLOBREQ = ['servurl']
#Required keys for volume section
VOLREQ = ['maxsnapshots', 'servurl']
#Keys in volume section that are inherited if not specified
VOLINH = ['servurl', 'maxsnapshots']
#Types of the keys, defaults to str
KEYTYPES = {}
KEYTYPES['maxsnapshots'] = int
KEYTYPES['nosnapshots'] = bool
KEYTYPES['noprune'] = bool


def parseConfig(configfile, config={}):
   section = None
   secarg = None
   cobj = None
   linenum = 0

   zloginfo("Parsing config file %s\n" % configfile)

   def unquote(val):
      if val[0] == '"' or val[0] == "'":
         if val[-1] != val[0]:
            raise ConfigParseError(linenum, "Badly quoted value!")
         return val[1:-1]
      else:
         return val

   for line in open(configfile, "r"):
      linenum = linenum + 1
      line = line.strip()
      if len(line) == 0 or line[0] == '#':
         #Ignore whitespace and comments
         continue
      if line[0] == '[':
         if line[-1] != ']':
            raise ConfigParseError(linenum, "Badly formatted section header!")
         #New section header
         l = line[1:-1].split(None, 1)
         if(len(l) == 0):
            raise ConfigParseError(linenum, "Empty section header!")
         section = l[0]
         if(len(l) > 1):
            secarg = l[1]
         else:
            secarg = None
         if section == 'global':
            if not config.has_key('global'):
               config['global'] = {}
            cobj = config['global']
         elif section == 'volume':
            if secarg is None:
               raise ConfigParseError(linenum, "volume section without volume name!")
            if not config.has_key(secarg):
               config[secarg] = {}
            cobj = config[secarg]
         elif section == 'files':
            if secarg is None:
               raise ConfigParseError(linenum, "files section without volume name!")
            if not config.has_key(secarg):
               config[secarg] = {}
            cobj = config[secarg]
            if not cobj.has_key('files'):
               cobj['files'] = []
         else:
            raise ConfigParseError(linenum, "Unknown section name `%s'" % section)
         continue
      #Inside a section
      if section is None:
         #Must be in a section
         raise ConfigParseError(linenum, "No section specified!")
      elif section == 'files':
         #All lines are filename globs
         cobj['files'].append(unquote(line))
      else:
         #All lines are key = value pairs
         l = line.split('=', 1)
         if(len(l) != 2):
            raise ConfigParseError(linenum, "Invalid key = value line")
         key = l[0].rstrip()
         val = unquote(l[1].lstrip())
         try:
            val = KEYTYPES.get(key, str)(val)
         except ValueError:
            raise ConfigParseError(linenum, "Invalid value type for key `%s', expected %s" % (key, str(KEYTYPES[key])))
         if key not in SECKEYS[section]:
            raise ConfigParseError(linenum, "Invalid key %s for section %s" % (key, section))
         cobj[key] = val
   #Done parsing the file
   return config

def finalizeConfig(config):
   gobj = config['global']
   
   #Query ZFS subsystem
   zfs = ZFS()

   #Handle global section first
   for reqkey in GLOBREQ:
      if not gobj.has_key(reqkey):
         raise ConfigParseError(linenum, "Global section missing required key %s" % reqkey)

   #Handle volumes
   for vol, vobj in config.iteritems():
      if vol == 'global':
         continue
      #Inherit keys from global
      for inhkey in VOLINH:
         if not vobj.has_key(inhkey):
            vobj[inhkey] = gobj[inhkey]
      #Inherit zfs from volume name if not set
      if not vobj.has_key('zfs'):
         vobj['zfs'] = vol
      #Check files list
      if not vobj.has_key('files'):
         vobj['files'] = []
      if len(vobj['files']) == 0:
         zlogwarn("Volume %s has no files!\n" % vol)

      #Check that zfs volume exists
      zfsname = vobj['zfs']
      vobj['zfs'] = zfs.get(zfsname)
      if vobj['zfs'] is None:
         zlogwarn("ZFS volume `%s' does not exist, attempting to create.." % zfsname)
         zfsCreate(zfsname)
         zfs = ZFS()
         vobj['zfs'] = zfs.get(zfsname)
         if vobj['zfs'] is None:
            #This should never happen
            raise ZFSError("Still couldn't create ZFS??? %s" % zfsname)
      
      #Verify all required keys are present
      for reqkey in VOLREQ:
         if not vobj.has_key(reqkey):
            raise ConfigError("Volume `%s' missing required key `%s'" % (vol, reqkey))


