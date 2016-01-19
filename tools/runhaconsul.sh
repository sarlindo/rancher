sudo docker run --net=host --name=haproxy -d -e HAPROXY_MODE=consul -e HAPROXY_DOMAIN=192.168.33.10.xip.io -e CONSUL_CONNECT=192.168.33.10:8500 sarlindo/haproxy-consul:v1.0.0
