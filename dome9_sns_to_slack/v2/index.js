/*
# *******************************************************************************
# Name: index.js (Dome9 Compliance & Governance findings pushed to Slack)
# Description: AWS Lambda function which consumes Dome9 Compliance findings via 
# SNS, pretty formats, and pushes to the defined slack channel. Filter for 
# severity level is supported.
#
#
# Copywrite 2019, Check Point Software
# www.checkpoint.com
# *******************************************************************************

Variables needed:
hookUrl - slack webhook url
slackChannel - individual channel to post to
severityFilter - CSV of high,medium,low
*/

'use strict';

const AWS = require('aws-sdk');
const url = require('url');
const https = require('https');

// The Slack webhook URL
const hookUrl = process.env.hookUrl;

// The Slack channel to send a message to
const slackChannel = process.env.slackChannel;

// The Severity Filter for Dome9 compliance findings
const severityFilter = process.env.severityFilter;

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
    
    // Prepare message
    var debug = false;
    var message = JSON.parse(event.Records[0].Sns.Message);
    
    // Process severity filters
    if (! severityFilter) {
        severityFilter = "high,medium";
    }
    var sevFilterArray = severityFilter.toLowerCase().split(',');
    if (! sevFilterArray.includes(message.rule.severity.toLowerCase()) ) {
        if (debug) {
            console.log('From SNS:', message);
        }
        var cbMsg = `Finding dropped due to severity filter of ${message.rule.severity}. Severity levels allowed: ${severityFilter}`;
        callback(cbMsg)
    }
    else {
        console.log('From SNS:', message);
    }
    console.log(severityFilter)
    
    // Format message bits
    
    /// Report Time
    var reportTime = new Date(message.reportTime);
    var formatted_reportTime = [
      reportTime.getFullYear(),
      '-',
      reportTime.getMonth() + 1,
      '-',
      reportTime.getDate(),
      ' ',
      reportTime.getHours(),
      ':',
      reportTime.getMinutes(),
      ':',
      reportTime.getSeconds()
    ].join('');
    
    /// Header
    var formatted_header = `*Dome9 Compliance Alert - ${formatted_reportTime} UTC*`;
    
    /// Severity
    var severity_icon = '';
    switch(message.rule.severity.toLowerCase()) {
        case 'high':
            severity_icon = ':octagonal_sign:';
            break;
        case 'medium':
            severity_icon = ':large_orange_diamond:';
            break;
        case 'low':
            severity_icon = ':warning:';
            break;
        default:
            severity_icon = ':warning:';
    }

    var formatted_severity = `${message.rule.severity} ${severity_icon}`;
    
    /// Region 
    var formatted_region = '';
    if (message.region) {
        formatted_region = message.region;
    }
    else {
        formatted_region = "n/a";
    }
        
    /// Rule ID
    var formatted_ruleId = '';
    if (message.rule.ruleId) {
        formatted_ruleId = `<https://gsl.dome9.com/${message.rule.ruleId}.html|${message.rule.ruleId}>`;
    }
    else {
        formatted_ruleId = "n/a";
    }
    
    /// Entity
    var formatted_entityId = '';
    if (message.entity.type == "SecurityGroup") {
        formatted_entityId = `<https://secure.dome9.com/v2/security-group/${message.account.vendor.toLowerCase()}/${message.entity.id}|${message.entity.id}>`;
    }
    else {
        formatted_entityId = `<https://secure.dome9.com/v2/protected-asset/index?query=%7B%22filter%22:%7B%22fields%22:%5B%7B%22name%22:%22organizationalUnitId%22,%22value%22:%2200000000-0000-0000-0000-000000000000%22%7D%5D,%22freeTextPhrase%22:%22${message.entity.id}%22%7D%7D|${message.entity.id}>`;
    }
    
    /// Account
    var formatted_account_id = '';
    if (message.account.vendor.toLowerCase() == "aws") {
        formatted_account_id = `<https://${message.account.id}.signin.aws.amazon.com/console/|${message.account.id}>`;
    }
    else {
        formatted_account_id = message.account.id;
    }
    
    var formatted_accountname = '';
        if (message.account.name) {
        formatted_accountname = message.account.name;
    }
    else {
        formatted_accountname = message.account.id;
    }
    
    var formatted_account = `<https://secure.dome9.com/v2/cloud-account/${message.account.vendor.toLowerCase()}/${message.account.dome9CloudAccountId}|${formatted_accountname}> (${message.account.vendor}: ${formatted_account_id})`;
    
    // Construct final message
    var formatted_message = `${formatted_header} \n${message.rule.name} \n>*Status*: ${message.status} \n>*Severity Level*: ${formatted_severity} \n>*Region*: ${formatted_region} \n>*Rule ID*: ${formatted_ruleId} \n>*Account*: ${formatted_account} \n>*Entity*: ${message.entity.type} (${formatted_entityId})`;

    const slackMessage = {
        channel: slackChannel,
        text: formatted_message
    };

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
