Table of Contents
=================

  * Overview

  * DHCP Installation and Configuration

  * TFTP Installation and Configuration

  * PXE Boot Files Configuration

  * Kickstart and Preseed Configuration

Overview
========

These files are intended to help you quickly setup and configure a PXE
(Preboot Execution Environment) server which is capable of installing
multiple operating systems.

The supported list of operating systems may be found in the mirrors file in
this same directory.  You may add to this list, but you *might* need to
modify the mktftpboot.py script in that case.


DHCP Installation and Configuration
===================================

If you currently have a DHCP server on your subnet then specify your intended
PXE boot server as the "next-server" in your DHCP config.  Also, specify
"pxelinux.0" as the filename for clients to look for.  Compare with the
snippet below.


If you currently do not have a DHCP server on your subnet:

  Install dhcpd:

    yum install dhcpd
      or
    apt-get update && apt-get install dhcp3-server

Edit /etc/dhcpd.conf, or /etc/dhcpd/dhcpd.conf and make an entry for your
subnet similar to the following:

    ddns-update-style none;
    ignore client-updates;
    
    next-server PXEServerIP;
    filename "pxelinux.0";
    
    subnet 192.168.1.0 netmask 255.255.255.0 {
            option routers                  192.198.1.1;   # Your Gateway IP
            option subnet-mask              255.255.255.0;
            option domain-name              "example.com";
            option domain-name-servers      8.8.8.8;       # DNS server
            option time-offset              -18000;        # Eastern Standard Time
            range dynamic-bootp 192.168.1.80 192.168.1.99; # DHCP IP range
            default-lease-time 2160;
            max-lease-time 4320;
    }

Start or restart dhcpd and check /var/log/message or /var/log/syslog for
failures.


TFTP Installation and Configuration
===================================

Install the TFTP server on your PXE boot server:

    yum install tftp tftp-server
      or
    apt-get update && apt-get install tftp tftpd

If you are running iptables, you'll need to add the following rule:

    -A RH-Firewall-1-INPUT -s 192.168.1.0/24 -p udp -m udp --dport 69 -j ACCEPT 

You will also need to load the ip_conntrack_tftp iptables module:

    modprobe ip_conntrack_tftp

On CentOS/Redhat servers, make the above persistent by editing
/etc/sysconfig/iptables, and /etc/sysconfig/iptables-config.

You'll likely need to edit /etc/xinetd.d/tftp to enable the tftp server.
Modify the "server_args" variable in that file to specify the tftp root
directory, perhaps use "/tftpboot".  Then restart xinetd and the tftp
server should be running.


PXE Boot Files Configuration
============================

Now you may run the mktftpboot.py script in this directory.  First, edit the
mirrors text file to ensure that you are using a mirror for each operating
system that is close to you.  Also, you may comment out any operating system
that you do not want to support.  Run the script with no arguments to see up
to date usage instructions. Basically, you should be able to run:

    python mktftpboot.py /tftpboot

and it will download the appropriate boot files for each supported operating
system.

You will then be instructed to make your menu system in /tftpboot/pxelinux.cfg,
assuming that tftpboot is the directory you passed to mktftpboot.py.  If this
is a new setup, then you can just run this:

    cp pxelinux.cfg/* /tftpboot/pxelinux.cfg/

This will give you a functional PXE boot environment that will allow you to do
stock installs, boot into rescue environments, and run memtest.

If you want to enable automatic installs then please continue to the next
section.


Kickstart and Preseed Configuration
===================================

If you look at pxelinux.cfg/auto you'll notice that every entry has a
"YOURWEBSERVER" variable.  In order to support automatic installations of
Debian, Ubuntu, and CentOS servers, you need to have a webserver that can serve
the preseed or kickstart files to the installation process.

The PXE boot server you just setup is a fine place to put these files.  First,
install a webserver:

    yum install httpd
      or
    apt-get install apache2

On CentOS, start and enable the web server:

    service httpd start
    chkconfig httpd on

The default webroot will likely be /var/www/html/.  In this directory, create
two folders:

    mkdir /var/www/html/kickstart
    mkdir /var/www/html/preseed

Now, copy the basic automatic install files from the kickstart and preseed
files in the current direcotry:

    cp pressed/* /var/www/html/preseed/
    cp kickstart/* /var/www/html/kickstart/

By default, the root password on these intallations is "pl3aseChangeme!".  To
set this to something different you'll need to encode a new password and
update the relevant options in the kickstart and preseed files.

If you run your own mirror, or if you are closer to another mirror than the
default, you can update the mirror options in the kickstart and preseed files.
Choosing a close and fast mirror will greatly increase the speed of the
installation process.
