# D9SnsToSlack
Lambda function for pushing events from SNS to Slack

Modified from the Cloudwatch to Slack template and adopted for Dome9  1.19.2017

Link to blog: https://blog.checkpoint.com/2017/02/28/dome9-integration-slack/

## Variables needed
- hookUrl - slack webhook url
- slackChannel - individual channel to post to


## SNStoSlack.js
This function is for pulling the events from the Dome9 audit trail and sending them to SNS

## complianceSNStoSlack.js
This function is for pulling the events from continuous compliance and sending them to SNS

Sample Event:  

ReportTime: 2018-06-20T20:37:08.466Z  
AccountId: 936643054293  
New rule violation found: Password policy must prevent reuse of previously used passwords  
ID: 936643054293 | Name: Account Summary  
