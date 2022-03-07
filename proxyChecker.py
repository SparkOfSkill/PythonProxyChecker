# SOCKS5 Proxy checker
#   by Spark of Skill
#
import sys, requests, datetime
from threading import Thread
from colorama import Fore, Style
from operator import itemgetter

date = str(datetime.datetime.now().replace(microsecond = 0))
date = date.replace(' ', '-').replace(':', '-')

# File with proxies to check
proxiesFile = 'proxylist.txt'

# File to save active proxies
outputPath = './Output/'
aliveFile = 'alive-' + date +'.txt'
pcsAliveFile = 'pcs-' + aliveFile   #ready to use proxychains format

reqTimeout = 10
proxyType = 'socks5' # type of proxies to check ('socks5' or 'https')

proxylist = []
workingProxies = []
threads = []

def import_proxies(proxiesFile):
    print(Fore.YELLOW + '[IMPORTING]' + Fore.RESET + ' Proxylist from ' + proxiesFile)
    proxies = open(proxiesFile)
    for x in proxies:
        tmp = x.strip().split(":")
        ip = tmp[0]
        port = tmp[1]

        proxy = {"ip": ip, "port": port}
        if proxy not in proxylist:
            proxylist.append(proxy)
    proxies.close()
    print(Fore.GREEN + '[IMPORTED] ' + Fore.RESET + ' Proxylist')
    return

#   Sorting proxylist by ping
def sortProxyList(workingProxies):
    workingProxiesSorted = sorted(workingProxies, key=itemgetter('ping'))
    return workingProxiesSorted

#   Saves proxylist in a file
def saveActive(filePath, workingProxies):
    print(Fore.YELLOW + '[SAVING] ' + Fore.RESET + ' Active proxies...')
    alive = open(filePath, 'w')
    for proxy in workingProxies:
        alive.write(proxy['ip'] + ':' + proxy['port']+'\n')
    alive.close()
    print(Fore.GREEN + '[SAVED]' + Style.RESET_ALL + ' Active proxies in ' + '"' + filePath + '".')
    return

#   Saves proxylist in proxychains format in a file
def saveActiveProxychainsFormat(filePath, workingProxies):
    print(Fore.YELLOW + '[SAVING] ' + Fore.RESET + 'Active proxies in proxychains format...')
    alive = open(outputPath+pcsAliveFile, 'w')
    for proxy in workingProxies:
        alive.write(proxyType + ' ' + proxy['ip'] + ' ' + proxy['port'] + '      #' + proxy['external_ip'] +' - ' + proxy['cc'] + ' - ' + proxy['country'] + ' - ' + str(proxy['ping']) +'ms\n')
    alive.close()
    print(Fore.GREEN + '[SAVED]' + Fore.RESET + ' Active proxies in pcs-format in ' + '"' + pcsAliveFile + '".')
    return

#   Checks if a proxy is working, gets information about the proxy and add its to the working proxy list
def check_proxy(proxy):
    try:
        print(Fore.YELLOW + '[CHECKING]' + Fore.RESET + proxy['ip'] + ':' + proxy['port'])
        proxies = {'https': proxyType + '://' + proxy['ip'] + ':' + proxy['port']}
        req = requests.get('https://api.myip.com', proxies=proxies, timeout=reqTimeout)
        data = req.json()
        proxy['ping'] = req.elapsed.total_seconds()
        proxy['external_ip'] = str(data['ip'])
        proxy['country'] = str(data['country'])
        proxy['cc'] = str(data['cc'])
        print(Fore.CYAN + '[Alive] ' + Fore.RESET + proxy['ip'] + ':' + proxy['port'] + ' - ' + proxy['external_ip'] +' - ' + proxy['cc'] + ' - ' + proxy['country'] + ' - ' + str(req.elapsed.total_seconds()) + 'ms - ' + str(req.status_code))
        workingProxies.append(proxy)
    except requests.exceptions.RequestException as e:
        return e
    return True

#   Handles the checking of a whole proxy list
def check_proxyList():
    print(Fore.YELLOW + '[CHECKING - Proxylist]' + Fore.RESET)
    for proxy in proxylist:
        thread = Thread( target=check_proxy, args=(proxy, ))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
    print(Fore.GREEN + '[DONE CHECKING - Proxylist]' + Fore.RESET)
    return


import_proxies(proxiesFile)
check_proxyList()
print(Fore.RED + '[STATUS] ' + Fore.RESET + str(len(workingProxies)) + ' proxies from ' + str(len(proxylist)) + ' alive.')
workingProxies = sortProxyList(workingProxies)
saveActive(outputPath+aliveFile, workingProxies)
saveActiveProxychainsFormat(outputPath+aliveFile, workingProxies)
