#!/usr/bin/env python

import urllib2
import json
import boto.ec2
import optparse

DEFAULT_REGION = 'eu-west-1'

def get_iam_role():
    """Read IAM role from AWS metadata store."""
    return urllib2.urlopen("http://169.254.169.254/latest/meta-data/iam/security-credentials/").read()

def get_credentials():
    """Read IAM credentials from AWS metadata store."""
    url = "http://169.254.169.254/latest/meta-data/iam/security-credentials/%s" % (get_iam_role(), )
    data = json.loads(urllib2.urlopen(url).read())
    return (data['AccessKeyId'], data['SecretAccessKey'], data['Token'])

def create_volume(size, device_name):
    (access_key, secret_key, token) = get_credentials()
    instance_id = urllib2.urlopen("http://169.254.169.254/latest/meta-data/instance-id").read()
    zone = urllib2.urlopen("http://169.254.169.254/latest/meta-data/placement/availability-zone").read()

    conn = boto.ec2.connect_to_region(
        region_name=DEFAULT_REGION,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        security_token=token
    )

    vol = conn.create_volume(size, zone)
    vol.attach(instance_id, device_name)

def main():
    parser = optparse.OptionParser(usage="%prog --size [int] --device [device_path]", version="%prog 1.0")
    parser.add_option("--size",
        metavar="SIZE", dest="size", default=False,
        action="store", help="Size in GB")
    parser.add_option("--device",
        metavar="DEVICE", dest="device", default=False,
        action="store", help="Example: /dev/sdh")
    (options, args) = parser.parse_args()

    if not options.size:
        parser.print_usage()
        return
    elif not options.device:
        parser.print_usage()
        return

    create_volume(options.size, options.device)

if __name__ == '__main__':
    main()
