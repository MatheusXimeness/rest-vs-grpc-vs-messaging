# Estágio 1: gera o código Python do contrato gRPC (communication/grpc/proto).
# O contexto "proto" é passado pelo docker-compose (additional_contexts).
FROM python:3.12-slim AS gerador-proto
RUN pip install --no-cache-dir grpcio-tools==1.66.2
COPY --from=proto ecommerce.proto /proto/
RUN mkdir /gen && python -m grpc_tools.protoc -I/proto --python_out=/gen --grpc_python_out=/gen /proto/ecommerce.proto

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY --from=gerador-proto /gen/ ./

EXPOSE 8003
# 50051: servidor gRPC (só atende quando COMMUNICATION_STRATEGY=grpc)
EXPOSE 50051

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
