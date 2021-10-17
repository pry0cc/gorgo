# Gorgo
<small>The vertasile multi-threaded password sprayer built on the shoulders of giants.</small>
---
Gorgo is a fast and option-rich password sprayer for traditional network protocols. Gorgo multi-threads Medusa to distribute spraying in a way that Medusa cannot do out of the box. 

For example, Gorgo can generate username:password permutations ahead of time so that you can adjust the order by hand if needed. This file can also be split for distributed scanning such as use with [axiom](https://github.com/pry0cc/axiom).

## Why?
I built Gorgo because I wasn't a fan of the current tools that are out there for password spraying 'dumb' protocols in a smart way. I wanted to change that. 

# Usage
```
usage: gorgo.py [-h] [-x X] [-iL IL] [-H H] [-U U] [-P P] [--protocols PROTOCOLS] [--generate] [--threads THREADS] [-o O] [--run] [--random RANDOM]

optional arguments:
  -h, --help            show this help message and exit
  -x X                  Nmap file to scan for inputs
  -iL IL                Take pre-permutations as input (must be generated with -g)
  -H H                  Hosts to spray against.
  -U U                  Username file spray (username per newline)
  -P P                  Password file spray (username per newline)
  --protocols PROTOCOLS
                        Protocols to spray
  --generate            Only generate permutations
  --threads THREADS     Threads to spray
  -o O                  Output filename
  --run                 Run spray
  --random RANDOM       Randomize target list
```

## Custom List Generation
There are often times when you want to be very specific about what combinations you want to try. You may want to treat host types differently also. For example, you may only want to only try a few usernames for windows accounts, because of lockouts, whereas you might try more on Unix-like services such as SSH. 

By outputting the combinations into a CSV file, you can go in by hand and remove and tweak the file before running the scan. It also allows you to distribute it to an array of distributed workers - such as through axiom.

## Using --generate
```
./gorgo.py -U unix-usernames.txt -P passwords.txt -H hosts-unix.txt --protocols ftp:21,ssh:22 --generate -o perms_unix.csv
./gorgo.py -U windows-usernames.txt -P passwords.txt -H hosts-windows.txt --protocols smb:445,rdp:3389 --generate -o perms_windows.csv
./gorgo.py -U database-usernames.txt -P passwords.txt -H hosts-database.txt --protocols mssql:1433 --generate -o perms_db.csv

cat perms_unix.csv perms_windows.csv perms_db.csv > combo.csv

./gorgo.py -iL combo.csv -o spray.log
```

## Using -x
If you want to import nmap xml results, gorgo will map selected protocols to ports regardless of port numbers.
```
./gorgo.py -x nmap.xml -U usernames.txt -P passwords.txt -H hosts.txt --protocols ssh --generate -o perms.csv

./gorgo.py -iL perms.csv
```

## Using --run
You don't have to generate a CSV, you can go yolo mode if you want.

```
./gorgo.py -x nmap.xml -U usernames.txt -P passwords.txt --protocols ssh -o gorgo.log --run
./gorgo.py -U usernames.txt -P passwords.txt -H hosts.txt --protocols ssh:22,rdp:3389 -o gorgo.log --run
```

### Convert JSON output to CSV using Jq
```
cat gorgo.log.pwned | jq -r 'to_entries | [.[].value] | @csv'
```

