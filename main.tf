resource "aws_api_gateway_rest_api" "api" {
  name = "MontyCloud_L2_API"
  binary_media_types = [ "multipart/form-data", "image/*"]
}

resource "aws_api_gateway_resource" "upload_resource" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "upload"
}

resource "aws_api_gateway_method" "upload_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.upload_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "upload_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.upload_resource.id
  http_method             = aws_api_gateway_method.upload_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.uploadImageLambdaFunction.invoke_arn
}

resource "aws_api_gateway_resource" "list_search_resource" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "list_search"
}

resource "aws_api_gateway_method" "list_search_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.list_search_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "list_search_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.list_search_resource.id
  http_method             = aws_api_gateway_method.list_search_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.listSearchImageLambdaFunction.invoke_arn
}

resource "aws_api_gateway_resource" "view_download_resource" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "view-download"
}

resource "aws_api_gateway_resource" "view_download_operation_resource" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.view_download_resource.id
  path_part   = "{operation}"
}

resource "aws_api_gateway_resource" "view_download_operation_image_resource" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.view_download_operation_resource.id
  path_part   = "{imageName}"
}

resource "aws_api_gateway_method" "view_download_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.view_download_operation_image_resource.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "view_download_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.view_download_operation_image_resource.id
  http_method             = aws_api_gateway_method.view_download_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.viewDownloadImageLambdaFunction.invoke_arn
}

resource "aws_api_gateway_resource" "delete_resource" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "delete"
}

resource "aws_api_gateway_resource" "delete_image_resource" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_resource.delete_resource.id
  path_part   = "{imageName+}"
}

resource "aws_api_gateway_method" "delete_method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.delete_image_resource.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "delete_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.delete_image_resource.id
  http_method             = aws_api_gateway_method.delete_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.deleteImageLambdaFunction.invoke_arn
}

resource "aws_lambda_layer_version" "lambda_layer" {
  layer_name = "lambda_layer"
  compatible_runtimes = ["python3.9"]
  filename = "lambdas/layer/layer.zip"
  source_code_hash = filebase64sha256("lambdas/layer/layer.zip")
}

resource "aws_lambda_function" "uploadImageLambdaFunction" {
  filename         = "lambdas/upload/lambda.zip"
  function_name    = "upload-image"
  role             = aws_iam_role.role.arn
  handler          = "lambda.handler"
  source_code_hash = filebase64sha256("lambdas/upload/lambda.zip")
  runtime          = "python3.9"
  layers = [aws_lambda_layer_version.lambda_layer.arn]
  timeout          = 60
  memory_size      = 512
}

resource "aws_lambda_function" "listSearchImageLambdaFunction" {
  filename         = "lambdas/list-search/lambda.zip"
  function_name    = "list-search-image"
  role             = aws_iam_role.role.arn
  handler          = "lambda.handler"
  source_code_hash = filebase64sha256("lambdas/list-search/lambda.zip")
  runtime          = "python3.9"
  layers = [aws_lambda_layer_version.lambda_layer.arn]
  timeout          = 60
  memory_size      = 512
}

resource "aws_lambda_function" "viewDownloadImageLambdaFunction" {
  filename         = "lambdas/view-download/lambda.zip"
  function_name    = "view-download-image"
  role             = aws_iam_role.role.arn
  handler          = "lambda.handler"
  source_code_hash = filebase64sha256("lambdas/view-download/lambda.zip")
  runtime          = "python3.9"
  layers = [aws_lambda_layer_version.lambda_layer.arn]
  timeout          = 60
  memory_size      = 512
}

resource "aws_lambda_function" "deleteImageLambdaFunction" {
  filename         = "lambdas/delete/lambda.zip"
  function_name    = "delete-image"
  role             = aws_iam_role.role.arn
  handler          = "lambda.handler"
  source_code_hash = filebase64sha256("lambdas/delete/lambda.zip")
  runtime          = "python3.9"
  layers = [aws_lambda_layer_version.lambda_layer.arn]
  timeout          = 60
  memory_size      = 512
}

resource "aws_lambda_permission" "apigw_upload_image_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.uploadImageLambdaFunction.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.api.execution_arn}/*/*/*"
}

resource "aws_lambda_permission" "apigw_list_search_image_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.listSearchImageLambdaFunction.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.api.execution_arn}/*/*/*"
}

resource "aws_lambda_permission" "apigw_view_download_image_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.viewDownloadImageLambdaFunction.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.api.execution_arn}/*/*/*"
}

resource "aws_lambda_permission" "apigw_delete_image_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.deleteImageLambdaFunction.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_rest_api.api.execution_arn}/*/*/*"
}

data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "role" {
  name = "lambda_function_role"

  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json

  inline_policy {
    name = "s3_policy"

    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action   = ["s3:*"]
          Effect   = "Allow"
          Resource = "*"
        },
      ]
    })
  }

  inline_policy {
    name = "ddb_policy"

    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action   = ["dynamodb:*"]
          Effect   = "Allow"
          Resource = "*"
        },
      ]
    })
  }
}

resource "aws_api_gateway_deployment" "deployment" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = "dev"

  triggers = {
    redeploy = sha1(jsonencode(aws_api_gateway_integration.upload_integration))
  }
}

resource "aws_dynamodb_table" "my_table" {
  name           = "montycloud_l2_file_metadata_table"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"
  attribute {
    name = "id"
    type = "S"
  }
}

resource "aws_s3_bucket" "s3_bucket" {
  bucket = "montycloud-l2-storage"
}

output "api_endpoint" {
  value = aws_api_gateway_deployment.deployment.invoke_url
}
