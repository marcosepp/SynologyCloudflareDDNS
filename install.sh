#!/bin/bash

set -e

epoch=$(date +%s)

echo "Backup current ddns_provider.conf to /etc.defaults/ddns_provider.conf.${epoch}"
cp /etc.defaults/ddns_provider.conf /etc.defaults/ddns_provider.conf.${epoch}
chmod 0755 /etc.defaults/ddns_provider.conf.${epoch}
echo "Done!"

echo "Downloading new ddns_provider.conf"
wget https://raw.githubusercontent.com/marcosepp/SynologyCloudflareDDNS/master/ddns_provider.conf -O /etc.defaults/ddns_provider.conf
chmod 0755 /etc.defaults/ddns_provider.conf
echo "Done!"

echo "Downloading cloudflare-ddns.py"
wget https://raw.githubusercontent.com/marcosepp/SynologyCloudflareDDNS/master/cloudflare-ddns.py -O /usr/syno/bin/ddns/cloudflare-ddns.py
echo "Done!"

echo "Addind exec priv to /usr/syno/bin/ddns/cloudflare-ddns.py"
chmod 0755 /usr/syno/bin/ddns/cloudflare-ddns.py
echo "Done!"
