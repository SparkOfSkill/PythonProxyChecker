# Proxy checking tool
#
#
#
import sys
import urllib.request, requests, socket
from threading import Thread

# File with proxies to check
proxiesFile = "proxylist.txt"

# File to save active proxies
aliveFile = "alive.txt"
pcsAliveFile = 'pcs-' + aliveFile
aliveMode = 'w' # w=write, a=append

proxylist = []
workingProxies = []
threads = []

socket.setdefaulttimeout(15)

def import_proxies(proxiesFile):
    print("Importing Proxylist...")
    proxies = open(proxiesFile)
    for x in proxies:
        y = x.strip().split(":")
        ip = y[0]
        port = y[1]

        proxy = {"ip": ip, "port": port}
        proxylist.append(proxy)
    proxies.close()
    print("Proxylist imported.")
    return

def saveActive():
    print('Saving active proxies...')
    alive = open(aliveFile, aliveMode)
    for proxy in workingProxies:
        alive.write(proxy['ip'] + ':' + proxy['port']+'\n')
    alive.close()
    print('Active proxies saved in ' + '"' + aliveFile + '".')
    return

def saveActiveProxychainsFormat():
    print('Saving active proxies in proxychains format...')
    alive = open(pcsAliveFile, aliveMode)
    for proxy in workingProxies:
        alive.write('socks5 ' + proxy['ip'] + ' ' + proxy['port'] + '      #' + proxy['external_ip'] +' - ' + proxy['cc'] + ' - ' + proxy['country'] + ' - ' + str(proxy['ping']) +'\n')
    alive.close()
    print('Active proxies in pcs-format saved in ' + '"' + pcsAliveFile + '".')
    return

def check_proxy(proxy):
    try:
        print("Checking: " + proxy['ip'] + ':' + proxy['port'])
        proxies = {'https': "socks5://" + proxy['ip'] + ':' + proxy['port']}
        req = requests.get('https://api.myip.com', proxies=proxies, timeout=10)
        data = req.json()
        proxy['ping'] = req.elapsed.total_seconds()
        proxy['external_ip'] = str(data['ip'])
        proxy['country'] = str(data['country'])
        proxy['cc'] = str(data['cc'])
        #print(req.text)
        print(proxy['ip'] + ':' + proxy['port'] + ' - ' + proxy['external_ip'] +' - ' + proxy['cc'] + ' - ' + proxy['country'] + ' - ' + str(req.elapsed.total_seconds()) + ' - ' + str(req.status_code))
        workingProxies.append(proxy)
    except requests.exceptions.RequestException as e:
        return e
    return 0

def check_proxyList():
    print("Checking Proxylist...")
    for proxy in proxylist:
        thread = Thread( target=check_proxy, args=(proxy, ))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
    print("Done checking Proxylist!")
    return


import_proxies(proxiesFile)
check_proxyList()
saveActive()
saveActiveProxychainsFormat()
