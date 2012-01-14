import sys
import datetime
import syslog
import smtplib

LOGLEVEL = 0
CONSOLE=True
SYSLOG=False
EMAIL=False

EBUFFER = []

def zlogInit(loglevel, console=True, syslog=False, email=False):
   global LOGLEVEL
   global SYSLOG
   global EMAIL
   global CONSOLE
   LOGLEVEL = loglevel
   SYSLOG = syslog
   EMAIL = email
   CONSOLE = console

def zlogerr(msg):
   msg = "ERROR: %s" % msg
   if CONSOLE:
      print >>sys.stderr, msg
   if SYSLOG:
      syslog.syslog(syslog.LOG_ERR, msg)
   if EMAIL:
      EBUFFER.append("%s\n" % msg)



def zlogwarn(msg):
   msg = "WARNING: %s" % msg
   if CONSOLE:
      print >>sys.stderr, msg
   if SYSLOG:
      syslog.syslog(syslog.LOG_WARNING, msg)
   if EMAIL:
      EBUFFER.append("%s\n" % msg)

def zloginfo(msg):
   if LOGLEVEL > 0:
      if CONSOLE:
         print msg
      if SYSLOG:
         syslog.syslog(syslog.LOG_INFO, msg)
      if EMAIL:
         EBUFFER.append("%s\n" % msg)

def zlogdebug(msg):
   if LOGLEVEL > 1:
      if CONSOLE:
         print msg
      if SYSLOG:
         syslog.syslog(syslog.LOG_DEBUG, msg)
      if EMAIL:
         EBUFFER.append("%s\n" % msg)


def zlogFinal(success, config):
   global EBUFFER
   gconfig = config['global']
   if SYSLOG:
      syslog.closelog()
   if EMAIL:
      if success:
         ss = "SUCCESS"
      else:
         ss = "FAILURE"
      now = datetime.datetime.now()
      fromaddr = gconfig['email:from']
      toaddr = gconfig['email:to']
      smtpsrv = gconfig['email:smtpsrv']
      subject = "zbackup Report: %02d/%02d/%04d %02d:%02d (%s)" % (now.month, now.day, now.year, now.hour, now.minute, ss)
      body = ''.join(EBUFFER)
      msg = '\n'.join([
         "From: %s" % fromaddr,
         "To: %s" % toaddr,
         "Subject: %s" % subject,
         "",
         body])

      zloginfo("Sending email report to %s" % toaddr)
      s = smtplib.SMTP(smtpsrv)
      s.sendmail(fromaddr, [toaddr], msg)
      s.quit()

      EBUFFER = []
