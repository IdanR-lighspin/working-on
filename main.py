import boto3
from collections import defaultdict
import boto.ec2
import os
import paramiko
import boto
import subprocess
import time
from creator import Creator
import time

start_time = time.time()
# Before running this:
# need to "aws configure" in terminal and provide data.


ec2 = boto3.client('ec2')

region = "us-east-2"
response = ec2.describe_vpcs()


def get_vpc():
    # vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')  # giving a wrong vpc
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
    return vpc_id


def security_group_settings(vpc_id_):
    try:
        response = ec2.create_security_group(GroupName='idantest30', #change bedore run again
                                             Description='DESCRIPTION',
                                             VpcId=vpc_id_)
        security_group_id = response['GroupId']
        print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id_))

        data = ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                # add here kibana ports later.
                {'IpProtocol': 'tcp',
                 'FromPort': 22,
                 'ToPort': 22,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
            ])
        print('Ingress Successfully Set %s' % data)
        return security_group_id
    except Exception as e:
        print(e)


def create_ec2(security_group_id, key_pair_name):
    # maybe get ImageId too.

    ec2 = boto3.resource('ec2')
    # create a file to store the key locally
    outfile = open(key_pair_name+'.pem', 'w')
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
    instance_id_ = str(instances[0])  # output: [ec2.Instance(id='i-0e379dc5b2efc913c')]
    instance_id_ = instance_id_.replace("ec2.Instance(id='", "")
    instance_id_ = instance_id_.replace("')", "")
    print(instance_id_)
    return instance_id_


def instance_id_ip(instance_id):
    ec2_global_ip = ""
    # instance_id = "i-073ae94f0d3e7b4d3"
    temp = boto.ec2.connect_to_region(region)
    reservations = temp.get_all_instances()
    for r in reservations:
        for i in r.instances:
            if i.state == 'running':
                if i.id == instance_id:
                    ec2_global_ip = i.ip_address
                    vpc_id = i.vpc_id
                    #print("On: " + ec2_global_ip)
    return ec2_global_ip


def ssh_operations(ec2_global_ip, key_pair_name, sudo_pass, file_path_to_pass, destination_file_path):
    """
    transferring and running a python file in the new ec2 machine (or another machine if wanted..)
    :param ec2_global_ip:
    :param key_pair_name:
    :param sudo_pass:
    :return:
    """
    # IMPORTANT- without chmod 400 (etc) the ssh will not work due to too open access to the key file.
    sudo_password = "echo " + sudo_pass + " | sudo -S "
    commands1 = sudo_password + "sudo chmod 400 " + "/home/idan/PycharmProjects/pythonProject/" + key_pair_name + ".pem"
    # commands1 = sudo_password + "sudo chmod 400 " + key_pair_name + ".pem"
    output = subprocess.getoutput(commands1)  # ill change the path later

    username = "ubuntu"  # may get this as parameter later on
    ssh = paramiko.SSHClient()
    private_key = paramiko.RSAKey.from_private_key_file(key_pair_name + ".pem")
    ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(hostname=ec2_global_ip, port=22, username=username, pkey=private_key)
    sftp = ssh.open_sftp()
    sftp.put(file_path_to_pass, destination_file_path)  # put is writing over
    sftp.close()

    # running the file:
    stdin_, stdout_, stderr_ = ssh.exec_command("python3 " + destination_file_path, get_pty=True) # probably add sudo here
    time.sleep(5)  # don't know why, but prevents crashing :) (well, apparently just sometimes. need to check more.)
    stdout_.channel.recv_exit_status()
    lines = stdout_.readlines()
    for line in lines:
        print(line)


def main():
    key_pair_name = "idan14"  # without .pem
    sudo_password = "Idan2408"

    vpc_id = get_vpc()
    print(vpc_id)

    #security_group_id = security_group_settings(vpc_id)
    #print(security_group_id)

    #instance_id = create_ec2(security_group_id, key_pair_name)
    #print("instance id: ", instance_id)
    instance_id = "i-0e08f61499fd5b91e"

    global_ip = instance_id_ip(instance_id)

    a = Creator("us-east-2", instance_id,  "i-0e379dc5b2efc913c")  # (region, ec2 just created, ec2 to snap from)
    a.create_and_attach_volume_from_snapshot()
    ssh_operations(global_ip, key_pair_name, sudo_password, "/home/idan/PycharmProjects/pythonProject/commands.py", "/home/ubuntu/test.py")
    ssh_operations(global_ip, key_pair_name, sudo_password, "/home/idan/PycharmProjects/pythonProject/main_elk.py", "/home/ubuntu/test1.py")

    print("main file took to execute: ", time.time()-start_time, " S")  # about 10 minutes +-


if __name__ == "__main__":
    main()


# todo: vuls isn't outputting correctly. need to look on the config file probably.
# todo: run vuls on the new root.-> ssh to it etc.
# todo: the kibana code is commented for now- need to check on "remote" kibana server.
# lynis is now go over the new volume. the comparison between the jsons is in my email.
# (one is on the new volume and one is on all of the ec2 machine.

