#sudo docker run -d -p 8400:8400 -p 8500:8500 -p 8600:53/udp -h node1 progrium/consul -server -bootstrap-expect 1

sudo docker run -d --name consul -h $HOSTNAME -v /mnt:/data \
    -p 192.168.33.10:8300:8300 \
    -p 192.168.33.10:8301:8301 \
    -p 192.168.33.10:8301:8301/udp \
    -p 192.168.33.10:8302:8302 \
    -p 192.168.33.10:8302:8302/udp \
    -p 192.168.33.10:8400:8400 \
    -p 192.168.33.10:8500:8500 \
    -p 172.17.0.1:153:53/udp \
    progrium/consul -server -advertise 192.168.33.10 -bootstrap-expect 1 -ui-dir /ui 
