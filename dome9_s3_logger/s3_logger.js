'use strict';

const AWS = require('aws-sdk');

const SQS = new AWS.SQS({ apiVersion: '2012-11-05' });
const S3 = new AWS.S3({apiVersion: '2006-03-01'});
const Lambda = new AWS.Lambda({ apiVersion: '2015-03-31' });

// Your queue URL stored in the queueUrl environment variable
const QUEUE_URL = process.env.queueUrl; // string: https://queue.amazonaws.com/123456789012/QUEUENAME
const S3_BUCKET_FOR_LOGGING = process.env.s3BucketForLogging; // string: s3BucketNameHere
const LOG_FOLDER = process.env.logFolder; // string: dome9-log/dome9AuditTrail/ (no leading forward slash)
const LOG_FILE_PREFIX = process.env.logFilePrefix; // string: dome9AuditTrail
const PROCESS_MESSAGE = 'process-message';

function invokePoller(functionName, message) {
	const payload = {
	   operation: PROCESS_MESSAGE,
	   message,
	};
	const params = {
	   FunctionName: functionName,
	   InvocationType: 'Event',
	   Payload: new Buffer(JSON.stringify(payload)),
	};
	return new Promise((resolve, reject) => {
	   Lambda.invoke(params, (err) => (err ? reject(err) : resolve()));
	});
}

var generateId = function() {
	var ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
	var ID_LENGTH = 16;
	var rtn = '';
	for (var i = 0; i < ID_LENGTH; i++) {
			rtn += ALPHABET.charAt(Math.floor(Math.random() * ALPHABET.length));
	};
	return rtn;
};

function processMessage(message, callback) {
	console.log(message);

	// process message
	var msgToJson = JSON.parse(message.Body);
	// prune message for logging
	delete msgToJson.Type;
	//delete msgToJson.MessageId;
	delete msgToJson.TopicArn;
	delete msgToJson.SignatureVersion;
	delete msgToJson.Signature;
	delete msgToJson.SigningCertURL;
	delete msgToJson.UnsubscribeURL;
	
	var msgTimestamp = msgToJson.Timestamp; // Timestamp sample: 2018-04-27T15:58:00Z
	if (! msgTimestamp) {
		console.error("Message timestamp not found.");
	};
	
	var tsYear = msgTimestamp.substring(0, 4);
	var tsMonth = msgTimestamp.substring(5, 7);
	var tsDate = msgTimestamp.substring(8, 10);
	var tsHours = msgTimestamp.substring(11, 13);
	var tsMinutes = msgTimestamp.substring(14, 16);
	
	var logFilename = LOG_FILE_PREFIX + tsYear + tsMonth + tsDate + "T" + tsHours + tsMinutes + "Z_" + generateId() + ".json";
	var strMsg = JSON.stringify(msgToJson, null, "\t"); // Indented with tab
	
	var s3Params = {
		Body: strMsg,
		Bucket: S3_BUCKET_FOR_LOGGING,
		Key: LOG_FOLDER + tsYear + "/" + tsMonth + "/" + tsDate + "/" + logFilename, 
		ContentType: "application/json",
		//ContentEncoding: "gzip",
		//ServerSideEncryption: "AES256", 
		Tagging: "source=dome9AuditTrail&timestamp=" + msgToJson.Timestamp
	};
	
	S3.putObject(s3Params, function(err, data) {
		if (err) {
			console.log(err, err.stack); // an error occurred
		}
		else {
			console.log(data);		 // successful response
			console.log("Log file written to s3://" + s3Params.Bucket + "/" + s3Params.Key);

			// delete message
			const sqsParams = {
			   QueueUrl: QUEUE_URL,
			   ReceiptHandle: message.ReceiptHandle,
			};
			SQS.deleteMessage(sqsParams, (err) => callback(err, message));
		}
	});
}

function poll(functionName, callback) {
	
	var msgCount = 0
	var estBatches = 0
	
	const sqsGetQueueAttributesParams = {
	  QueueUrl: QUEUE_URL,
	  AttributeNames: [ "ApproximateNumberOfMessages" ]
	};
	
	const sqsReceiveMessageParams = {
	   QueueUrl: QUEUE_URL,
	   MaxNumberOfMessages: 10,
	   VisibilityTimeout: 15,
	};
	
	SQS.getQueueAttributes(sqsGetQueueAttributesParams, function(err, data) {
		if (err) {
			console.log(err, err.stack); // an error occurred
		}
		else {
			console.log(data);		   // successful response
			var estBatches = Math.ceil( (data.Attributes.ApproximateNumberOfMessages / 5) )
			console.log("Queue Size: " + data.Attributes.ApproximateNumberOfMessages + " Estimated Poll Batches: " + estBatches)
				
			var i = 0;
			while (i < estBatches) {
				// batch request messages 
				console.log("Processing batch #" + (i + 1));
				SQS.receiveMessage(sqsReceiveMessageParams, (err, data) => {
					if (err) {
					  return callback(err);
					}
				   
					// for each message, reinvoke the function
					if (data.Messages) {
						const promises = data.Messages.map((message) => invokePoller(functionName, message));
					   // complete when all invocations have been made
						Promise.all(promises).then(() => {
							const batchResult = `Messages received: ${data.Messages.length}`;
							console.log(batchResult);
							msgCount += data.Messages.length
						});
					}
					else {
						const batchResult = "Woohoo! No messages to process.";
						console.log(batchResult);
						i = estBatches;
					}
				});
				i++;
			}
			const result = "Total Batches: " + estBatches
			callback(null, result);
		}
	});
}

exports.handler = (event, context, callback) => {
	try {
	   if (event.operation === PROCESS_MESSAGE) {
		  // invoked by poller
		  processMessage(event.message, callback);
	   } else {
		  // invoked by schedule
		  poll(context.functionName, callback);
	   }
	} catch (err) {
	   callback(err);
	}
};
