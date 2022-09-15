import sys, os, getopt
import paramiko
import threading
import configparser
from scp import SCPClient
'''
The script supports remote command execution, file upload and file download;
the host can be a target or multiple hosts;
the single host uses the - H IP - U username - P password parameter;
the multiple hosts use the format of the configuration file host.ini;
the content of the host.ini file takes [host] as the first line,
the second line uses the format of id = IP, username, passwd.
Examples are as follows:
-H :host ip -H 192.168.11.11
-U :-U uername
-P :-P passwd
-f :config file host.ini配置如下
[hosts]
###hostname=ip,username,password
1 = 192.168.152.131,root,123456
2 = 192.168.152.132,autotest,123456
3 = 192.168.152.133,root,123456
4 = 192.168.152.134,root,123456
-c :command -c 'ls ~/'
-p :local filename -u ：remote path
-g :remote filename -d ：local path
Usage :python3 remote_cmd.py -f /home/host.ini -c 'pwd' #remote hosts execute command , the list of host in the host.ini
python3 remote_cmd.py -f /home/conf/host.ini -p test.py -u /home/autotest ##Upload files to remote host
python3 remote_cmd.py -H '192.168.152.131' -U 'autotest' -P 'passwd' -g ~/Videos.tar -d /home/autotest/test/ ###get remote file download /home/autotest/tests
python3 remote_cmd.py -H '192.168.152.131' -U 'autotest' -P 'passwd' -c 'pwd' ##remotehost execute command
'''

def getConnection(ip, username, password, command, port=22, local_filename="",
                  remotepath="", remote_filename="", localpath=""):
    """
    :param localpath:
    :param remote_filename:
    :param remotepath:
    :param command:
    :param local_filename:
    :param ip: 服务器的ip
    :param username:  服务器的用户名称
    :param password:  服务器的密码
    :param CMD:  服务器的命令
    :param port:  服务器的端口
    """
    ssh = paramiko.SSHClient()
    policy = paramiko.AutoAddPolicy()
    ssh.set_missing_host_key_policy(policy)
    ssh.connect(
        hostname=ip,  # 服务器的ip
        port=port,  # 服务器的端口
        username=username,  # 服务器的用户名
        password=password  # 用户名对应的密码
    )

    # 传输文件
    if command:
        stdin, stdout, stderr = ssh.exec_command(command)
        result = stdout.read().decode()
        error = stderr.read().decode()
        print("+++++++++++++++++++++++start++++++++++++++++++++")
        print("[connect success] | ip : %s" % ip)
        print("result: %s" % result)
        if error != " ":
            print("error: %s" % error)
        print("+++++++++++++++++++++++done++++++++++++++++++++")
    if all([local_filename, remotepath]):
        scpclient = SCPClient(ssh.get_transport(), socket_timeout=15.0)
        scpclient.put(local_filename, remotepath)
    if all([remote_filename, localpath]):
        scpclient = SCPClient(ssh.get_transport(), socket_timeout=15.0)
        scpclient.get(remote_filename, localpath)
    ssh.close()


# 读取配置文件
def read_conf(config):
    cf = configparser.ConfigParser()
    filename = cf.read(config)
    opt = cf.options("hosts")
    host_list = []

    for ooo in opt:
        tmp_host = cf.get("hosts", ooo)
        host_list.append(tmp_host.split(","))
    return host_list


# 采用多线程
def multi_thread(thread_target, args_lists):
    thread_list = []
    for args_tuple in args_lists:
        thread = threading.Thread(target=thread_target, args=args_tuple)
        thread_list.append(thread)
    for tmp_argv in thread_list:
        tmp_argv.start()
    for tmp_argv in thread_list:
        tmp_argv.join()


def main():
    # 初始化参数
    ip = ""
    username = ""
    password = ""
    config = ""
    conf = ""
    command = ""
    local_filename = ""
    remotepath = ""
    remote_filename = ""
    localpath = ""
    # 获取外参
    opts, args = getopt.getopt(sys.argv[1:], "hH:U:P:f:c:p:u:g:d:",
                               ["help", "host=", "username", "password", "conf", "command", "local_filename",
                                "remotepath", "remote_filename", "localpath"])
    for o, a in opts:
        if o in ("-h", "--help") or not o:
            print('Usage:python3 remote_cmd.py  [options]... ')
            print("""Script supports remote command execution, file upload and file download
                The script supports remote command execution, file upload and file download;
                the host can be a target or multiple hosts; 
                the single host uses the - H IP - U username - P password parameter; 
                the multiple hosts use the format of the configuration file host.ini; 
                the content of the host.ini file takes [host] as the first line, 
                the second line uses the format of id = IP, username, passwd. 
                Examples are as follows:
              -H  :host ip -H 192.168.11.11
              -U  :-U uername  
              -P  :-P passwd
              -f  :config file host.ini配置如下
                  [hosts]
                  ###hostname=ip,username,password
                  1 = 192.168.152.131,root,123456
                  2 = 192.168.152.132,autotest,123456
                  3 = 192.168.152.133,root,123456
                  4 = 192.168.152.134,root,123456
              -c  :command  -c 'ls ~/'
              -p  :local filename -u  ：remote path
              -g  :remote filename  -d  ：local path
            Usage :python3 remote_cmd.py -f /home/host.ini -c 'pwd' #remote hosts execute command , the list of host in the host.ini
                    python3 remote_cmd.py -f /home/conf/host.ini -p test.py -u /home/autotest ##Upload files to remote host
                    python3 remote_cmd.py -H '192.168.152.131' -U 'autotest' -P 'qiaoyi'  -g ~/Videos.tar -d /home/autotest/test/ ###get remote file download /home/autotest/tests
                    python3 remote_cmd.py -H '192.168.152.131' -U 'autotest' -P 'qiaoyi' -c 'pwd' ##remotehost execute command
            """)
            sys.exit()
        if o in ("-H", "--host"):
            ip = a
        # print(ip)
        if o in ("-U", "--username"):
            username = a
        # print(username)
        if o in ("-P", "--password"):
            password = a
        # print(password)
        if o in ("-f", "--conf"):
            config = a
            # print(config)
        if o in ("-c", "--command"):
            command = a
            # print(command)
        if o in ("-p", "--local_filename"):
            local_filename = a
        #  print(local_filename)
        if o in ("-u", "--remotepath"):
            remotepath = a
        #  print(remotepath)
        if o in ("-g", "--remote_filename"):
            remote_filename = a
            # print(remote_filename)
        if o in ("-d", "--localpath"):
            localpath = a
        # print(localpath)
    # 判断是读参数还是读配置文件
    host_list = []
    if all([ip, username, password]) and not config:
        host_list = [(ip, username, password)]
    elif config:
        host_list = read_conf(config)
    args_lists = []
    if not host_list:
        print("Usage：python3 remote_cmd.py -h")
    for ip, username, password in host_list:
        args_lists.append(
            [ip.strip(), username.strip(), password.strip(), command, 22, local_filename, remotepath, remote_filename,
             localpath])
    multi_thread(getConnection, args_lists)


if __name__ == "__main__":
    main()