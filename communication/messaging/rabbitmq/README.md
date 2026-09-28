# Contrato de mensageria (RabbitMQ / AMQP 0-9-1)

A estratégia de mensageria usa o padrão **RPC sobre fila** (request/reply) para as
operações cujo resultado o fluxo de pedido precisa conhecer, e **evento sem resposta**
(fire-and-forget) para a liberação de estoque, que não altera o resultado do pedido.

| Fila                | Produtor | Consumidor | Tipo            | Payload da requisição                          | Resposta                                          |
|---------------------|----------|------------|-----------------|------------------------------------------------|---------------------------------------------------|
| `usuario.get_user`  | pedidos  | usuario    | RPC             | `{"user_id": "user-1"}`                        | `{"status": 200, "id", "name", "email"}`          |
| `estoque.reserve`   | pedidos  | estoque    | RPC             | `{"product_id": "mouse", "quantity": 1}`       | `{"status": 200, "product_id", "quantity", "reserved"}` |
| `estoque.release`   | pedidos  | estoque    | evento          | `{"product_id": "mouse", "quantity": 1}`       | —                                                 |
| `pagamento.process` | pedidos  | pagamento  | RPC             | `{"order_id", "user_id", "amount": "50.00"}`   | `{"status": 200, "id", "order_id", "approved", "transaction_id", "decline_reason"}` |

Todas as mensagens são JSON (UTF-8), com os mesmos campos do REST, para que a
comparação varie só o transporte.

## Como funciona o RPC sobre fila

1. O serviço de pedidos declara uma fila de resposta exclusiva (nome gerado pelo broker).
2. Para cada chamada, publica a requisição na fila do serviço com `reply_to` = fila de
   resposta e um `correlation_id` único.
3. O consumidor processa, publica a resposta em `reply_to` com o mesmo `correlation_id`
   e confirma (`ack`) a mensagem original.
4. O pedidos casa a resposta com a chamada pendente pelo `correlation_id`.

O campo `status` da resposta usa os códigos HTTP equivalentes (200, 404, 422, 500),
para que as métricas e o tratamento de erro sejam comparáveis entre as estratégias.

## Configuração

- Filas não duráveis e mensagens transitórias: requisições RPC são efêmeras (se o
  broker reiniciar, o chamador já terá desistido por timeout), e a persistência em disco
  adicionaria custo que não existe nas outras estratégias.
- `prefetch_count` (padrão 100): quantas mensagens cada consumidor processa em paralelo.
- Timeout do lado do chamador: 10 s, igual ao do cliente HTTP e ao deadline do gRPC.

A configuração do broker está em `infrastructure/docker/rabbitmq/rabbitmq.conf`.
