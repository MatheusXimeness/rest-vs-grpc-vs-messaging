class OrderNotFoundError(Exception):
    pass


class InvalidOrderStateError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class InsufficientStockError(Exception):
    pass


class PaymentFailedError(Exception):
    pass


class DependencyUnavailableError(Exception):
    """Outro serviço não respondeu (conexão recusada, timeout). É falha técnica, não de negócio."""
