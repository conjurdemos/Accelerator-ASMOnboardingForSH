# Accelerator-ASMOnboardingForSH
###Automated onboarding of AWS RDS secrets from AWS Secrets Manager to CyberArk Vaults with rotation by CPM and syncing with Secrets Hub

## Goals:
- Show how to enable CyberArk Privilege Cloud to manage AWS RDS secrets that were first created in AWS Secrets Manager.
- Automate onboarding for AWS Relational Database Service (RDS) secrets in AWS Secrets Manager (ASM) to a designated safe in a CyberArk Privilege Cloud vault.
- Enable CPM to rotate secret and SecretsHub to sync secrets back to the same ASM secret.

## Prerequisites
- Roles:
  - AWS interactive user
    - Requires admin rights to:
      - Lambda - to create & test the lambda function
      - AWS Secrets Manager - to create the admin secret
  - CyberArk Identity user (human)
    - Requires admin rights to a NON-PRODUCTION tenant for Privilege Cloud
    - Imports platforms for ASM RDS accounts
    - Creates safes for secret onboarding
  - CyberArk Identity service user (non-human Oauth2 confidential client)
    - Requires admin rights to NON-PRODUCTION tenants for:
      - CyberArk Privilege Cloud - to onboard secret
      - CyberArk Secrets Hub - to create sync policies
- Resources:
  - A Safe in Privilege Cloud with:
    - the CyberArk Identity service user as safe member with Access and Account Management permissions, and
    - the 'SecretsHub' user as member with Access and Workflow permissions.
  - Make sure all scripts are executable. Run: chmod -R +x *.sh

## STEP ONE: Manual Setup
   - https://aws.amazon.com/blogs/security/how-to-connect-to-aws-secrets-manager-service-within-a-virtual-private-cloud/
   - https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html
 - create lambda, upload zipfile
 - increase lambda default timeout in Configuration->General Configuration
 - create ASM secret for CyberArk service account:
   - key: subdomain
     value: subdomain prefix CyberArk Privilege Cloud tenant
   - key: username
     value: username of CyberArk Identity Oauth2 service user
   - key: password
     value: password of CyberArk Identity Oauth2 service user 
 - create env var named PrivilegeCloudSecret with name of ASM secret.

ASM secrets must have these tags:
CyberArk Safe
CyberArk Platform
CyberArk Account
Sourced by CyberArk

   - SAFE_NAME
     - Must be the name of an existing safe.
     - Name is case sensitive and should not contain spaces.
     - The CyberArk admin service user must be a member with at least Access and Account Management permissions.
     - 'Conjur Sync' must be a member with Access and Workflow permissions.

## STEP TWO: Start Script

## Use-Case 1 - Ansible plugin

## Use-Case 3 - Password rotation

### Sequence Diagram:
![Onboarding Workflow](https://github.com/conjurdemos/Accelerator-ASMOnboardingForSH/blob/main/Onboarding-Workflow.png?raw=true)

## Description of Demo

## Description of Repo Contents
