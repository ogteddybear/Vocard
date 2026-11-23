FROM mongo:8.0

# Fly's private network uses IPv6; bind MongoDB on both IPv4 and IPv6.
CMD ["mongod", "--ipv6", "--bind_ip_all"]
