#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import sys
import requests
import json


class Output:
    """Class to define Confirmed & logged interpreted/translated messages
    by Synology
    """
    SUCCESS = "good"  # [succesfully registered]
    NO_CHANGES = "nochg"  # [no changes in ddns record]
    HOSTNAME_DOES_NOT_EXIST = "nohost"
    # [The hostname specified does not exist. Check if you created
    # the hostname on the website of your DNS provider]
    AUTHENTICATION_FAILED = "badauth"  # [Authentication failed]
    DDNS_PROVIDER_DOWN = "911"  # [Server is broken]


def parse_args():
    """Parsing cli arguments
    """
    parser = argparse.ArgumentParser(sys.argv[0])

    parser.add_argument("cf_zone", type=str, help="Cloudflare Zone ID")
    parser.add_argument("cf_token", type=str, help="Cloudflare API token")
    parser.add_argument("domain", type=str, help="DDNS domain")
    parser.add_argument("ip", type=str, help="DDNS ip")

    return parser.parse_args()


# Function to update DNS records
def update_dns_record(cf_endpoint, headers, data, item_id):
    """Updates DNS record.
    https://developers.cloudflare.com/api/operations/dns-records-for-a-zone-patch-dns-record

    Args:
        cf_endpoint (str): Cloudflare API endpoint including ZoneID
        headers (dict): Dictrionary of headers to include in PATCH request
        data (dict): Dictionary of data to send in PATCH request body.
        item_id (str): DNS record ID you want to update.

    Returns:
        dict: Dictionary of request object response
    """
    response = requests.patch(
        f"{cf_endpoint}/{item_id}", headers=headers, data=json.dumps(data)
    )
    if response.ok:
        print(Output.SUCCESS)
    return response.json()


# Function to update DNS records
def create_dns_record(cf_endpoint, headers, data):
    """Create DNS record.
    https://developers.cloudflare.com/api/operations/dns-records-for-a-zone-create-dns-record

    Args:
        cf_endpoint (str): Cloudflare API endpoint including ZoneID
        headers (dict): Dictrionary of headers to include in POST request
        data (dict): Dictionary of data to send in POST request body.

    Returns:
        dict: Dictionary of request object response
    """
    response = requests.post(
        cf_endpoint, headers=headers, data=json.dumps(data)
    )
    if response.ok:
        print(Output.SUCCESS)
    return response.json()


# Function to get all DNS records
def get_dns_records(cf_endpoint, headers, data=None):
    """Get DNS record(s).
    https://developers.cloudflare.com/api/operations/dns-records-for-a-zone-list-dns-records

    Args:
        cf_endpoint (str): Cloudflare API endpoint including ZoneID
        headers (dict): Dictrionary of headers to include in GET request
        data (dict, optional): Dictionary of data to send in
            GET request params. Defaults to None.

    Returns:
        dict: Dictionary of DNS record objects.
        dict: Dictionary of ERROR object.
    """
    response = requests.get(cf_endpoint, headers=headers, params=data)
    if response.ok:
        return response.json()["result"]
    return response.json()


if __name__ == "__main__":
    """Main function that runs logic around whether to create or update
    DNS record.
    """
    # Check if all required arguments are provided
    args = parse_args()

    cf_zone = args.cf_zone
    cf_token = args.cf_token
    domain = args.domain
    ip = args.ip

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {cf_token}",
    }

    data = {
        "type": "A",
        "name": domain,
        "content": ip,
        "ttl": 1,
        "proxied": True,
        "comment": "Updated by Synology",
    }

    cf_endpoint = (
        f"https://api.cloudflare.com/client/v4/zones/{cf_zone}/dns_records"
    )

    missing = True

    dns_records = get_dns_records(cf_endpoint, headers)

    for record in dns_records:
        if record["type"] == "A" and record["name"] == domain:
            missing = False
            response = get_dns_records(cf_endpoint, headers, data)
            if len(response) == 0:
                response = update_dns_record(
                    cf_endpoint, headers, data, record["id"]
                )
            else:
                print(Output.NO_CHANGES)

    if missing:
        print(Output.HOSTNAME_DOES_NOT_EXIST)
        response = create_dns_record(cf_endpoint, headers, data)
        print(Output.SUCCESS)
