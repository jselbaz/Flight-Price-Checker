# Flight Price Checker

## Summary
This script allows you to scrape flight prices using google flights. If the price drops it will email and/or text you an alert so you can rebook at the lower price.

## Installation
Recommend installing uv to manage dependencies
uv pip install -r /path/to/requirements.txt

This requires an App Password if using gmail which can be created [here](https://myaccount.google.com/apppasswords)

## Cell Phone Details to enable text notifications
|Provider|Gateway|
|--------|-------|
|AT&T|@txt.att.net|
|Sprint|@messaging.sprintpcs.com or @pm .sprint.com|
|T-Mobile|@tmomail.net|
|Verizon|@vtext.com|
|Boost Mobile|@myboostmobile.com|
|Cricket|@sms.mycricket.com|
|Metro PCS|@mymetropcs.com|
|Tracfone|@mmst5.tracfone.com|
|U.S. Cellular|@email.uscc.net|
|Virgin Mobile|@vmobl.com|

## Automation
I recommend making a cron job or scheduling a batch file to run this every few hours if using the local version

If using the containerized version you can schedule a lambda to run every few hours

## Container + Lambda + DDB + SSM Set Up
Upload image to ECR

```
docker build -f Dockerfile.dockerfile -t price-checker .

docker tag price-checker:latest AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/price-checker:latest

docker push AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/price-checker:latest
```

Create a new Lambda from the container image in this repo

Architecture: x86_64

Make sure to update the Lambda role so it has IAM permissions to read/write to DDB and read from SSM

Create a dynamoDB table to track price changes. Table's primary key should be an integer field called flight. Add an integer attribute field called price to the table as well.

Add RecipientCell, RecipientEmail, SenderEmail, and SenderEmailAppPassword as parameters in SSM.

Note that all shell scripts may need to be changed from CRLF to LF as Github changes them.

## Credit
Special thanks to [wbyte-selenium-lambda](https://github.com/wbytedev/wbyte-selenium-lambda/blob/main/src/chrome-installer.sh) for their script to download the latest stable version of chrome and drivers to ensure compatibility with selenium.
