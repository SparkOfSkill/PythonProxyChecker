# SOCKS5 Proxy checker
#   by Spark of Skill
#
import sys, requests
from threading import Thread

# File with proxies to check
proxiesFile = 'proxylist.txt'

# File to save active proxies
aliveFile = 'alive.txt'
pcsAliveFile = 'pcs-' + aliveFile   #ready to use proxychains format
aliveMode = 'w' # w=write, a=append

reqTimeout = 10
proxyType = 'socks5' # type of proxies to check ('socks5' or 'https')

proxylist = []
workingProxies = []
threads = []

def import_proxies(proxiesFile):
    print('[IMPORTING] Proxylist from ' + proxiesFile)
    proxies = open(proxiesFile)
    for x in proxies:
        tmp = x.strip().split(":")
        ip = tmp[0]
        port = tmp[1]

        proxy = {"ip": ip, "port": port}
        proxylist.append(proxy)
    proxies.close()
    print('[IMPORTED] Proxylist')
    return

def saveActive():
    print('[SAVING] Active proxies...')
    alive = open('./'+aliveFile, aliveMode)
    for proxy in workingProxies:
        alive.write(proxy['ip'] + ':' + proxy['port']+'\n')
    alive.close()
    print('[SAVED] Active proxies in ' + '"' + aliveFile + '".')
    return

def saveActiveProxychainsFormat():
    print('[SAVING] Active proxies in proxychains format...')
    alive = open('./'+pcsAliveFile, aliveMode)
    for proxy in workingProxies:
        alive.write(proxyType + ' ' + proxy['ip'] + ' ' + proxy['port'] + '      #' + proxy['external_ip'] +' - ' + proxy['cc'] + ' - ' + proxy['country'] + ' - ' + str(proxy['ping']) +'ms\n')
    alive.close()
    print('[SAVED] Active proxies in pcs-format in ' + '"' + pcsAliveFile + '".')
    return

def check_proxy(proxy):
    try:
        print('[CHECKING]' + proxy['ip'] + ':' + proxy['port'])
        proxies = {'https': proxyType + '://' + proxy['ip'] + ':' + proxy['port']}
        req = requests.get('https://api.myip.com', proxies=proxies, timeout=reqTimeout)
        data = req.json()
        proxy['ping'] = req.elapsed.total_seconds()
        proxy['external_ip'] = str(data['ip'])
        proxy['country'] = str(data['country'])
        proxy['cc'] = str(data['cc'])
        print('[Alive] ' + proxy['ip'] + ':' + proxy['port'] + ' - ' + proxy['external_ip'] +' - ' + proxy['cc'] + ' - ' + proxy['country'] + ' - ' + str(req.elapsed.total_seconds()) + 'ms - ' + str(req.status_code))
        workingProxies.append(proxy)
    except requests.exceptions.RequestException as e:
        return e
    return True

def check_proxyList():
    print('[CHECKING - Proxylist]')
    for proxy in proxylist:
        thread = Thread( target=check_proxy, args=(proxy, ))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
    print('[DONE CHECKING - Proxylist]')
    return


import_proxies(proxiesFile)
check_proxyList()
print('[STATUS] ' + str(len(workingProxies)) + ' proxies from ' + str(len(proxylist)) + ' alive.')
saveActive()
saveActiveProxychainsFormat()
