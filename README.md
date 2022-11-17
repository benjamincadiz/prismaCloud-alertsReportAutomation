# Create a CSV report about security alerts in Prisma Cloud and send to the stakeholders by email

Script created to automate the proccess of reporting to the Infrastructure team about their security alerts  through Prisma Cloud in CSV format. 

Currently Prisma Cloud allow you to create a report in PDF format with not enough details about the alerts. For that reason I created an automation in CSV format where you can get much more details about each alerts found with Prisma Cloud. 

## Flow of the script

Prisma Cloud has a ton of alerts of our infrastructure associated with an Account Group. This account group usually is associated with an team/org inside the company whom has an email either of the responsible or team.

We're going to create a resource list in Prisma cloud to dynamically send the report as many team/org we want without change our code. In that resource list, which is a Key-Value list we're going to specify the name of the Account Group and the value the email where we're going to send it 

## Params which you'd need

base_url = "" -> base url of your Prisma cloud instance.

"password": "", -> password Prisma cloud
"username": "" -> username Prisma Cloud

payload -> You can customize the payload to achieve whatever the report you want it. 

msg['From'] = "" -> from details to send email
msg['Subject'] = "" -> Subject details to send email

<IdResourceList> -> ID resouce List in Prisma Cloud where the script will take the account group and email of the team
