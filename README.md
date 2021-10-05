# working-on
running the main now:
- create new ec2.
- install all the things there.
- the creator class attaches the wanted volume to the ec2 we created. then mount it to local folder from the command script.
- running all of the checks and save them as jsons on the created ec2.

bugs:
- can't access any tool after chroot.
- vuls output doesnt contain cves. faced this issue before, probably config error. need to run vuls after chroot to the new volume, which isnt working.
