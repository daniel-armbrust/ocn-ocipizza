#!/bin/sh

if [ -z "$(which curl)" ]; then
   echo "[ERROR] Need curl command to continue. Exiting..."
   exit 1
fi

host_list=('icanhazip.com' 'ifconfig.me' 'ipinfo.io/ip' 'ipecho.net/plain')

for host in ${host_list[*]}; do
   my_ip="$(curl "$host" 2>/dev/null)"

   if [ $? -eq 0 ]; then     
      break
   fi
   
done

echo "{\"my_public_ip\": \"$my_ip/32\"}"

exit 0