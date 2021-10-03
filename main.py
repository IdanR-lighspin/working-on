import boto3
from collections import defaultdict
import boto.ec2
import os
import paramiko
import boto
import subprocess
import time

# Before running this:
# need to "aws configure" in terminal and provide data.
ec2 = boto3.client('ec2')

region = "us-east-2"
response = ec2.describe_vpcs()
# vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')  # giving a wrong vpc
"""
#giving the right vpc:
vpc_id = ""
str_i = ""
client = boto3.client('ec2')
Myec2 = client.describe_instances()
for i in Myec2['Reservations']:
    str_i = str(i)
    if "vpc" in str_i:
        str_i = str_i.split("'VpcId': '")
        str_i = str_i[1]
        str_i = str_i.split("', 'Architecture':") # the thing that comes after the VpcId
        vpc_id = str_i[0]
"""

vpc_id = "vpc-5dc26436"

"""
try:
    response = ec2.create_security_group(GroupName='idantest24',
                                         Description='DESCRIPTION',
                                         VpcId=vpc_id)
    security_group_id = response['GroupId']
    print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))

    data = ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {'IpProtocol': 'tcp',
             'FromPort': 22,
             'ToPort': 22,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ])
    print('Ingress Successfully Set %s' % data)
except Exception as e:
    print(e)
"""

key_pair_name = "idan8"

"""
ec2 = boto3.resource('ec2')
# create a file to store the key locally
outfile = open(key_pair_name+'.pem','w')
key_pair = ec2.create_key_pair(KeyName=key_pair_name)

# capture the key and store it in a file
KeyPairOut = str(key_pair.key_material)
outfile.write(KeyPairOut)

# create a new EC2 instance
instances = ec2.create_instances(
     ImageId='ami-00399ec92321828f5',
     MinCount=1,
     MaxCount=1,
     InstanceType='t2.large',
     KeyName=key_pair_name,
     SecurityGroupIds=[
         security_group_id,
     ]
 )
instance_id = str(instances[0])  # output: [ec2.Instance(id='i-0e379dc5b2efc913c')]
instance_id = instance_id.replace("ec2.Instance(id='","")
instance_id = instance_id.replace("')","")
print(instance_id)
"""
instance_id = "i-073ae94f0d3e7b4d3"
temp = boto.ec2.connect_to_region(region)
reservations = temp.get_all_instances()
for r in reservations:
    for i in r.instances:
        if i.state == 'running':
            if i.id == instance_id:
                ec2_global_ip = i.ip_address  #
                vpc_id = i.vpc_id
                print("On: " + ec2_global_ip)

print("--------------------------------")
# IMPORTANT- without chmod 400 (etc) the ssh will not work due to too open access to the key file
sudo_pass = 'Idan2408'  # sudo password of the machine
sudo_password = "echo " + sudo_pass + " | sudo -S "
commands1 = sudo_password + ";" + "sudo chmod 400 /"+key_pair_name+".pem"
output = subprocess.getoutput(commands1)

username = "ubuntu"
ssh = paramiko.SSHClient()
private_key = paramiko.RSAKey.from_private_key_file(key_pair_name + ".pem")
ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
ssh.connect(hostname=ec2_global_ip, port=22, username=username, pkey=private_key)
sftp = ssh.open_sftp()
sftp.put("/home/idan/PycharmProjects/pythonProject/commands.py", "/home/ubuntu/test.py")  # put is writing over
sftp.close()

# running the file:
stdin_, stdout_, stderr_ = ssh.exec_command("python3 test.py", get_pty=True)
time.sleep(5)  # don't know why, but prevents crashing :) (well, apparently just sometimes. need to check more.)
stdout_.channel.recv_exit_status()
lines = stdout_.readlines()
for line in lines:
    print(line)

# this file creates ec2 instance and download to it all the vuls etc.
# todo: need to organize the file. probably this wont be the execution file so wrap it in a class or something.
