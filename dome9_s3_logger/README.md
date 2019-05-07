# S3 Logger

This tool write logs to an S3 bucket. It will create an SNS Topic and SQS Queue, poll messages from SQS, and then write the logs elegantly to the S3 every minute. The deployment method leverages CloudFormation and is customizable using the available parameters. It is recommended to deploy two stacks, to segregate Dome9 Audit Trail and Compliance Results into separate folders.

## Getting Started

These instructions will get you a copy of the project up and running in an AWS Account for testing and development.

### Prerequisites

The following cloud assets and conditions are prerequisites to the deployment

* S3 Bucket for Logging before deploying the CloudFormation template.

### Installation

Click the link below to deploy this stack. The AWS region last logged into will be the region of deployment.

The stack has three parameters

**S3BucketForLogging** - this is the S3 bucket

**LogFolder** - path in the S3 bucket for the log files

**LogFilePrefix** - a prefix for the log files, to identify them


[<img src="docs/pictures/cloudformation-launch-stack.png">](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=dome9s3Logger&templateURL=https://s3.amazonaws.com/dome9s3loggercft-us-east-1/s3logger_cftemplate.yaml)

## Post-Install - Configure Dome9 to send events to the new SNS Topic

### Set up a Notification Policy for Continuous Compliance Findings
1. In CloudFormation, find the stack that was designated for Dome9 compliance results and click the **Outputs** tab. 
1. Copy the **InputTopicARN** value.
1. Log into a Dome9 account.
1. Select **Policies** in the  **Compliance and Governance** menu.
1. In the top-right, click  **ADD NOTIFICATION**.
1. Enter a policy **Name**.
1. Click to check **SNS notification for each new finding as soon as it is discovered**.
1. Paste the **InputTopicARN** value into the **SNS Topic ARN** field.
1. Click **SEND TEST MESSAGE**.
1. Click **SAVE**.

### Dome9 Audit Trail Events
1. In CloudFormation, find the stack that was designated for Dome9 audit trail events and select the **Outputs** tab. 
1. Copy the **InputTopicARN** value.
1. Log into a Dome9 account.  
1. Click **Administration** > **Account Settings**. 
1. Click the **SNS Integration** tab.
1. Click **Enable**.
1. In the pop up window, paste the **InputTopicARN** value (step 4).

## Additional Reference: 
[CloudGuard Dome9 SNS Events Integration](https://supportcenter.checkpoint.com/supportcenter/portal?eventSubmit_doGoviewsolutiondetails=&solutionid=sk145195&partition=General&product=CloudGuard)


## Testing
The LogIngestionLambdaFunction is scheduled to run every minute. If you would like to run manual tests configure a test event within the lambda function.

## License

This project is licensed under the MIT License
