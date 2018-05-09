# S3 Logger

This tool will create an SNS Topic and SQS Queue, poll messages from SQS, and then write the logs elegantly to S3 every minute. The deployment method leverages CloudFormation and customizable using the available parameters. It is recommended to deploy two stacks to segregate Dome9 Audit Trail and Compliance Results into separate folders.

## Getting Started

These instructions will get you a copy of the project up and running in an AWS Account for testing and development.

### Prerequisites

Cloud assets needed to install the stack

* S3 Bucket for Logging before deploying the CloudFormation template.

### Installing

To install the stack in your environment simply deploy the CloudFormation template from this project.

CFT File:

```
s3logger_cftemplate.yaml
```

## Post-Install - Configure Dome9 to send events to the new SNS Topic

**Option 1 - Dome9 Audit Trail Events**
1. In CloudFormation, find the stack that was designated for Dome9 audit trail events and click the **Outputs** tab. 
2. Copy the **InputTopicARN** value
2. Log into a Dome9 account.  
3. In the top-right, click your *username* and then click the **Account Settings** tab.
4. Click the **SNS Integration** tab.
5. Click **Enable**.
6. Jump to step 4 and Paste the **InputTopicARN** value

**Option 2 - Dome9 Continuous Compliance Results**
1. In CloudFormation, find the stack that was designated for Dome9 compliance results and click the **Outputs** tab. 
2. Copy the **InputTopicARN** value
3. Log into a Dome9 account.
4. Click the **Compliance and Governance** tab and then click **Continuous Compliance**.
5. In the top-right, click the **Manage Notifications** button.
6. Click **Add new policy**.
7. Enter a policy **Name**.
8. Click to check **SNS notification for each changed test**
9. Paste the **InputTopicARN** value into the **SNS Topic ARN** field.
10. Click **SEND TEST MESSAGE**.
11. Click **Create**.

Additional Reference: 
https://dome9-security.atlassian.net/wiki/spaces/DG/pages/30179352/Dome9+SNS+Events+Integration+-+How+to

## Testing
The LogIngestionLambdaFunction is scheduled to run every minute. If you would like to run manual tests configure a test event within the lambda function.

## License

This project is licensed under the MIT License
