import json
import time
import paramiko
import os
import sys
#coding=utf-8
# serverIP = "114.115.141.215"
# port = 22
# username = "root"
# password = "hag123456!"
# tomcatWebappsPath = ""
# warName = ""


def execute():

    json = resolveJson("./config.json")
    if isinstance(json, list):
        for item in json:
            executeOnce(item)
            print('\r\r\r')
            print('==========================================')
            print('\r\r')
    else:
        executeOnce(json)

    print("执行完毕，请按回车键退出...")
    input()
    os._exit(0)


def executeOnce(json):
    serverIP = json['serverIP']
    port = json['port']
    username = json['username']
    password = json['password']
    tomcatWebappsPath = json['tomcatWebappsPath']
    warName = json['warName']

    try:
        print("开始时间 : %s" % time.ctime())
        con = connect(serverIP, port, username, password)
        if  con==None:
            raise Exception(f'连接${serverIP}失败！')
        resolveJson("./config.json")
        exec_commands(con, f'cd {tomcatWebappsPath} && rm -rf {warName.split(".")[0]}*')
        copy_module(con, warName, f'{tomcatWebappsPath}/{warName}')
        exec_commands(con, 'systemctl stop tomcat8s')
        exec_commands(con, 'systemctl start tomcat8s')
        print("结束时间 : %s" % time.ctime())

    except Exception as e:
        print("异常 : %s" % e)
        print("结束时间 : %s" % time.ctime())

# 读取外部配置文件
def resolveJson(path):
    file = open(path, "rb")
    fileJson = json.load(file)
    # serverIP = fileJson["serverIP"]
    # port = fileJson["port"]
    # username = fileJson["username"]
    # password = fileJson["password"]
    # tomcatWebappsPath = fileJson["tomcatWebappsPath"]
    # warName = fileJson["warName"]
    return fileJson


# connect函数中，参数是一个主机的IP地址或者是主机名称，
# 在执行这个方法之后，如果成功的连接到服务器，那么就会返回一个sshclient对象
def connect(serverIP,port,username,password):
    print(f"连接：{serverIP}...")
    # 建立一个SSHClient的对象
    ssh = paramiko.SSHClient()

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 然后就尝试连接服务器，在连接服务器的时候，可以使用两种方式：
        # 一种方式是使用秘钥的方式，也就是参数look_for_keys。
        # 也可以直接使用密码的方式，也就是直接使用参数password，从而最后返回一个连接的对象。
        # ssh.connect(host,username='root',allow_agent=True,look_for_keys=True)
        ssh.connect(hostname=serverIP, port=port, username=username,
                    password=password)
        return ssh
    except:
        return None


# 在参数中，一个是args，一个outpath，args表示命令的参数，而outpath表示为可执行文件的路径，
# 例如/usr/bin/ls -l。在其中outpath也就是/usr/bin/ls ,而参数为-l
# 这个方法主要是用来组合命令，将分开的参数作为命令的一部分进行组装。
def command(args, outpath):
    cmd = '%s %s' % (outpath, args)
    return cmd


# 传入的参数一个为连接的对象conn，一个为需要执行的命令cmd，
# 最后得到执行的结果，也就是stdout.read（），最后返回得到的结果
def exec_commands(conn, cmd):
    print(f"执行：${cmd}")
    stdin, stdout, stderr = conn.exec_command(cmd)
    results = stdout.read()
    return results


def progress_bar(transferred, toBeTransferred, suffix=''):
    # print "Transferred: {0}\tOut of: {1}".format(transferred, toBeTransferred)
    bar_len = 60
    filled_len = int(round(bar_len * transferred / float(toBeTransferred)))
    percents = round(100.0 * transferred / float(toBeTransferred), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('\r[%s] %s%s ...%s' % (bar, percents, '%', suffix))
    if percents == 100:
        sys.stdout.write('\r')
    else:
        sys.stdout.flush()

    # print('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix),flush=True)


# 上传文件50|ftp|.|put|(|inpath|,| |outpath|)	50|ftp|.|put|(|inpath|,| |outpath|)	50|ftp|.|put|(|inpath|,| |outpath|)	50|ftp|.|put|(|inpath|,| |outpath|)
# 一个是连接对象conn，一个是上传的文件名称，一个上传之后的文件名称，在此必须写入完整的文件名称包括路径。
# 做法主要是打开一个sftp对象，然后使用put方法进行上传文件，最后关闭sftp连接，最后返回一个上传的文件名称的完整路径
def copy_module(conn, inpath, outpath):
    print(f"拷贝：{inpath}到{outpath}")
    ftp = conn.open_sftp()
    ftp.put(inpath, outpath, callback=progress_bar)
    ftp.close()
    return outpath


# 执行命令得到结果
# 首先，进行连接服务器，得到一个连接对象，
# 如果连接不成功，那么返回主机名和None，表示没有连接成功，
# 如果连接成功，那么修改文件的执行权限，从而可以执行文件，
# 然后得到执行的命令，
# 最后，进行执行命令，得到结果，
# 将结果用json格式表示返回，从而结果能得到一个美观的json格式，
# 最后和主机名一起返回相关的信息
def excutor(host, outpath, args):
    conn = connect(host)
    if not conn:
        return [host, None]
    # exec_commands(conn,'chmod +x %s' % outpath)
    cmd = command(args, outpath)
    result = exec_commands(conn, cmd)
    return [host, result]


# 第一步测试命令执行，
# 第二步测试上传文件，
# 第三部测试修改上传文件的权限。
if __name__ == '__main__':
    execute()
# print(json.dumps(excutor(serverIP, 'ls', ' -l'), indent=4, sort_keys=True))

# print(exec_commands(connect(serverIP),
#                     'cd /var/lib/tomcat8/webapps/HAGFrame/WEB-INF/classes && sed -i "s#^url=.*#url=jdbc:mysql://127.0.0.1:8809/frame?useUnicode=true\&characterEncoding=utf8\&characterSetResults=utf8\&autoReconnect=true\&failOverReadOnly=false\&useSSL=false\n#g"  dbconfig.properties'))
# print(exec_commands(connect(serverIP),
#                     'cd /var/lib/tomcat8/webapps/HAGFrame/WEB-INF/classes && sed -i "s#^mongodb.url=.*#mongodb.url=127.0.0.1:27017\n#g"  mongodb.properties'))
