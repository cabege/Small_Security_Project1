# AWS 리소스 설정을 위한 프로바이더 정의
provider "aws" {
  region = "ap-northeast-2" 
}

# [S3] 버전 관리가 비활성화된 S3 버킷
resource "aws_s3_bucket" "vulnerable_bucket" {
  bucket = "shy-s3-bucket"

  tags = {
    Name        = "VulnerableBucket"
    Environment = "Dev"
  }
}

# [EC2] SSH 포트(22)가 모든 IP(0.0.0.0/0)에 열려있는 보안 그룹
resource "aws_security_group" "vulnerable_sg" {
  name        = "vulnerable-sg"
  description = "Allow all"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # 취약점
  }
}

# 위 보안 그룹을 사용하는 EC2 인스턴스
resource "aws_instance" "web_server" {
  ami           = "ami-099099dff4384719c"
# EC2 인스턴스 생성할때 Amazon Machine을 정할 수 있는데, 거기에서 ami-~~~의 최신버전 사용(x86)
  instance_type = "t2.micro"
  security_groups = [aws_security_group.vulnerable_sg.name]

  tags = {
    Name = "VulnerableWebServer"
  }
}

# [RDS] 암호화가 비활성화된 RDS 데이터베이스 인스턴스
resource "aws_db_instance" "vulnerable_db" {
  allocated_storage    = 10
  engine               = "mysql"
  engine_version       = "5.7"
  instance_class       = "db.t2.micro"
  db_name              = "mydb"
  username             = "user"
  password             = "password" # 하드코딩된 비밀번호 (취약점)
  skip_final_snapshot  = true
  storage_encrypted    = false # 암호화 비활성화 (취약점)
}


#PR용 주석1