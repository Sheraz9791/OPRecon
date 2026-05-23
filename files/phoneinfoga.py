#!/usr/bin/env python3

__version__ = 'v2.3.8-BETA'

try:
    import sys
    from colorama import Fore, Style
    import atexit
    import argparse
    import random
except KeyboardInterrupt:
    print('[!] Exiting.')
    sys.exit()
except:
    print('\033[91m[!] Missing requirements.\033[92m')
    sys.exit()

def banner():
    print("\033[92m    ___ _                       _____        __                   ")
    print("   / _ \ |__   ___  _ __   ___  \_   \_ __  / _| ___   __ _  __ _ ")
    print("  / /_)/ '_ \ / _ \| '_ \ / _ \  / /\/ '_ \| |_ / _ \ / _` |/ _` |")
    print(" / ___/| | | | (_) | | | |  __/\/ /_ | | | |  _| (_) | (_| | (_| |")
    print(" \/    |_| |_|\___/|_| |_|\___\____/ |_| |_|_|  \___/ \__, |\__,_|")
    print("                                                      |___/       ")
    print(" PhoneInfoga version {}".format(__version__))
    print(" Coded by Charon IV")
    print(" Modified by @AbirHasan2005")
    print("\n")

banner()

if sys.version_info[0] < 3:
    print("\033[1m\033[93m(!) Please run the tool using Python 3" + Style.RESET_ALL)
    sys.exit()

parser = argparse.ArgumentParser(
    description="Advanced information gathering tool for phone numbers",
    usage='%(prog)s -n <number> [options]'
)

parser.add_argument(
    '-n', '--number',
    metavar='number',
    type=str,
    help='The phone number to scan'
)

parser.add_argument(
    '-i', '--input',
    metavar="input_file",
    type=argparse.FileType('r'),
    help='Phone number list to scan'
)

parser.add_argument(
    '-o', '--output',
    metavar="output_file",
    type=argparse.FileType('w'),
    help='Output file'
)

parser.add_argument(
    '-s', '--scanner',
    metavar="scanner",
    default="all",
    type=str,
    help='Scanner to use'
)

parser.add_argument(
    '--osint',
    action='store_true',
    help='Use OSINT reconnaissance'
)

parser.add_argument(
    '-u', '--update',
    action='store_true',
    help='Update project'
)

args = parser.parse_args()

def resetColors():
    if not args.output:
        print(Style.RESET_ALL)

atexit.register(resetColors)

if not len(sys.argv) > 1:
    parser.print_help()
    sys.exit()

try:
    import time
    import hashlib
    import json
    import re
    import requests
    import urllib3
    from bs4 import BeautifulSoup
    import html5lib
    import phonenumbers
    from phonenumbers import carrier
    from phonenumbers import geocoder
    from phonenumbers import timezone
except KeyboardInterrupt:
    print('\033[91m[!] Exiting.')
    sys.exit()
except Exception as e:
    print('\033[91m[!] Missing requirements.\033[92m')
    print(e)
    sys.exit()

# =========================================
# FIXED urllib3 SSL CIPHER ERROR
# =========================================

requests.packages.urllib3.disable_warnings()

try:
    from urllib3.util import ssl_

    if hasattr(ssl_, "DEFAULT_CIPHERS"):
        ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'

except Exception:
    pass

try:
    import urllib3.contrib.pyopenssl

    if hasattr(urllib3.contrib.pyopenssl, "DEFAULT_SSL_CIPHER_LIST"):
        urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += ':HIGH:!DH:!aNULL'

except Exception:
    pass

# =========================================

scanners = ['any', 'all', 'numverify', 'ovh']

number = ''
localNumber = ''
internationalNumber = ''
numberCountryCode = ''
numberCountry = ''

def formatNumber(InputNumber):
    return re.sub("(?:\+)?(?:[^[0-9]*)", "", InputNumber)

def localScan(InputNumber):
    global number
    global localNumber
    global internationalNumber
    global numberCountryCode
    global numberCountry

    print(code_info + 'Running local scan ...')

    FormattedPhoneNumber = "+" + formatNumber(InputNumber)

    try:
        PhoneNumberObject = phonenumbers.parse(FormattedPhoneNumber, None)

    except:
        return False

    else:
        if not phonenumbers.is_valid_number(PhoneNumberObject):
            return False

        number = phonenumbers.format_number(
            PhoneNumberObject,
            phonenumbers.PhoneNumberFormat.E164
        ).replace('+', '')

        numberCountryCode = phonenumbers.format_number(
            PhoneNumberObject,
            phonenumbers.PhoneNumberFormat.INTERNATIONAL
        ).split(' ')[0]

        localNumber = phonenumbers.format_number(
            PhoneNumberObject,
            phonenumbers.PhoneNumberFormat.E164
        ).replace(numberCountryCode, '')

        internationalNumber = phonenumbers.format_number(
            PhoneNumberObject,
            phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )

        print(code_result + 'International format: {}'.format(internationalNumber))
        print(code_result + 'Local format: 0{}'.format(localNumber))
        print(code_result + 'Country code: {}'.format(numberCountryCode))
        print(code_result + 'Location: {}'.format(
            geocoder.description_for_number(PhoneNumberObject, "en")
        ))
        print(code_result + 'Carrier: {}'.format(
            carrier.name_for_number(PhoneNumberObject, 'en')
        ))

        for timezoneResult in timezone.time_zones_for_number(PhoneNumberObject):
            print(code_result + 'Timezone: {}'.format(timezoneResult))

        if phonenumbers.is_possible_number(PhoneNumberObject):
            print(code_info + 'The number is valid and possible.')
        else:
            print(code_warning + 'The number is valid but might not be possible.')

def scanNumber(InputNumber):

    print(
        code_title +
        "[!] ---- Fetching informations for {} ---- [!]".format(
            formatNumber(InputNumber)
        )
    )

    localScan(InputNumber)

    global number

    if not number:
        print(
            code_error +
            "Error: number {} is not valid.".format(
                formatNumber(InputNumber)
            )
        )
        sys.exit()

    print(code_info + "Scan finished!")
    print('\n' + Style.RESET_ALL)

try:

    if args.output:
        code_info = '[*] '
        code_warning = '(!) '
        code_result = '[+] '
        code_error = '[!] '
        code_title = ''

        sys.stdout = args.output
        banner()

    else:
        code_info = Fore.RESET + Style.BRIGHT + '[*] '
        code_warning = Fore.YELLOW + Style.BRIGHT + '(!) '
        code_result = Fore.GREEN + Style.BRIGHT + '[+] '
        code_error = Fore.RED + Style.BRIGHT + '[!] '
        code_title = Fore.YELLOW + Style.BRIGHT

    if not args.scanner in scanners:
        print(code_error + "Error: scanner doesn't exist.")
        sys.exit()

    if args.number:
        scanNumber(args.number)

    elif args.input:
        for line in args.input.readlines():
            scanNumber(line)

    if args.output:
        args.output.close()

except KeyboardInterrupt:
    print("\n" + code_error + "Scan interrupted. Good bye!")
    sys.exit()
