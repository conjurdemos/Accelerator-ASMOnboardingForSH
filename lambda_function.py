"""Module to retrieve metadata from a secret in AWS Secrets Manager
and use them to onboard the secret to CyberArk Privilege Cloud"""
import json
import os
import urllib.parse
import requests
import boto3
from botocore.exceptions import ClientError

def urlify(s):
    """URL encodes a given string"""
    return urllib.parse.quote(s)


def lambda_handler(event, context):
    """Lambda function handler"""
    # Print the event to see its structure (useful for debugging)
    #print("Received event: " + json.dumps(event, indent=2))

    # Print the context to see its structure (useful for debugging)
    print("Lambda function ARN: " + context.invoked_function_arn)
    print("CloudWatch log stream name: " + context.log_stream_name)
    print("CloudWatch log group name: " +  context.log_group_name)
    print("Lambda Request ID: " + context.aws_request_id)
    print("Lambda function memory limits in MB: " + context.memory_limit_in_mb)

    try:
        # Extract the secret ID from the CloudWatch Event
        secret_id = event['detail']['requestParameters']['name']

        # Initialize a client for AWS Secrets Manager
        secrets_manager_client = boto3.client('secretsmanager')

        # Retrieve the tags of the secret
        response = secrets_manager_client.describe_secret(SecretId=secret_id)
        tags = response.get('Tags', [])
        tags_dict = {tag['Key']: tag['Value'] for tag in tags}

        # Check for Sourced by CyberArk tag
        if 'Sourced by CyberArk' not in tags_dict:
            return {
                'statusCode': 200,
                'body': json.dumps(f"Secret {secret_id} not sourced by CyberArk")
            }

        # Retrieve the secret value of PrivilegeCloudSecret
        pcloud_secret_id = os.environ.get("PrivilegeCloudSecret")
        try:
            pcloud_response = secrets_manager_client.get_secret_value(SecretId=pcloud_secret_id)
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print("The requested secret " + pcloud_secret_id + " was not found")
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                print("The request was invalid due to:", e)
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                print("The request had invalid params:", e)
            elif e.response['Error']['Code'] == 'DecryptionFailure':
                print("The requested secret can't be decrypted using the provided KMS key:", e)
            elif e.response['Error']['Code'] == 'InternalServiceError':
                print("An error occurred on service side:", e)
        else:
            pcloud_secret_value = pcloud_response.get('SecretString', None)
            pcloud_secret_dict = json.loads(pcloud_secret_value)

        # Retrieve the secret value of the secret
        try:
            response = secrets_manager_client.get_secret_value(SecretId=secret_id)
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print("The requested secret " + secret_name + " was not found")
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                print("The request was invalid due to:", e)
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                print("The request had invalid params:", e)
            elif e.response['Error']['Code'] == 'DecryptionFailure':
                print("The requested secret can't be decrypted using the provided KMS key:", e)
            elif e.response['Error']['Code'] == 'InternalServiceError':
                print("An error occurred on service side:", e)
        else:
            secret_value = response.get('SecretString', None)
            secret_dict = json.loads(secret_value)

        # Create dict of CyberArk metadata
        cyberark_dict = {
            "subdomain":    pcloud_secret_dict.get('subdomain', None),
            "svc_username": pcloud_secret_dict.get('username', None),
            "svc_password": pcloud_secret_dict.get('password', None),
            "safe":         tags_dict.get('CyberArk Safe', None),
            "account":      tags_dict.get('CyberArk Account', None),
            "address":      secret_dict.get('address', None),
            "username":     secret_dict.get('username', None),
            "password":     secret_dict.get('password', None),
            "platformId":   secret_dict.get('platformId', None)
        }

        # If no address, check if RDS Secret containing host
        if cyberark_dict['address'] is None:
            cyberark_dict['address'] = secret_dict.get('host', None)
        
        # If no platformId, check if RDS Secret contains as tag
        if cyberark_dict['platformId'] is None:
            cyberark_dict['platformId'] = tags_dict.get('CyberArk Platform', None)

        print(f"CyberArk Metadata: {cyberark_dict}")

        # Check for None as the value for any dict keys
        none_keys = [key for key, value in cyberark_dict.items() if value is None]

        if none_keys:
            return {
                'statusCode': 404,
                'body': json.dumps(f"Required key value(s) not found: {none_keys}")
            }
            print(f'HTTP 404: Required key value(s) not found: {none_keys}')

        # Authenticate to CyberArk Identity
        url = f"https://{cyberark_dict['subdomain']}.cyberark.cloud/api/idadmin/oauth2/platformtoken"
        payload = f"grant_type=client_credentials&client_id={urlify(cyberark_dict['svc_username'])}&client_secret={cyberark_dict['svc_password']}"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.request("POST", url, headers=headers, data=payload, timeout=30)
        if response.status_code == 200:
            # Parse the JSON response into a dictionary
            data = response.json()

            # Access the session token from the dictionary
            session_token = data.get('access_token', None)
            if session_token is None:
                return {
                    'statusCode': 401,
                    'body': json.dumps(f"There was a problem authenticating to: {cyberark_dict['subdomain']}.privilegecloud.cyberark.cloud")
                }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps(f"There was a problem authenticating to: {cyberark_dict['subdomain']}.privilegecloud.cyberark.cloud")
            }
        
        # Create safe
        url = f"https://{cyberark_dict['subdomain']}.privilegecloud.cyberark.cloud/passwordvault/api/safes"
        payload = json.dumps({
            "safeName": cyberark_dict['safe'],
            "description": "Created by AWS Secrets Manager",
            "olacEnabled": False,
            "managingCPM": "PasswordManager",
            "numberOfDaysRetention": 0
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {session_token}'
        }
        response = requests.request("POST", url, headers=headers, data=payload, timeout=30)
        print(f"Safe Response Message: {response.text}")
        if response.status_code == 201:
            print(f"Safe {cyberark_dict['safe']} created successfully")
        elif response.status_code == 409:
            print(f"Safe {cyberark_dict['safe']} already exists")
        else:
            return {
                'statusCode': 500,
                'body': json.dumps(f"There was a problem creating safe {cyberark_dict['safe']}")
            }

        # Onboard account into safe
        url = f"https://{cyberark_dict['subdomain']}.privilegecloud.cyberark.cloud/passwordvault/api/accounts"
        payload = json.dumps({
            "safeName": cyberark_dict['safe'],
            "platformID": cyberark_dict['platformId'],
            "name": cyberark_dict['account'],
            "address": cyberark_dict['address'],
            "userName": cyberark_dict['username'],
            "secretType": "password",
            "secret": cyberark_dict['password'],
            "secretManagement": {
                "automaticManagementEnabled": True
            }
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {session_token}'
        }
        response = requests.request("POST", url, headers=headers, data=payload, timeout=30)
        print(f"Account Response Message: {response.text}")
        if response.status_code == 201:
            print(f"Account {cyberark_dict['account']} onboarded successfully")
        elif response.status_code == 409:
            print(f"Account {cyberark_dict['account']} already exists")
        else:
            return {
                'statusCode': 500,
                'body': json.dumps(f"There was a problem onboarding account {cyberark_dict['account']}")
            }

        return {
            'statusCode': 200,
            'body': json.dumps(f"Tags retrieved for secret {secret_id}: {tags}")
        }

    except ClientError as e:
        print(f"An error occurred: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error retrieving tags for secret: {e}")
        }
