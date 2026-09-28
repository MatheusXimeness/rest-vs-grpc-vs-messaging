output "ip_publico" {
  value = aws_instance.experimento.public_ip
}

output "ssh" {
  value = "ssh ubuntu@${aws_instance.experimento.public_ip}"
}

output "tipo_instancia" {
  value = aws_instance.experimento.instance_type
}
