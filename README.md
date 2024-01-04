# Accelerator-ASMOnboardingForSH
### Onboarding of AWS RDS secrets from AWS Secrets Manager to CyberArk Vaults with rotation by CPM and syncing with Secrets Hub

## Goals:
- Show how to enable CyberArk Privilege Cloud to manage AWS RDS secrets that were first created in AWS Secrets Manager.
- Automate onboarding for AWS Relational Database Service (RDS) secrets in AWS Secrets Manager (ASM) to a designated safe in a CyberArk Privilege Cloud vault.
- Enable CPM to rotate secret and SecretsHub to sync secrets back to the same ASM secret.

## Prerequisites
 - Admin access to an AWS account with admin access for Lambda & AWS Secrets Manager services.
 - Admin access to a NON-PRODUCTION Cyberark Identity tenant
 - Admin access to a NON-PRODUCTION CyberArk Privilege Cloud tenant
 - Admin access to a NON-PRODUCTION CyberArk Secrets Hub tenant
 - A Safe in Privilege Cloud with the above service user as member with Access and Account Management permissions, and the 'Conjur Sync' user as member with Access and Workflow permissions.
 - A demo host - a MacOS or Linux VM environment with Docker or Podman installedand IPV4 network access to the CyberArk tenants.
 - Make sure all scripts are executable. Run: chmod -R +x *.sh

## STEP ONE: Manual Setup
   - https://aws.amazon.com/blogs/security/how-to-connect-to-aws-secrets-manager-service-within-a-virtual-private-cloud/
   - https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html
 - create lambda, upload zipfile
 - increase lambda default timeout in Configuration->General Configuration
 - create ASM secret for CyberArk service account:
   - key: subdomain
     value: tenant subdomain prefix
   - key: username
     value: Oauth2 service user username
   - key: password
     value: Oauth2 service user password
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
