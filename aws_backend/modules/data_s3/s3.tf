resource "aws_s3_bucket" "data_bucket" {
  bucket = "eoh-data-bucket"
}

resource "aws_s3_bucket_lifecycle_configuration" "bucket_day_expiration" {
  bucket = aws_s3_bucket.data_bucket.id
  rule {
    id      = "object-day-expiration"
    
    filter {
      prefix  = ""  # Applies to all objects in the bucket
    }
    
    expiration {
      days = 10  # Set to delete objects after 10 day
    }

    status = "Enabled"
  }
}