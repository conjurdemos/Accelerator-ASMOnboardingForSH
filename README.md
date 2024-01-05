# Accelerator-ASMOnboardingForSH
###Automated onboarding of AWS RDS secrets from AWS Secrets Manager to CyberArk Vaults with rotation by CPM and syncing with Secrets Hub

## Goals:
- Show how to enable CyberArk Privilege Cloud to manage AWS Relational Database Service (RDS) secrets that were first created in AWS Secrets Manager.
- Automate onboarding for RDS secrets in AWS Secrets Manager (ASM) to a designated safe in a CyberArk Privilege Cloud vault.
- Enable CPM to rotate secret and SecretsHub to sync secrets back to the same ASM secret.

## Prerequisites
- Roles:
  - AWS admin user (human)
    - Requires admin rights to:
      - Lambda - to create & test the lambda function
      - AWS Secrets Manager - to create the admin secret
  - CyberArk Privilege Cloud admin (human)
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

## STEP ONE: Privilege Cloud setup
- Role: CyberArk Privilege Cloud admin
- Tasks:
  - Import platforms
  - Create safe w/ SH user as member
    - Name is case sensitive and should not contain spaces.
    - The CyberArk admin service user must be a member with at least Access and Account Management permissions.
    - 'SecretsHub' must be a member with Access and Workflow permissions.

## STEP TWO: AWS Secrets Manager setup
- Role: AWS admin user
- Tasks:
  - Create ASM secret for CyberArk service account:
    - name: whatever you want, this will be the value in an environment variable for lambda to use to retrieve admin credentials
    - key: subdomain, value: subdomain prefix of CyberArk Privilege Cloud tenant
    - key: username, value: username of CyberArk Identity Oauth2 service user
    - key: password, value: password of CyberArk Identity Oauth2 service user
  - Note: any ASM secret to be onboarded must have these tags:
    - CyberArk Safe - name of safe, see specifications above
    - CyberArk Platform - name of platform with RDS-specific properties added
    - CyberArk Account - name to give account in Safe
    - Sourced by CyberArk - no value needed

## STEP THREE: AWS Lambda setup
- Role: AWS admin user
- Tasks:
  - Create lambda, upload deployment-package.sip zipfile
  - Cncrease lambda default timeout to 20 seconds in Configuration->General Configuration
  - Create env var named PrivilegeCloudSecret with name of ASM secret
  - Lambda internet access to ASM and CyberArk Privilege Cloud
    - Default lambda environment has internet access, but if you attach it to a VPC, VPC must have a NAT gateway
    - https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html
    - https://aws.amazon.com/blogs/security/how-to-connect-to-aws-secrets-manager-service-within-a-virtual-private-cloud/

### Sequence Diagram:
![Onboarding Workflow](https://github.com/conjurdemos/Accelerator-ASMOnboardingForSH/blob/main/Onboarding-Workflow.png?raw=true)

## Description of Demo

## Description of Repo Contents
