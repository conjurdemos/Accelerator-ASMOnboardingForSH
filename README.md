# Accelerator-ASMOnboardingForSH
### Automated onboarding of AWS RDS secrets from AWS Secrets Manager to CyberArk Vaults, for rotation by CPM and syncing with Secrets Hub

## Goals:
- Automate onboarding for RDS secrets in AWS Secrets Manager (ASM) to a designated safe in a CyberArk Privilege Cloud vault.
- Show how CyberArk Privilege Cloud can manage AWS Relational Database Service (RDS) secrets that were first created in AWS Secrets Manager.
- Enable SecretsHub to sync secrets back to the same ASM secret without loss of information.
- Enable CPM to rotate database credential.

## Prerequisites
- Roles:
  - **CyberArk Admin (human)**
    - Imports platforms for ASM accounts and creates safes for secret onboarding
    - Creates Oauth2 service user identity for lambda to use for onboarding
    - CyberArk Identity least-privilege role required:
      - System Adminstrator
  - **CyberArk Identity service user (non-human Oauth2 confidential client)**
    - Creates accounts in safes and creates Secrets Hub sync policies
    - CyberArk Identity least-privilege roles required:
      - Privilege Cloud Users
      - Secrets Manager - Secrets Hub Administrators
  - **AWS admin user (human)**
    - Requires admin rights to:
      - Lambda Service - to create & test the lambda function
      - AWS Secrets Manager - to create the CyberArk admin secret, and tag secrets for onboarding
  - **AWS IAM role for lambda**
    - Retrieves secret tags and values
    - Least-privilege permissions required:
      - Allow: secretsmanager:ListSecrets
      - Allow: secretsmanager:GetSecretValue
      - Allow: secretsmanager:DescribeSecret
- Resources:
  - A Safe in Privilege Cloud with:
    - the CyberArk Identity Oauth2 service user as safe member with preset Account Managers permissions
    - **Be sure to use the "Account Managers" preset.**
  - An ASM secret containing values for CyberArk Identity Oauth2 service user credentials and tenant subdomain.
  - An RDS secret in ASM, tagged as described below.
  - The provided lambda function, configured as below.

## Setup
### Step One: Privilege Cloud setup
- Role: CyberArk Privilege Cloud admin
- Tasks:
  - Import platforms for relevant RDS databases (see platformlib directory in this repo)
  - In Privilege Cloud->Adminstration->Configuration Options, add "SecretNameInSecretStore" to Search Properties 
    ![Pcloud Admin Config](https://github.com/conjurdemos/Accelerator-ASMOnboardingForSH/blob/main/img/Pcloud-Admin-Add-SearchProperty.png?raw=true)
    ![Pcloud Property Added](https://github.com/conjurdemos/Accelerator-ASMOnboardingForSH/blob/main/img/Pcloud-Added-SecretNameInSecretStore.png?raw=true)
    - Create safe w/ Oauth2 service user as member
    - The CyberArk admin service user must be a member with Account Managers permissions.

### Step Two: AWS Secrets Manager setup
- Role: AWS admin user
- Tasks:
  - Create ASM secret for CyberArk service account credentials:
    - secret name: whatever you want, this name will be stored in an environment variable for the lambda to use to retrieve admin credentials
    - secret values:
      - key: subdomain, value: subdomain prefix of CyberArk Privilege Cloud tenant
      - key: username, value: username of CyberArk Identity Oauth2 service user
      - key: password, value: password of CyberArk Identity Oauth2 service user
    - secret tags: none required
    ![Admin secret](https://github.com/conjurdemos/Accelerator-ASMOnboardingForSH/blob/main/img/admin-secret.png?raw=true)
  - Create an RDS secret for onboarding:
    - secret name: whatever you want, this value will be extracted from a test event
    - secret values: automatically created per the RDS database
    ![Onboarding secret values](https://github.com/conjurdemos/Accelerator-ASMOnboardingForSH/blob/main/img/rds-values.png?raw=true)
    - secret tags:
      - Tag secret for SecretsHub syncing
	- key: Sourced by CyberArk, value: leave empty - no value needed
      - Name of existing Safe to onboard secret into - see step One above
        - key: CyberArk Safe, value: existing safe name
      - Friendly name to give account in Safe
        - key: CyberArk Account, value: new account name

**NOTE**: Take care with capitalization and ensure there are no trailing spaces in keys.

    ![Onboarding secret tags](https://github.com/conjurdemos/Accelerator-ASMOnboardingForSH/blob/main/img/rds-tags.png?raw=true)

### Step Three: AWS Lambda setup
- Role: AWS admin user
- Tasks:
  - Upload deployment-package.zip to create lambda function
  - Set execution evironment to latest Python version
  - Add permissions for ASM access
  ![Lambda config](https://github.com/conjurdemos/Accelerator-ASMOnboardingForSH/blob/main/img/lambda-permissions.png?raw=true)
  - Increase lambda default timeout to 30 seconds in Configuration->General Configuration.
  ![Lambda config](https://github.com/conjurdemos/Accelerator-ASMOnboardingForSH/blob/main/img/lambda-config.png?raw=true)
  ![Lambda timeout](https://github.com/conjurdemos/Accelerator-ASMOnboardingForSH/blob/main/img/lambda-timeout.png?raw=true)
  - Create env var named PrivilegeCloudSecret with name of ASM secret for the CyberArk service account credentials.
  ![Lambda env var](https://github.com/conjurdemos/Accelerator-ASMOnboardingForSH/blob/main/img/lambda-env-vars.png?raw=true)
  - Add the test events, edited with the name of the secret to onboard/offboard.
  ![Lambda test event](https://github.com/conjurdemos/Accelerator-ASMOnboardingForSH/blob/main/img/test-event.png?raw=true)
  - Lambda internet access
    - Default lambda environment has internet access, but if you attach it to a VPC, the VPC must have a NAT gateway configured.
    - https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html
    - https://aws.amazon.com/blogs/security/how-to-connect-to-aws-secrets-manager-service-within-a-virtual-private-cloud/

### Sequence Diagram:
![Onboarding Workflow](https://github.com/conjurdemos/Accelerator-ASMOnboardingForSH/blob/main/img/ASMOnboardingFlow.png?raw=true)
Edit ./img/ASMOnboardingFlow.txt with https://sequencediagram.org

