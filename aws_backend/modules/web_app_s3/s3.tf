resource "aws_s3_bucket" "web_bucket" {
  bucket = "eoh-web-app-bucket"
}

resource "aws_s3_bucket_policy" "web_bucket_policy" {
  bucket = aws_s3_bucket.web_bucket.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        "Sid" : "AllowCloudFrontServicePrincipal",
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "cloudfront.amazonaws.com"
        },
        "Action" : "s3:GetObject",
        "Resource" : "arn:aws:s3:::${aws_s3_bucket.web_bucket.id}/*",
        "Condition" : {
          "StringEquals" : {
            "AWS:SourceArn" : "${var.cloudfront_arn}"
          }
        }
      }
    ]
  })
}

