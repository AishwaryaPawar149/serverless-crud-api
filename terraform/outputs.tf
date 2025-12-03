output "api_endpoint" {
  description = "API Gateway endpoint URL"
  value       = "${aws_api_gateway_deployment.api_deployment.invoke_url}"
}

output "dynamodb_table_name" {
  description = "DynamoDB table name"
  value       = aws_dynamodb_table.items_table.name
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.api_function.function_name
}

output "s3_bucket_name" {
  description = "S3 bucket for Lambda artifacts"
  value       = aws_s3_bucket.lambda_bucket.id
}
