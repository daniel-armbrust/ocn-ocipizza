#!/bin/sh

#/usr/bin/timedatectl set-timezone America/Sao_Paulo

/usr/bin/dnf -y update
/usr/bin/dnf -y install traceroute net-tools

# Disable SELinux
setenforce 0
/usr/bin/sed -i 's/^SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config

/usr/bin/systemctl stop firewalld
/usr/bin/systemctl disable firewalld

# Expand the boot volume
/usr/libexec/oci-growfs -y

# rc.local file content
cat <<EOF >/etc/rc.d/rc.local
#!/bin/bash

# Região.
region="\`curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/region\`"

# Object Storage Namespace.
objectstorage_ns="\`curl -s -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/metadata/objectstorage-ns\`"

# Download do script de configuração do Firewall e Policy Routing.
curl -s -o /etc/rc-firewall.sh https://objectstorage.\$region.oraclecloud.com/n/\$objectstorage_ns/b/scripts-storage/o/rc-firewall.sh

# Execução do script de configuração do Firewall e Policy Routing.
chmod 0500 /etc/rc-firewall.sh
/etc/rc-firewall.sh

# From /etc/rc.local
touch /var/lock/subsys/local
EOF

# Start and enable the rc-local service
chmod +x /etc/rc.d/rc.local
systemctl start rc-local
systemctl enable rc-local

exit 0