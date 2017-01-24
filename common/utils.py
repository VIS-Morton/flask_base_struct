import struct
import socket


def ip2long(ip):
    """ip to unsigned long int"""
    return struct.unpack("!I", socket.inet_aton(ip))[0]


def long2ip(lint):
    """unsigned long int to ip"""
    return socket.inet_ntoa(struct.pack("!I", lint))