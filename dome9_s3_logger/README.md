# S3 Logger

This tool will poll messages from SQS on a schedule user-defined and write the logs elegantly to S3.

## Getting Started

These instructions will get you a copy of the project up and running in an AWS Account for testing and development.

### Prerequisites

What things you need to install the software and how to install them

```
* 1 SNS Topic - https://dome9-security.atlassian.net/wiki/spaces/DG/pages/30179352/Dome9+SNS+Events+Integration+-+How+to
* 1 SQS Queue
* 1 Lambda Function and IAM Role
* S3 Bucket for Logging
```

### Installing

A step by step series of examples that tell you have to get a development env running

Say what the step will be

```
Lambda Environment Variables
queueUrl : string: https://queue.amazonaws.com/123456789012/QueueNameHere
s3BucketForLogging : string : s3BucketNameHere
logFilePrefix : string : dome9AuditTrail
logFolder : string : dome9-log/dome9AuditTrail/
maxBatches : number : 1000
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

In Lambda you will need to configure a new test event. 
1. Open the lambda function and find the dropdown to the left of the Test button. 
2. Click "Configure Test events"
3. From the Event template drop-down menu, select "Scheduled Event"
4. Do not modify the JSON in the event as it is irrelevant.
5. Click the Create button
6. Click the Test button using the new test event.

## Deployment

Add additional notes about how to deploy this on a live system

## License

This project is licensed under the MIT License
