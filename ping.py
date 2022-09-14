#!/usr/bin/python3
"""
输入扫描的网段：172.17.66.0
输入ip段首个地址1
输入ip段末端地址253
"""
from threading import Thread
import os, re


class ip_scan(Thread):

    def __init__(self, ip):
        super(ip_scan, self).__init__()
        self.success = -1
        self.ip = ip

    def run(self) -> None:
        ping_out = os.popen("ping -q -c2 " + self.ip, "r")
        while True:
            line = ping_out.readline()
            if not line: break
            n_recv = re.findall(recv_pat, line)
            if n_recv:
                self.success = int(n_recv[0])
        # end-while

    # end-def

    def status(self):
        if self.success == 0:
            return "no response!!"
        elif self.success == 1:
            return "alive,but 50 % package loss"
        elif self.success == 2:
            return "alive"
        else:
            return "some problem occur 囧!!"
    # end-def


# end-class

if __name__ == '__main__':
    ipPat = re.compile('(\d+\.\d+\.\d+\.)\d+')
    recv_pat = re.compile(r'(\d) received')

    ipRang = input("输入扫描的网段：")
    res = ipPat.findall(ipRang)
    net = res[0] if res else None

    s = e = 1

    if net:
        r = input("输入ip段首个地址:")
        if re.compile('\d+').findall(r):
            if int(r) < 0 or int(r) > 254:
                print("ipv4地址只限制1到254之间!!")
            else:
                s = int(r)
        # end-if
        r = input("输入ip段末端地址:")
        if re.compile('\d+').findall(r):
            if int(r) < 0 or int(r) > 254:
                print("ipv4地址只限制1到254之间!!")
            else:
                e = int(r)
    # end-if
    else:
        exit(0)

    result = []
    for n in range(s, e):
        ip = net + str(n)
        cur = ip_scan(ip)
        result.append(cur)
        cur.start()
    # end-for

    for c in result:
        c.join()
        print("Status from ", c.ip, "is ", c.status())
    # end-for
