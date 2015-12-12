# Dome9 reporter and locker for AWS Security Groups

## What is it?
- A little python script that provides multiple operations on AWS security groups managed by Dome9 Security:
- Ability to **report (CSV/ JSON format)** all security groups in multi AWS accounts, multi regions / multi VPCs setups.
- Ability to batch **'lock'** SGs - Move multiple security groups to *'Dome9 Full Protection'* given criteria such VPC, SG names,SG ids region etc...
- Ability to batch **'unlock'** SGs - Move to *'Read-Only'* mode.
- This is very useful for highly secured environments that do not permit changes outside of a clearly defined update window.

## Installation instructions
- Make sure you have python version 2.5 and up.
- Git clone this repo or download the repository zip file.
- Set execute permissions for the script file:

```bash
cd sg_locker
chmod +x d9_sg_locker.py
```

- (Optional) For ease of use, set your Dome9 user(email) / api key (found in your Dome9 console-> Setting page) in environment variables : 

```
export d9_user=my@email.com
export d9_api_sec=XXXXXXXXXXX
```

## Usage

```
./d9_sg_locker.py --help
```

usage: d9_sg_locker.py [-h] [--sgname SGNAME [SGNAME ...]]
                       [--sgid SGID [SGID ...]] [--vpc VPC [VPC ...]]
                       [--accid ACCID [ACCID ...]]
                       [--region REGION [REGION ...]] [-v] -a ACTION [-u USER]
                       [-p APISECRET] [--ack]

Query for security groups given some filter criteria

optional arguments:

  -h, --help            show this help message and exit
  
  --sgname SGNAME [SGNAME ...]
                        Filter given list of security groups names (space
                        delimited)
						
  --sgid SGID [SGID ...]
                        Filter given list of security groups (aws) ids (space
                        delimited)
						
  --vpc VPC [VPC ...]   Filter given list of VPC ids. Will match all security
                        groups in these VPCs
						
  --accid ACCID [ACCID ...]
                        Filter given list of AWS account ids. Will match all
                        security groups in these accounts
						
  --region REGION [REGION ...]
                        Filter given list of regions. Will match all security
                        groups in these regions
						
  -v, --verbose         Prints additional statistics
  
  -a ACTION, --action ACTION
                        [report|report_json|lock|unlock]
						
  -u USER, --user USER  Dome9 user name (your email)
  
  -p APISECRET, --apisecret APISECRET
                        Your Dome9 api key. Found under settings.
						
  --ack                 Supress acknowledgement message before perfroming
                        changes (recommended only for automated use-cases)

					
## Examples
* Generate CSV report for all security groups in either of these 2 regions (could be in multiple AWS accounts)

```
./d9_sg_locker.py -u my@email.com -p XXX --region us_west_2 us_east_1 -a report
```

* Generate JSON report with complex filter. SGs need to satisfy both region and name contraints

```
./d9_sg_locker.py -u my@email.com -p XXX --region us_east_1 --sgname=default app1 app2  -a report_json
```

* Lock (move to Dome9 Full Protection) all security groups in the VPC. User will need to acknowledge action before update occurs

```
./d9_sg_locker.py -u my@email.com -p XXX --vpc vpc-12345 -a lock
```

* Unlock (move to Dome9 Read-Only mode) all security groups in the VPC. User will *not* need to acknowledge action as --ack was provided. This is important for automated deployment.

```
./d9_sg_locker.py -u my@email.com -p XXX --vpc vpc-12345 -a unlock --ack
```