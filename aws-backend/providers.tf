terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  backend "s3" {
    bucket = "eoh-tf-state"      # S3 bucket where the state file will be stored
    key    = "terraform.tfstate" # Path within the S3 bucket (e.g., "terraform/state.tfstate")
    region = "us-east-1"      # AWS region for the S3 bucket
  }
}

provider "aws" {
  region = "us-east-1"  # Change this as needed
}