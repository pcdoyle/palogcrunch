#!/usr/bin/env python3
"""
Palo Alto Log Cruncher

This program takes in a CSV file of Palo Alto logs and reduces the log size by removing columns and deduplicating the logs.
It will also optionally perform a DNS lookup on the IP address and write the hostname to a new column.

Author: Patrick Doyle (pdoyle@glaciermedia.ca)
Date: 2022-12-05
Version: 0.2.6

Check requirements.txt for required Python modules.
Use config.yml to configure the script.
"""
# PyYAML Configuration Parsing Module
import yaml
# Pandas CSV Manipulation Module
import pandas as pd
# IP Address Validation Module
from ipaddress import ip_address, IPv4Address
# Error Analysis Module
import traceback
# Python DNS Module
import dns.resolver, dns.reversename

# Configuration file location for the program: (Default is config.yml in the same directory as the script.)
config_file = "config.yml"

def log_crunch(input,output,dedupe_enabled,dedupe_column,dropna_enabled,drop_enabled,drop,ns_enabled,ns_from,ns_to):
    """
    log_crunch takes in log information and reduces it as specified in the config.yml file.

    :param input: The input file path as defined in config.yml
    :param ouput: The output file path as defined in config.yml
    :param dedupe_enabled: Deduplication enabled as defined in config.yml (true/false)
    :param dedupe_column: The column header to deduplicate on as defined in config.yml
    :param dropna_enabled: Drop empty rows enabled as defined in config.yml (true/false)
    :param drop_enabled: Drop columns enabled as defined in config.yml (true/false)
    :param drop: The list of columns to drop as defined in config.yml
    :param ns_enabled: DNS Lookup enabled as defined in config.yml (true/false)
    :param ns_from: What column to perform the DNS lookup on as defined in config.yml
    :param ns_to: What column to write the DNS lookup result to as defined in config.yml
    :return: None
    """

    print("Cruncing",input,"file, this could take a while if the log file is large.")
    df = pd.read_csv(input)

    if dropna_enabled:
        print("Dropping empty rows is enabled, dropping all empty rows.")
        df.dropna(how='all', axis=1, inplace=True)
    else:
        print("Not dropping rows with empty cells.")

    if drop_enabled:
        print("Dropping columns is enabled, dropping the columns configured in",config_file)
        df.drop(drop, inplace=True, axis=1, errors='ignore')
    else:
        print("Dropping columns is disabled, not dropping any columns.")

    if dedupe_enabled:
        print("Deduplication is enabled, dropping duplicate entries on the",dedupe_column,"column.")
        df = df.drop_duplicates(subset=dedupe_column, keep='first')
    else:
        print("Deduplication is disabled, not dropping duplicate entries.")

    if ns_enabled:
        print("DNS Hostname lookup is enabled, attempting to resolve hostnames to the",ns_to,"column.")
        result = []
        for value in df[ns_from]:
            hostname = nslookup_ip(value)
            result.append(hostname)
        df[ns_to] = result
    else:
        print("DNS Hostname lookup is disabled, not attempting to resolve hostnames.")

    df.to_csv(output, encoding='utf-8', index=False)
    return

def validate_ip(address):
    """
    validate_ip takes in an IP address and determines if it is IPv4, IPv6, or not a valid IP at all.

    :param address: The IP address to validate.
    :return: "IPv4", "IPv6", or "NotIP"
    """

    try:
        return "IPv4" if type(ip_address(address)) is IPv4Address else "IPv6"
    except ValueError:
        return "NotIP"
    except:
        if debug_flag == True:
            print(traceback.format_exc())
        return "NotIP"

def nslookup_ip(host):
    """
    nslookup_ip takes in an IP address and performs a DNS lookup on it.
    
    :param host: The IP address to perform the DNS lookup on.
    :return: The hostname of the IP address or "Unable to Resolve" if the hostname cannot be resolved.
    """

    try:
        if validate_ip(host) == "IPv4":
            host = dns.reversename.from_address(host)
            output = str(dns.resolver.resolve(host,"PTR")[0])
            return(output)
        elif validate_ip(host) == "IPv6":
            return("Unable to Resolve IPv6")
        else:
            return("Unable to Resolve")           
    except: 
        if debug_flag == True:
            print(traceback.format_exc())
        return("Unable to Resolve")

def set_dns_server(address):
    """
    set_dns_server takes in an IP address and sets it as the DNS resolver for the program.
    
    :param address: The IP address to set as the DNS resolver.
    :return: True if the DNS resolver was set successfully, False if there was an error.
    """

    if (validate_ip(address) == "IPv4"):
        try:
            dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
            dns.resolver.default_resolver.nameservers = [address]
            resolver = dns.resolver.default_resolver.nameservers[0]
            if resolver == address:
                return(True,resolver)
            else:
                return(False,resolver)
        except:
            resolver = None
            print('There was an error setting custom DNS resolver.')
            if debug_flag == True:
                print(traceback.format_exc())
            return(False,resolver)
    else:
        print('Custom DNS server address is invalid or not IPv4 in',config_file,'so the DNS resolver set on the local host will be used by default.')

def check_custom_dns():
    """
    check_custom_dns checks to see if a custom DNS resolver is set in the config.yml file and sets it if it is.
    
    :return: None
    """

    try:
        enabled = config['dns lookup']['server']['enabled']
        address = config['dns lookup']['server']['address']
        if enabled:
            validate,resolver = set_dns_server(address)

            if validate:
                print('DNS resolver set to', resolver)
            else:
                print('There was an error the DNS resolver in',config_file,'so the default DNS resolver for the local host will be used.')

        else:
            print('Custom DNS resolver is disabled in',config_file,'so the default DNS resolver for the local host will be used.')

    except:
        print('The config lines for setting a DNS server is missing or invalid in',config_file,'so the default DNS resolver for the local host will be used.')
        if debug_flag == True:
            print(traceback.format_exc())
    return()

def main():
    """
    main is the main function of the program that calls the other functions to perform the log crunching tasks.
    
    :return: None
    """

    try:
        input = config['input']
        output = config['output']
        dedupe_enabled = config['dedupe']['enabled']
        dedupe_column = config['dedupe']['column']
        dropna_enabled = config['drop']['empty enabled']
        drop_enabled = config['drop']['columns enabled']
        drop = config['drop']['columns']
        ns_enabled = config['dns lookup']['enabled']
        ns_from = config['dns lookup']['column from']
        ns_to = config['dns lookup']['column to']
    except:
        print('Error: Unable to properly parse required values from',config_file)
        if debug_flag == True:
            print(traceback.format_exc())
        exit()

    check_custom_dns()
    log_crunch(input,output,dedupe_enabled,dedupe_column,dropna_enabled,drop_enabled,drop,ns_enabled,ns_from,ns_to)
    print("Program completed successfully, output file written to",output)
    exit()

if __name__=="__main__":
    """
    Use PyYAML to parse the file in the config_file global variable.
    """
    try:
        with open(config_file) as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        print('Error: Unable to find',config_file)
        exit()
    except yaml.scanner.ScannerError:
        print('Error: Unable to parse',config_file)
        exit()
    except:
        print('Error: Unknown problem with',config_file)
        print(traceback.format_exc())
        exit()

    """
    Check the debug_flag global variable to see if the user wants to enable debug mode.
    """
    try:
        debug_flag = config['debug']
    except:
        debug_flag = False
        print('Debug flag is missing in',config_file,'debugging is off by default.')

    main()