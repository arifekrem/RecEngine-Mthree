variable "aws_region" {
  default = "us-east-2"
}

variable "public_key_path" {
  default     = "~/.ssh/id_rsa.pub"
  description = "Path to your local SSH public key"
}