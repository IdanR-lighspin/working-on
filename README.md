# working-on
running the main now:
- create new ec2.
- install all the things there.
- the creator class attaches the wanted volume to the ec2 we created. then mount it to local folder from the command script.
- running all of the checks and save them as jsons on the created ec2.
- (now the lynis is being installed to the ec2 regularly and to the new volume. didnt test it yet. ill fix it after a bit of testing.

todo:
- vuls output doesnt contain cves. faced this issue before, probably config error. need to run vuls after chroot to the new volume, which isnt working (due to the same error as above)+ add ssh thing etc.

before running:
-  /newvolumes has different numbers throughout the code.
-  change "idan8" key name. 
-  import boto3 (eventually the code will do it with a subprocess)
-  change device name in class
