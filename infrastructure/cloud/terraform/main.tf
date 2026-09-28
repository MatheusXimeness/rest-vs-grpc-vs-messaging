# Uma VM que roda exatamente o mesmo docker-compose do ambiente local, com os mesmos
# limites de CPU/memória por contêiner e o k6 no mesmo host. Assim, a única diferença
# entre os ambientes é a infraestrutura (virtualização, hardware e vizinhança da nuvem).

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
}

resource "aws_key_pair" "tcc" {
  key_name_prefix = "tcc-"
  public_key      = file(pathexpand(var.chave_publica_ssh))
}

resource "aws_security_group" "tcc" {
  name_prefix = "tcc-"
  description = "SSH apenas do IP do pesquisador; os servicos nao ficam expostos"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.meu_ip]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "experimento" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.tipo_instancia
  key_name               = aws_key_pair.tcc.key_name
  vpc_security_group_ids = [aws_security_group.tcc.id]
  user_data              = file("${path.module}/cloud-init.yaml")

  root_block_device {
    volume_size = var.disco_gb
    volume_type = "gp3"
  }

  tags = {
    Name = "tcc-experimento"
  }
}
