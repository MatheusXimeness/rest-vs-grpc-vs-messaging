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
