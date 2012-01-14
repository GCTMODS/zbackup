#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.68])
AC_INIT([zbackup], [0.0.1], [fmatthew5876@gmail.com])

AC_PROG_INSTALL

AM_INIT_AUTOMAKE([1.11 -Wall no-define foreign])

# Checks for programs.
AC_CHECK_PROG([ZFSBIN], [zfs], [zfs], [])
AS_IF([test "x$ZFSBIN" != "xzfs"],
      AC_MSG_ERROR(["Could not find zfs binary!"]))
AC_CHECK_PROG([RSYNCBIN], [rsync], [rsync], [])
AS_IF([test "x$RSYNCBIN" != "xrsync"],
      AC_MSG_ERROR(["Could not find rsync binary!"]))

# Checks for libraries.
AM_PATH_PYTHON([2.7])

# Checks for header files.

# Checks for typedefs, structures, and compiler characteristics.

# Checks for library functions.

AC_CONFIG_FILES([Makefile
                 python/Makefile
                 python/zbackup/Makefile])

AC_OUTPUT
