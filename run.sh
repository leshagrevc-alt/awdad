#!/bin/bash
cd /opt/vpn2
./vpn_checker
git add -A
git commit -m "update $(date +'%d.%m %H:%M')"
git push
