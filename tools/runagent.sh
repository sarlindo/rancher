#sudo docker run -d -p 8400:8400 -p 8500:8500 -p 8600:53/udp --name node2 -h node2 progrium/consul -join 172.17.0.2
sudo docker run -d --name consul -h $HOSTNAME -v /mnt:/data \
    -p 192.168.33.11:8300:8300 \
    -p 192.168.33.11:8301:8301 \
    -p 192.168.33.11:8301:8301/udp \
    -p 192.168.33.11:8302:8302 \
    -p 192.168.33.11:8302:8302/udp \
    -p 192.168.33.11:8400:8400 \
    -p 192.168.33.11:8500:8500 \
    -p 172.17.0.1:153:53/udp \
    progrium/consul -advertise 192.168.33.11 -join 192.168.33.10

