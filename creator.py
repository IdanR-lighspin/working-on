import boto3
import time


class Creator:
    def __init__(self, r, instance_attach, snap_from_id):
        # need to provide: region, ec2 just created, ec2 to snap from
        self.region = r
        self.instance_id_to_attach = instance_attach
        self.instance_id_to_snap_from = snap_from_id
        self.client = boto3.client('ec2', region_name=self.region)
        self.ec2 = boto3.resource('ec2', region_name=self.region)
        self.volume_id_ = ""
        self.snapshot_id_ = ""

    @staticmethod
    def get_volume_id(doc, name):
        for item in doc['BlockDeviceMappings']:
            if item["DeviceName"] == name:
                return item['Ebs']['VolumeId']

    def get_volume_id_of_instance(self):
        # instance_id = "i-0e379dc5b2efc913c"  # for example, will change it later
        response = self.client.describe_instances(InstanceIds=[self.instance_id_to_snap_from])
        instance_doc = response["Reservations"][0]["Instances"][0]
        volume_id = self.get_volume_id(doc=instance_doc, name=instance_doc["RootDeviceName"])
        self.volume_id_ = volume_id
        print("Got volume: ", self.volume_id_)

    def create_snapshot(self):
        self.get_volume_id_of_instance()
        response = self.ec2.create_snapshot(
            VolumeId=self.volume_id_
        )
        # taking snapshot:
        response = str(response)
        response = response.replace("ec2.Snapshot(id='", "")  # ec2.Snapshot(id='snap-0bfb40a0d37dfaf7e')
        snapshot_id = response.replace("')", "")  # = snap-0f7ed1ffa06c93a97
        self.snapshot_id_ = snapshot_id
        print("Created snapshot: ", self.snapshot_id_)
        # need to wait for the snapshot to end the pending time:
        time.sleep(60)  # sometimes need 3 seconds, sometimes need over 100 seconds.

    def create_and_attach_volume_from_snapshot(self):
        self.create_snapshot()

        # create:

        new_volume = self.ec2.create_volume(
            AvailabilityZone='us-east-2b',
            SnapshotId=self.snapshot_id_,
            VolumeType='gp2',
            TagSpecifications=[
                {
                    'ResourceType': 'volume',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'test'
                        }
                    ]
                }
            ]
        )

        print(f'Created volume {new_volume.id} from Snapshot {self.snapshot_id_}')
        time.sleep(20)

        # attach:

        volume_id = new_volume.id
        # volume_id = new_volume.id
        volume = self.ec2.Volume(volume_id)
        volume.attach_to_instance(
            Device='/dev/xvdw',
            InstanceId=self.instance_id_to_attach
        )
        print(f'Volume {volume.id} attached to -> {self.instance_id_to_attach}')


a = Creator("us-east-2", 'i-073ae94f0d3e7b4d3',  "i-0e379dc5b2efc913c")  # (region, ec2 just created, ec2 to snap from)
# need to run just this function:
a.create_and_attach_volume_from_snapshot()

"""
ask michael later:
as far as i saw, the new "disk" name will be the device name we gave above +1.
for example : Device='/dev/xvdw'
will need to mount xvdw1
"""
# todo: use it from the test.py. run the thing on new machine and try to get output.
# todo: need to see how to use elasticsearch on the the machine. probably open new port beforehand for kibana or
# todo: connect to elasticsearch server. test connection from any machine ?
# todo: need to see how to use the new volume in the ec2.
