# Accelerator-ASMOnboardingForSH
### Automated onboarding of AWS RDS secrets from AWS Secrets Manager to CyberArk Vaults with rotation by CPM and syncing with Secrets Hub

## Goals:
- Show how to enable CyberArk Privilege Cloud to manage AWS Relational Database Service (RDS) secrets that were first created in AWS Secrets Manager.
- Automate onboarding for RDS secrets in AWS Secrets Manager (ASM) to a designated safe in a CyberArk Privilege Cloud vault.
- Enable CPM to rotate secret and SecretsHub to sync secrets back to the same ASM secret.

## Prerequisites
- Roles:
  - **AWS admin user (human)**
    - Requires admin rights to:
      - Lambda - to create & test the lambda function
      - AWS Secrets Manager - to create the admin secret
  - **AWS IAM role for lambda**
    - Retrieves secret tags and values
    - Least-privilege permissions required:
      - Allow: secretsmanager:ListSecrets
      - Allow: secretsmanager:GetSecretValue
      - Allow: secretsmanager:DescribeSecret
  - **CyberArk Privilege Cloud admin (human)**
    - Imports platforms for ASM RDS accounts and creates safes for secret onboarding
    - Least-privilege role required:
      - Privilege Cloud Administrators
  - **CyberArk Identity service user (non-human Oauth2 confidential client)**
    - Creates accounts in safes and creates Secrets Hub sync policies
    - Least-privilege roles required:
      - Privilege Cloud Users
      - Secrets Manager - Secrets Hub Administrators
- Resources:
  - A Safe in Privilege Cloud with:
    - the CyberArk Identity service user as safe member with Access and Account Management permissions, and
    - the 'SecretsHub' user as member with Access and Workflow permissions.
  - An RDS secret in ASM, tagged as described below
  - The provided lambda function, configured as below
  - Make sure all scripts are executable. Run: chmod -R +x *.sh

## Setup
### Step One: Privilege Cloud setup
- Role: CyberArk Privilege Cloud admin
- Tasks:
  - Import platforms
  - Create safe w/ SH user as member
    - Name is case sensitive and should not contain spaces.
    - The CyberArk admin service user must be a member with at least Access and Account Management permissions.
    - 'SecretsHub' must be a member with Access and Workflow permissions.

### Step Two: AWS Secrets Manager setup
- Role: AWS admin user
- Tasks:
  - Create ASM secret for CyberArk service account credentials:
    - secret name: whatever you want, this will be the value in an environment variable for lambda to use to retrieve admin credentials
    - secret values:
      - key: subdomain, value: subdomain prefix of CyberArk Privilege Cloud tenant
      - key: username, value: username of CyberArk Identity Oauth2 service user
      - key: password, value: password of CyberArk Identity Oauth2 service user
    - secret tags: none required
    ![Admin secret](https://github.com/conjurdemos/Accelerator-ASMOnboardingForSH/blob/main/img/admin-secret.png?raw=true)
  - Create a test RDS secret for onboarding:
    - secret name: whatever you want, this value will be extracted from a test event
    - secret values: automatically created per the RDS database
    ![Onboarding secret values](https://github.com/conjurdemos/Accelerator-ASMOnboardingForSH/blob/main/img/rds-values.png?raw=true)
    - secret tags:
      - CyberArk Safe - name of safe, see specifications above
      - CyberArk Platform - name of platform with RDS-specific properties added
      - CyberArk Account - name to give account in Safe
      - Sourced by CyberArk - no value needed
    ![Onboarding secret tags](https://github.com/conjurdemos/Accelerator-ASMOnboardingForSH/blob/main/img/rds-tags.png?raw=true)

### Step Three: AWS Lambda setup
- Role: AWS admin user
- Tasks:
  - Upload deployment-package.zip to create lambda function
  - Increase lambda default timeout to more than 10 seconds in Configuration->General Configuration.
  ![Lambda config](https://github.com/conjurdemos/Accelerator-ASMOnboardingForSH/blob/main/img/lambda-config.png?raw=true)
  ![Lambda timeout](https://github.com/conjurdemos/Accelerator-ASMOnboardingForSH/blob/main/img/lambda-timeout.png?raw=true)
  - Create env var named PrivilegeCloudSecret with name of ASM secret for the CyberArk service account credentials.
  ![Lambda env var](https://github.com/conjurdemos/Accelerator-ASMOnboardingForSH/blob/main/img/lambda-env-vars.png?raw=true)
  - Add the simple test event, edited with the name of the secret to onboard.
  ![Lambda test event](https://github.com/conjurdemos/Accelerator-ASMOnboardingForSH/blob/main/img/test-event.png?raw=true)
  - Lambda internet access
    - Default lambda environment has internet access, but if you attach it to a VPC, the VPC must have a NAT gateway configured.
    - https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html
    - https://aws.amazon.com/blogs/security/how-to-connect-to-aws-secrets-manager-service-within-a-virtual-private-cloud/

### Sequence Diagram:
![Onboarding Workflow](https://github.com/conjurdemos/Accelerator-ASMOnboardingForSH/blob/main/img/Onboarding-Workflow.png?raw=true)

## Description of Demo

## Description of Repo Contents
