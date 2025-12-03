variable "aws_region" {
  description = "AWS Region"
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  default     = "serverless-crud-api"
}

variable "s3_bucket_name" {
  description = "S3 bucket for Lambda code"
}
