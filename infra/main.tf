terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ---------------------------------------------
# 1. CREATE S3 BUCKET (NO ACL HERE)
# ---------------------------------------------
resource "aws_s3_bucket" "weather_data_bucket" {
  bucket = "${var.project_name}-bucket"

  tags = {
    Name        = "${var.project_name}-bucket"
    Environment = "dev"
  }
}

# ---------------------------------------------
# 2. ENABLE ACLs VIA OWNERSHIP CONTROLS
#    (THIS TURNS OFF "Bucket owner enforced")
# ---------------------------------------------
resource "aws_s3_bucket_ownership_controls" "ownership" {
  bucket = aws_s3_bucket.weather_data_bucket.id

  rule {
    # Allows ACLs to be used
    object_ownership = "ObjectWriter"
    # alternatives: "BucketOwnerPreferred"
  }
}

# ---------------------------------------------
# 3. UNTICK ALL BLOCK PUBLIC ACCESS SETTINGS
# ---------------------------------------------
resource "aws_s3_bucket_public_access_block" "public_access" {
  bucket = aws_s3_bucket.weather_data_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false

  depends_on = [
    aws_s3_bucket_ownership_controls.ownership
  ]
}

# ---------------------------------------------
# 4. SET BUCKET ACL TO PUBLIC-READ
# ---------------------------------------------
resource "aws_s3_bucket_acl" "bucket_acl" {
  bucket = aws_s3_bucket.weather_data_bucket.id
  acl    = "public-read"

  depends_on = [
    aws_s3_bucket_public_access_block.public_access
  ]
}

# ---------------------------------------------
# 5. BUCKET POLICY: PUBLIC READ FOR ALL OBJECTS
# ---------------------------------------------
resource "aws_s3_bucket_policy" "public_read_policy" {
  bucket = aws_s3_bucket.weather_data_bucket.id

  depends_on = [
    aws_s3_bucket_acl.bucket_acl
  ]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowPublicRead"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.weather_data_bucket.arn}/*"
      }
    ]
  })
}
