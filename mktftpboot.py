#!/usr/bin/env python
#
#  Script to setup a /tftpboot for running PXE installs of CentOS, Ubuntu,
#  and Debian Operating Systems.
#
#  Copyright (c) 2012, Jesse Griffin <jag3773@gmail.com>
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#    Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
#  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
#  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#  POSSIBILITY OF SUCH DAMAGE.

import os
import sys
import shutil
import urllib2

help = '''
Script to setup a /tftpboot for running PXE installs of CentOS, Ubuntu, and
Debian Operating Systems.

[sudo] python mktftpboot.py TFTPROOTDIR

Use like this:
python mktftpboot.py /tftpboot
'''
warning = '''
I'm going to destroy and recreate these directories:

  %s

in %s.  I will also replace pxelinux.0, vesamenu.c32, and memtest86.
'''
mirrorsfile = "mirrors"
bootfiles = ["linux", "initrd.gz"]
pxelinuxurl = "http://mirror.anl.gov/pub/ubuntu/dists/precise/main/installer-i386/current/images/netboot/ubuntu-installer/i386/pxelinux.0"
vesamenuurl = "http://mirror.anl.gov/pub/centos/6/os/i386/isolinux/vesamenu.c32"
memtesturl = "http://mirror.anl.gov/pub/centos/5/os/i386/isolinux/memtest"

def geturl(url, outfile):
  print "Getting %s" % url
  try:
    request = urllib2.urlopen(url)
  except:
    print "  => ERROR retrieving %s\nCheck the URL" % url
    return
  print "  => Writing to %s" % outfile
  with open(outfile, 'wb') as fp:
    shutil.copyfileobj(request, fp)

def loadMirrors(filename):
  mirrors = {}
  if not os.path.exists(filename):
    print "Could not find mirrors file: %s" % filename
    exit(1)
  for line in open(filename, 'r'):
    if line.startswith('#'): continue
    if line.startswith('\n'): continue
    k,v = line.split('=', 1)
    mirrors[k.strip()] = [v.strip()]
  for k,v in mirrors.items():
    mirrors[k].append('i386')
    if 'centos' in k:
      mirrors[k].append('x86_64')
      mirrors[k].append('initrd.img')
      mirrors[k].append('vmlinuz')
    else:
      mirrors[k].append('amd64')
      mirrors[k].append('initrd.gz')
      mirrors[k].append('linux')
  return mirrors

def pxelinuxcfg(tftpdir):
  if not os.path.exists("%s/pxelinux.cfg" % tftpdir):
    os.mkdir("%s/pxelinux.cfg" % tftpdir)
    print '''\n You should now create your menu system in %s/pxelinux.cfg/, you
may use the files in pxelinux.cfg/ in this directory as an example.''' % tftpdir

def getFiles(mirrors, tftpdir):
  for OS, m in mirrors.items():
    for arch in m[1:3]:
      try:
        for root, dirs, files in os.walk("%s/%s/%s" % (tftpdir, OS, arch),
                                                             topdown=False):
          for name in files:
            os.remove(os.path.join(root, name))
          for name in dirs:
            os.rmdir(os.path.join(root, name))
      except OSError: pass
      try:
        os.makedirs("%s/%s/%s" % (tftpdir, OS, arch))
      except OSError: pass
      for bf in m[3:5]:
        geturl('%s/%s' % (m[0].replace('arch', arch).strip('/'), bf),
                                "%s/%s/%s/%s" % (tftpdir, OS, arch, bf))
  geturl(pxelinuxurl, "%s/pxelinux.0" % tftpdir)
  geturl(vesamenuurl, "%s/vesamenu.c32" % tftpdir)
  geturl(memtesturl, "%s/memtest86" % tftpdir)


if __name__ == '__main__':
  mirrors = loadMirrors(mirrorsfile)
  if len(sys.argv) < 2:
    print help
    exit()
  print warning % (' '.join(mirrors.keys()), sys.argv[1])
  cont = raw_input("Is this OK? [y/n] ")
  if cont.lower() != 'y':
    exit(0)
  getFiles(mirrors, sys.argv[1])
  pxelinuxcfg(sys.argv[1])
