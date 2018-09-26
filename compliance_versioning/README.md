# Compliance Versioning

Auto backup/versioning of Dome9 compliance bundles to GitHub

Currently there isn't bundle versioning within Dome9. This can be a challenge when bundles are frequently updated and there isn't a log of the changes over time. Additionally, just having a backup of all custom bundles can be a helpful tool as well. 

This bash script is meant to be ran on a cron. Once a day should be frequent enough.

## Setup Steps:

### Create a Dome9 API credentials
- Click on your username in the top right hand corner of the Dome9 UI
- Go to 'My Settings'
- In the V2 API section, click 'Create API Key'

### Create a GitHub repo (preferably private) to backup the bundles to

### On the machine that will run the cron:
- Copy backup_bundles.sh and secrets.cfg to where they will run
- Set up the git credentials for this box and clone the backups git repo to /tmp/
```bash 
cd /tmp/ ; git clone git@github.com:Dome9/bundle_backups.git
```

- JQ is required. Make sure it's installed

### Set up secrets.cfg with your Dome9 API key/secret and your github repo name

### Manually run backup_bundles.sh and make sure it's working properly. 

### If it is, set up a cron to run this on an ongoing basis


## How to restore from backup
- Find the bundle you want to restore
- Go through the versions to find the one you wanted
- Copy the text in   "rules": [<GSL>]
- Go into Dome9 Compliance Engine
- Create a new bundle
- Click on 'Edit JSON' 
- Paste and save bundle


## Sample Run
```bash
[AlexAir compliance_versioning]$./backup_bundles.sh 
Pulling latest state from git
Already up-to-date.
Pulling current bundles from the Dome9 API

  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 12.3M  100 12.3M    0     0  1559k      0  0:00:08  0:00:08 --:--:-- 2084k

Saving the custom bundles into their own files

Comparing current bundles to what is currently in git

Checking bundle "Review of Best Practices for AWS"
Checking bundle "Review Dome9 Network Alerts for AWS"
Bundle has been updated since last backup. Copying current version to git directory
[master ad629b5] Updated - "Review Dome9 Network Alerts for AWS"
 1 file changed, 2 insertions(+), 2 deletions(-)

Checking bundle "Review HIPAA Technical Safeguards for AWS"
Checking bundle "CloudSupervisor1"
Pushing updates to Git

Counting objects: 6, done.
Delta compression using up to 8 threads.
Compressing objects: 100% (6/6), done.
Writing objects: 100% (6/6), 785 bytes | 0 bytes/s, done.
Total 6 (delta 4), reused 0 (delta 0)
remote: Resolving deltas: 100% (4/4), completed with 3 local objects.
To github.com:Dome9/bundle_backups.git
   d5e21f4..ad629b5  master -> master

Buncle backup completed 
Fri Mar 23 09:43:58 PDT 2018

[AlexAir]$
```