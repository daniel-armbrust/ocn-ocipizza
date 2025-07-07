#!/bin/sh

/usr/bin/timedatectl set-timezone America/Sao_Paulo

/usr/bin/dnf -y update
/usr/bin/dnf -y install traceroute

# Disable SELinux
setenforce 0
/usr/bin/sed -i 's/^SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config

/usr/bin/systemctl stop firewalld
/usr/bin/systemctl disable firewalld

# Enable IP Forwarding
sysctl -w net.ipv4.ip_forward=1
echo 'net.ipv4.ip_forward = 1' >> /etc/sysctl.conf

# Expand the boot volume
/usr/libexec/oci-growfs -y

# Configuring VNICs
/usr/bin/oci-network-config configure

exit 0