#!/bin/bash
cd /opt/vpn2
./vpn_checker

# Добавляем заголовок в vpn.txt
DATE=$(date +'%d.%m.%Y %H:%M')
HEADER="#profile-title: LLxickVPN
#support-url: https://t.me/LLxick2
#profile-update-interval: 1
#announce: UPD: $DATE | обновление каждые 15 мин | тгк @LLxickVPN
"
echo "$HEADER$(cat vpn.txt)" > vpn.txt

git add -A
git commit -m "update $DATE"
git push
