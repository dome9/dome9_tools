/*
Lambda function for pushing events from SNS to Slack
Modified from the Cloudwatch to Slack template and adopted for Dome9  1.19.2017
Variables needed:
hookUrl - slack webhook url
slackChannel - individual channel to post to
Optional variable:
messageTypeBlacklist - pipe delimited list of message types to NOT post to slack. This is to help reduce noise
The top 3 most common events you might want to filter are:
InstanceStateChanged
InstanceCreatedEvent
InstanceTagsChangeDetectedEvent
*/

'use strict';

const AWS = require('aws-sdk');
const url = require('url');
const https = require('https');

// The Slack webhook URL
const hookUrl = process.env.hookUrl;

// The Slack channel to send a message to
const slackChannel = process.env.slackChannel;

// The event types we DON'T want to print (split by pipe)
const messageTypeBlacklist = process.env.messageTypeBlacklist ? process.env.messageTypeBlacklist.split("|"): [];

function postMessage(message, callback) {
    const body = JSON.stringify(message);
    const options = url.parse(hookUrl);
    options.method = 'POST';
    options.headers = {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
    };

    const postReq = https.request(options, (res) => {
        const chunks = [];
        res.setEncoding('utf8');
        res.on('data', (chunk) => chunks.push(chunk));
        res.on('end', () => {
            if (callback) {
                callback({
                    body: chunks.join(''),
                    statusCode: res.statusCode,
                    statusMessage: res.statusMessage,
                });
            }
        });
        return res;
    });

    postReq.write(body);
    postReq.end();
}

function processEvent(event, callback) {
    var message = event.Records[0].Sns.Message;
    message = message.split(",").join("\n"); // you can comment out this line to send the message as a blob
    console.log('From SNS:', message);

    const slackMessage = {
        channel: slackChannel,
        text: message
    };

    if ((messageTypeBlacklist.filter((n) => message.indexOf(n) >= 0)).length > 0) {
        return; // if the message matches our blacklist - no need to do anything
    }

    postMessage(slackMessage, (response) => {
        if (response.statusCode < 400) {
            console.info('Message posted successfully');
            callback(null);
        } else if (response.statusCode < 500) {
            console.error(`Error posting message to Slack API: ${response.statusCode} - ${response.statusMessage}`);
            callback(null);  // Don't retry because the error is due to a problem with the request
        } else {
            // Let Lambda retry
            callback(`Server error when processing message: ${response.statusCode} - ${response.statusMessage}`);
        }
    });
}

exports.handler = (event, context, callback) => {
    processEvent(event, callback);
};