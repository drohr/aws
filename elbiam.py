#!/usr/bin/env python
 
import urllib2
import json
import boto.ec2.elb
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
 
def register_instance(load_balancer_name):
    (access_key, secret_key, token) = get_credentials()
    instance_id = urllib2.urlopen("http://169.254.169.254/latest/meta-data/instance-id").read()
 
    elb = boto.ec2.elb.connect_to_region(
        region_name=DEFAULT_REGION,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        security_token=token
    )
 
    lbs = elb.get_all_load_balancers(load_balancer_names=[load_balancer_name])
 
    for lb in lbs:
        lb.register_instances([instance_id])
 
def main():
    parser = optparse.OptionParser(usage="%prog --elb name", version="%prog 1.0")
    parser.add_option("--elb",
        metavar="NAME", dest="lb", default=False,
        action="store", help="load balancer name")
    (options, args) = parser.parse_args()
 
    if not options.lb:
        parser.print_usage()
        return
 
    register_instance(options.lb)
 
if __name__ == '__main__':
    main()
