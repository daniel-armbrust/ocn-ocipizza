#!/bin/sh

/usr/bin/timedatectl set-timezone America/Sao_Paulo

/usr/bin/dnf -y update

# Disable SELinux
setenforce 0
/usr/bin/sed -i 's/^SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config

/usr/bin/systemctl stop firewalld
/usr/bin/systemctl disable firewalld

# Expand the boot volume
/usr/libexec/oci-growfs -y

exit 0
