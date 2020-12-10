#!/usr/bin/env python3
# coding: UTF-8

import argparse
import glob
import os
import shlex
import subprocess
import traceback

import colorama
from colorama import Fore, Back, Style

def get_adb_path():
    home_dir = os.environ['HOME']
    adb_path = glob.glob(home_dir + '/Library/Android/sdk/platform-tools/adb')[0]
    return adb_path

def get_network_id():
    adb_path = get_adb_path()
    dumpsys_cmd = [adb_path, 'shell', 'su', '-c', '"dumpsys netd"']
    dumpsys_proc = subprocess.Popen(dumpsys_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outs, errs = dumpsys_proc.communicate()

    if (errs is not None) and (len(errs) != 0):
        errs = errs.decode('ascii').replace('\n', '')
        raise Exception(errs)

    outs = outs.decode('ascii')
    start = outs.find('Default network: ')
    network_id = outs[start+(len('Default network: ')): start + outs[start:].find('\n')]
    return network_id

def cmd_manual(args):
    adb_path = get_adb_path()
    start_cmd = [adb_path, 'shell', 'am', 'start']
    start_cmd.append('--activity-clear-top')
    start_cmd.append('-a')
    start_cmd.append('android.settings.WIRELESS_SETTINGS')

    start_proc = subprocess.Popen(start_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outs, errs = start_proc.communicate()

    if (errs is not None) and (len(errs) != 0):
        errs = errs.decode('ascii').replace('\n', '')
        print(Fore.RED + errs)
        return

    if (outs is not None) and (len(outs) != 0):
        print(outs.decode('ascii').replace('\n', ''))

def cmd_proxy(args):
    adb_path = get_adb_path()
    put_cmd = [adb_path, 'shell', 'settings', 'put', 'global', 'http_proxy']
    proxy_addr = shlex.quote(args.proxy_addr)
    put_cmd.append(proxy_addr)

    put_proc = subprocess.Popen(put_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outs, errs = put_proc.communicate()

    if (errs is not None) and (len(errs) != 0):
        errs = errs.decode('ascii').replace('\n', '')
        print(Fore.RED + errs)
        return 

    print(Fore.CYAN + 'Local proxy has been set up')

def cmd_dns(args):
    network_id = ''
    try:
        network_id = get_network_id()
    except Exception as e:
        print(Fore.RED + traceback.format_exception_only(type(e), e)[0][11:-1])
        return
    adb_path = get_adb_path()
    ndc_cmd = [adb_path, 'shell', 'su', '-c']
    dns_addr = shlex.quote(args.dns_addr)
    ndc_cmd.append('"ndc resolver setnetdns ' + network_id + ' \'\' ' + dns_addr + '"')
    ndc_proc = subprocess.Popen(ndc_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outs, errs = ndc_proc.communicate()
    if (errs is not None) and (len(errs) != 0):
        errs = errs.decode('ascii').replace('\n', '')
        print(Fore.RED + errs)
        return 

    if (outs is not None) and (len(outs) != 0):
        outs = outs.decode('ascii').replace('\n', '')
        print(Fore.CYAN + outs)

def cmd_clear(args):
    adb_path = get_adb_path()
    get_cmd = [adb_path, 'shell', 'settings', 'get', 'global', 'http_proxy']
    settings_proc = subprocess.Popen(get_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outs, errs = settings_proc.communicate()

    if (errs is not None) and (len(errs) != 0):
        errs = errs.decode('ascii').replace('\n', '')
        print(Fore.RED + errs)
        return 

    outs = outs.decode('ascii')
    if (outs != 'null') and (outs != ':0\n'):
        put_cmd = [adb_path, 'shell', 'settings', 'put', 'global', 'http_proxy']
        put_cmd.append(':0')
        put_proc = subprocess.Popen(put_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        outs, errs = put_proc.communicate()

        if (errs is not None) and (len(errs) != 0):
            errs = errs.decode('ascii')
            raise Exception(errs)
        
        print(Fore.CYAN + 'Cleared local proxy settings!!')
    else:
        print(Fore.RED + 'Local proxy is not configured...')

    network_id = ''
    try:
        network_id = get_network_id()
    except Exception as e:
        # adb: no devices/emulators found
        # need root privileges to clear the dns settings
        return
    adb_path = get_adb_path()
    ndc_cmd = [adb_path, 'shell', 'su', '-c']
    ndc_cmd.append('"ndc resolver setnetdns ' + network_id + ' \'\' 8.8.8.8 8.8.4.4"')
    ndc_proc = subprocess.Popen(ndc_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outs, errs = ndc_proc.communicate()
    if (errs is not None) and (len(errs) != 0):
        errs = errs.decode('ascii')
        raise Exception(errs)

    print(Fore.CYAN + 'Cleared local DNS settings!!')

def main():
    colorama.init(autoreset=True)
    parser = argparse.ArgumentParser(description='Android PROXy setting tool')
    subparsers = parser.add_subparsers()

    parser_manual = subparsers.add_parser('manual', aliases=['m'], help='Access WiFi settings page on GUI')
    parser_manual.set_defaults(handler=cmd_manual)

    parser_proxy = subparsers.add_parser('proxy', aliases=['p'], help='Set local proxy server')
    parser_proxy.add_argument('proxy_addr', help='local proxy address')
    parser_proxy.set_defaults(handler=cmd_proxy)

    parser_dns = subparsers.add_parser('dns', aliases=['d'], help='Set local DNS server(rooted device only)')
    parser_dns.add_argument('dns_addr', help='local DNS address')
    parser_dns.set_defaults(handler=cmd_dns)

    parser_clear = subparsers.add_parser('clear', aliases=['c', 'cl'], help='Clear local proxy/DNS setting')
    parser_clear.set_defaults(handler=cmd_clear)

    args = parser.parse_args()
    if hasattr(args, 'handler'):
        args.handler(args)
    else:
        parser.print_help()
