"""Module to retrieve metadata from a secret in AWS Secrets Manager
and use them to onboard the secret to CyberArk Privilege Cloud"""
import json
import os
import urllib.parse
import requests
import boto3
from botocore.exceptions import ClientError

# CONSTANTS
DEBUG = False

# environment variable containing name of Pcloud admin secret in ASM
PCLOUD_ADMIN_SECRET_ENV_VAR = "PrivilegeCloudSecret"


# -------------------------------------------
def urlify(s):
    # URL encodes a given string
    return urllib.parse.quote(s)


# -------------------------------------------
def prologOut(event, context):
    if DEBUG:
        print("Received event: " + json.dumps(event, indent=2))

    # Print the context to see its structure (useful for debugging)
    print("Lambda function ARN: " + context.invoked_function_arn)
    print("CloudWatch log stream name: " + context.log_stream_name)
    print("CloudWatch log group name: " + context.log_group_name)
    print("Lambda Request ID: " + context.aws_request_id)
    print("Lambda function memory limits in MB: " + context.memory_limit_in_mb)


# -------------------------------------------
def validateSecretTags(secrets_manager_client, secret_id):
    # Validate secret is tagged w/ 'Sourced by CyberArk' - if not, flag as not found
    # returns dictionary of secret tags, status_code & response_body message

    tags_dict = {}
    status_code = 200
    response_body = f"Secret {secret_id} sourced by CyberArk"

    # Retrieve tags of the secret
    try:
        response = secrets_manager_client.describe_secret(SecretId=secret_id)
    except ClientError as e:
        status_code = 500
        response_body = json.dumps(f"Error retrieving tags for secret: {e}")
    else:
        tags = response.get("Tags", [])
        tags_dict = {tag["Key"]: tag["Value"] for tag in tags}

        if "Sourced by CyberArk" not in tags_dict:
            status_code = 404
            response_body = f"Secret {secret_id} not sourced by CyberArk"

    if DEBUG:
        print("================ validateSecretTags() ================")
        print(f"\tsecret_id: {secret_id}\n\ttags_dict: {tags_dict}")
        print(f"\tstatus_code: {status_code}\n\tresponse: {response_body}")

    return tags_dict, status_code, response_body


# -------------------------------------------
def getAsmSecretValue(secrets_manager_client, secret_id):
    # uses client & secret_id to retrieve value of secret
    # returns secret_value dictionary, status_code & message for response_body

    secret_value = {}
    status_code = 200
    response_body = "Secret retrieved successfully."

    try:
        response = secrets_manager_client.get_secret_value(SecretId=secret_id)
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            status_code = 404
            response_body = json.dumps(
                f"The requested secret {secret_id} was not found."
            )
        elif e.response["Error"]["Code"] == "AccessDeniedException":
            status_code = 403
            response_body = json.dumps(
                f"Access to the requested secret {secret_id} was denied."
            )
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            status_code = 500
            response_body = json.dumps(f"The request was invalid due to: {e}")
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            status_code = 500
            response_body = json.dumps(f"The request had invalid params: {e}")
        elif e.response["Error"]["Code"] == "DecryptionFailure":
            status_code = 500
            response_body = json.dumps(
                f"The requested secret can't be decrypted using the provided KMS key: {e}"
            )
        elif e.response["Error"]["Code"] == "InternalServiceError":
            status_code = 500
            response_body = json.dumps(f"An error occurred on service side: {e}")
        else:
            status_code = 500
            response_body = json.dumps(f"Unknown error: {e}")
    else:
        secret_value = json.loads(response.get("SecretString", None))

    if DEBUG:
        print("================ getAsmSecretValue() ================")
        print(f"\tsecret_id: {secret_id}\n\tsecret_value: {secret_value}")
        print(f"\tstatus_code: {status_code}\n\tresponse: {response_body}")

    return secret_value, status_code, response_body


# -------------------------------------------
def authnCyberArk(cyberark_dict):
    # uses Pcloud creds in cyberark_dict to authenticate to CyberArk Identity
    # returns session_token to use in further CyberArk API calls

    session_token = None
    status_code = 200
    response_body = "Successfully authenticated to CyberArk Privilege Cloud."

    # Authenticate to CyberArk Identity
    url = f"https://{cyberark_dict['subdomain']}.cyberark.cloud/api/idadmin/oauth2/platformtoken"
    payload = f"grant_type=client_credentials&client_id={urlify(cyberark_dict['svc_username'])}&client_secret={urlify(cyberark_dict['svc_password'])}"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.request("POST", url, headers=headers, data=payload, timeout=60)
    if response.status_code == 200:
        # Parse the JSON response into a dictionary
        data = response.json()
        # Extract session token from the response dict
        session_token = data.get("access_token", None)
        if session_token is None:
            status_code = 401
            response_body = json.dumps(
                f"There was a problem authenticating to: {cyberark_dict['subdomain']}.privilegecloud.cyberark.cloud"
            )
    else:
        status_code = 500
        response_body = json.dumps(
            f"There was a problem authenticating to: {cyberark_dict['subdomain']}.privilegecloud.cyberark.cloud"
        )

    if DEBUG:
        print("================ authnCyberark() ================")
        print(f"\tstatus_code: {status_code}\n\tresponse: {response_body}")

    return session_token, status_code, response_body

# -------------------------------------------
def createSafe(cyberark_dict, session_token):
    # Uses info in dictionary to create a safe in Privilege Cloude
    # returns status_code == 201 on success with response_body message

    status_code = 201
    response_body = f"Safe {cyberark_dict['safe']} created successfully"

    url = f"https://{cyberark_dict['subdomain']}.privilegecloud.cyberark.cloud/passwordvault/api/safes"
    payload = json.dumps(
        {
            "safeName": cyberark_dict["safe"],
            "description": "Created by AWS Secrets Manager",
            "olacEnabled": False,
            "managingCPM": "PasswordManager",
            "numberOfDaysRetention": 0,
        }
    )
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {session_token}",
    }
    response = requests.request("POST", url, headers=headers, data=payload, timeout=30)
    if response.status_code == 409:
        status_code = 409
        response_body = json.dumps(f"Safe {cyberark_dict['safe']} already exists")
    else:
        status_code = 500
        response_body = response.text

    if DEBUG:
        print("================ createSafe() ================")
        print(f"\tstatus_code: {status_code}\n\tresponse: {response_body}")

    return status_code, response_body

# -------------------------------------------
def assembleOnboardingDict(pcloud_secret_dict, tags_dict, secret_dict):
    #
    # returns onboarding dictionary, status_code & response_body message

    status_code = 200
    response_body = "Onboarding dictionary assembled successfully."
    cyberark_dict = {
        # values pulled from service account secret
        "subdomain": pcloud_secret_dict.get("subdomain", None),
        "svc_username": pcloud_secret_dict.get("username", None),
        "svc_password": pcloud_secret_dict.get("password", None),
        # values pulled from secret tags - standard CyberArk properties
        "safe": tags_dict.get("CyberArk Safe", None),
        "account": tags_dict.get("CyberArk Account", None),
        # values pulled from RDS secret value - standard CyberArk properties
        "address": secret_dict.get("address", None),
        "username": secret_dict.get("username", None),
        "password": secret_dict.get("password", None),
        "platformId": secret_dict.get("platformId", None),
        # RDS values pulled from secret value - additional properties in secret
        "dbInstanceIdentifier": secret_dict.get("dbInstanceIdentifier", None),
        "host": secret_dict.get("host", None),
        "engine": secret_dict.get("engine", None),
        "port": secret_dict.get("port", None),
    }

    # If no address, get secret value for 'host', if any
    if cyberark_dict["address"] is None:
        cyberark_dict["address"] = secret_dict.get("host", None)

    # If no platformId, get value for 'CyberArk Platform' tag, if any
    if cyberark_dict["platformId"] is None:
        cyberark_dict["platformId"] = tags_dict.get("CyberArk Platform", None)

    # Validate no keys contain None as a value, if any, exit w/ 404
    none_keys = [key for key, value in cyberark_dict.items() if value is None]
    if none_keys:
        status_code = 404
        response_body = json.dumps(f"Required key value(s) not found: {none_keys}")

    if DEBUG:
        print("================ assembleOnboardingDict() ================")
        print(f"\ncyberark_dict: {cyberark_dict}")
        print(f"\tstatus_code: {status_code}\n\tresponse: {response_body}")

    return cyberark_dict, status_code, response_body

# -------------------------------------------
def onboardAccount(cyberark_dict, session_token):
    # uses values in cyberark_dict to create account
    # returns status_code == 201 for success, response_body with message

    status_code = 201
    response_body = json.dumps(
        f"Account {cyberark_dict['account']} onboarded successfully"
    )

    url = f"https://{cyberark_dict['subdomain']}.privilegecloud.cyberark.cloud/passwordvault/api/accounts"
    payload = json.dumps(
        {
            "safeName": cyberark_dict["safe"],
            "platformID": cyberark_dict["platformId"],
            "name": cyberark_dict["account"],
            "address": cyberark_dict["address"],
            "userName": cyberark_dict["username"],
            "secretType": "password",
            "secret": cyberark_dict["password"],
            "secretManagement": {"automaticManagementEnabled": True},
            "platformAccountProperties": {
                "port": cyberark_dict["port"],
                "host": cyberark_dict["host"],
                "dbInstanceIdentifier": cyberark_dict["dbInstanceIdentifier"],
                "engine": cyberark_dict["engine"],
            },
        }
    )
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {session_token}",
    }
    response = requests.request("POST", url, headers=headers, data=payload, timeout=30)
    if response.status_code == 409:
        status_code = 409
        response_body = json.dumps(f"Account {cyberark_dict['account']} already exists")
    else:
        status_code = 500
        response_body = json.dumps(f"{response.text}")

    if DEBUG:
        print("================ onboardAccount() ================")
        print(f"\turl: {url}\n\tpayload: {payload}")
        print(f"\tstatus_code: {status_code}\n\tresponse: {response_body}")

    return status_code, response_body

##########################################################################################
# Lambda function handler (main entrypoint)
##########################################################################################

def lambda_handler(event, context):
    prologOut(event, context)

    # Extract the ID of secret to onboard from the triggering event
    secret_id = event["detail"]["requestParameters"]["name"]

    # Initialize a client for AWS Secrets Manager
    secrets_manager_client = boto3.client("secretsmanager")

    # Validate secret is correctly tagged for onboarding
    tags_dict, status_code, response_body = validateSecretTags(
        secrets_manager_client, secret_id
    )
    if status_code != 200:
        return {"statusCode": status_code, "body": response_body}

    # Retrieve from env var the ID of ASM secret storing admin creds
    pcloud_secret_id = os.environ.get(PCLOUD_ADMIN_SECRET_ENV_VAR, None)
    if pcloud_secret_id is None:
        response_body = f"Env var '{PCLOUD_ADMIN_SECRET_ENV_VAR}' not found in lambda environment variables."
        return {"statusCode": 404, "body": response_body}

    # Get Pcloud admin creds from ASM
    pcloud_secret_dict, status_code, response_body = getAsmSecretValue(
        secrets_manager_client, pcloud_secret_id
    )
    if status_code != 200:
        return {"statusCode": status_code, "body": response_body}

    # Retrieve the value of the secret to onboard
    secret_dict, status_code, response_body = getAsmSecretValue(
        secrets_manager_client, secret_id
    )
    if status_code != 200:
        return {"statusCode": status_code, "body": response_body}

    # Assemble all info into a single onboarding dictionary
    onboarding_dict, status_code, response_body = assembleOnboardingDict(
        pcloud_secret_dict, tags_dict, secret_dict
    )
    if status_code != 200:
        return {"statusCode": status_code, "body": response_body}

    # Authenticate to Privilege Cloud
    session_token, status_code, response_body = authnCyberArk(onboarding_dict)
    if status_code != 200:
        return {"statusCode": status_code, "body": response_body}

    # Create safe in Privilege Cloud
    status_code, response_body = createSafe(onboarding_dict, session_token)
    if status_code != 201:
        return {"statusCode": status_code, "body": response_body}

    # Onboard account into safe
    status_code, response_body = onboardAccount(onboarding_dict, session_token)
    if status_code != 201:
        return {"statusCode": status_code, "body": response_body}

    return {"statusCode": 200, "body": f"Secret {secret_id} onboarded successfully."}
