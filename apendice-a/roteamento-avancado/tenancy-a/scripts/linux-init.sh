#!/bin/sh

#/usr/bin/timedatectl set-timezone America/Sao_Paulo

/usr/bin/dnf -y update

# Disable SELinux
setenforce 0
/usr/bin/sed -i 's/^SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config

/usr/bin/systemctl stop firewalld
/usr/bin/systemctl disable firewalld

# Enable OCID Daemon
# https://docs.oracle.com/en-us/iaas/oracle-linux/oci-utils/index.htm#oci-network-config__config_vnic
/usr/bin/systemctl enable --now ocid.service

# Expand the boot volume
/usr/libexec/oci-growfs -y

exit 0
