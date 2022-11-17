#!/usr/bin/python3

from concurrent.futures import process
import requests
import multiprocessing
import json
import os
from time import time, sleep
import smtplib
from email.message import EmailMessage

base_url = ""

def getJWT():
    url = base_url+"login"

    payload = {
        "password": "",
        "username": ""
    }
    headers = {"content-type": "application/json; charset=UTF-8"}

    response = requests.request("POST", url, json=payload, headers=headers)
    resp = json.loads(response.text)
    return resp['token']

def getStatusJob(idJob, token):
    url = base_url+"alert/csv/%s/status"%idJob
    headers = {"x-redlock-auth": "%s"%token}

    response = requests.request("GET", url, headers=headers)
    resp = json.loads(response.text)
    return resp['status']

def generationJob(token, account):

    url = base_url+"alert/csv"

    querystring = {"detailed":"true"}

    payload = {
        "detailed": True,
        "filters": [
            {
                "name": "timeRange.Type",
                "operator": "=",
                "value": "ALERT_OPENED"
            },
            {
                "name": "alert.status",
                "operator": "=",
                "value": "open"
            },
            {
                "name": "account.group",
                "operator": "=",
                "value": "%s"%account
            },
            {
                "name": "policy.severity",
                "operator": "=",
                "value": "high"
            }
        ],
        "timeRange": {
            "type": "to_now",
            "value": "epoch"
            
        }
    }

    headers = {
        "content-type": "application/json; charset=UTF-8",
        "x-redlock-auth": "%s"%token
    }
    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)

    resp = json.loads(response.text)
    return resp['id']


def sendEmail(email_account, account):
    #Data from COMPANY email server
    port = 25
    smtp_server = ""
    # Email details
    msg = EmailMessage()
    msg['To'] = email_account
    msg['From'] = ""
    msg['Subject'] = ""
    with open(filename, 'rb') as content_file:
        content = content_file.read()
        msg.add_attachment(content, maintype='application', subtype='csv', filename=filename)
    msg.set_content("Hi  team, \n \n I'm sending you a report about the alerts which Prisma Cloud found in your infrastructure. Please take a look into the file attached and let us know if you have any question. \n \n Thanks so much. ")

    with smtplib.SMTP(smtp_server,port) as server:
        server.send_message(msg)

def getCSV(idJob, token, account):

    url = base_url+"alert/csv/%s/download"%idJob

    headers = {"x-redlock-auth": "%s"%token}

    response = requests.request("GET", url, headers=headers)

    csv_file = open('%s_alertsReport.csv'%account, 'w')
    csv_file.write(response.text)
    csv_file.close()

def getResourceList(token):
    url = base_url+'v1/resource_list/<IdResourceList>'
    headers = {"x-redlock-auth": "%s"%token}
    response = requests.request("GET", url, headers=headers)
    resp = json.loads(response.text)
    accounts_group=[]
    emails_account=[]
    for item in resp['members']:
        for key in item.keys(): accounts_group.append(key)
        for value in item.values(): emails_account.append(value)
    return accounts_group, emails_account


def logicalPart(account, token, email_account):
    # 1. generate job job 
    print('Starting to work')
    idJob = generationJob(token, account)
    statusResponse = ''
    # 2. wait for finish 
    while not statusResponse == 'READY_TO_DOWNLOAD':
        statusResponse = getStatusJob(idJob, token)
        print(statusResponse)
        sleep(60 - time() % 60)
    # 3.save file
    getCSV(idJob, token, account)
    print('Done work')

def main():
    print(os.environ.get('test'))
    # 1. get token 
    tokenResponse = getJWT()

    # 2. get details of accounts group with the resourceList on Prisma
    accounts_group, emails_account = getResourceList(tokenResponse)

    # 3. Spin up a proccess per account and run it
    process_list = []
    for i in range(len(accounts_group)):
        p = multiprocessing.Process(target=logicalPart, args=[accounts_group[i], tokenResponse, emails_account[i]])
        p.start()
        process_list.append(p)

    for process in process_list:
        process.join()
    
    # Send email per account
    for i in range(len(accounts_group)):
        sendEmail(emails_account[i], accounts_group[i])

    
if __name__ == "__main__":
    main()

