from abc import ABC, abstractmethod
import uuid

# ==============================
# Snippet 1: Cart Component (Repository Pattern)
# ==============================


class Cart:
    """Domain model representing a shopping cart with unique identity and items."""

    def __init__(self, cart_id=None):
        self.id = cart_id or str(uuid.uuid4())
        self.items = []

    def add_item(self, item, quantity):
        """Adds an item and quantity to the cart."""
        self.items.append((item, quantity))
        print(f"Added {quantity} {item}(s) to cart {self.id}.")


class CartRepository:
    """Repository responsible for cart persistence operations."""

    def __init__(self):
        self._store = {}

    def create(self, cart_id=None):
        """Creates and stores a new cart."""
        cart = Cart(cart_id)
        self._store[cart.id] = cart
        return cart

    def get(self, cart_id):
        """Retrieves an existing cart by ID."""
        return self._store.get(cart_id)

    def save(self, cart):
        """Saves the current state of a cart."""
        self._store[cart.id] = cart
        return cart

    def merge(self, source_id, target_id):
        """Merges items from one cart into another, removing the source."""
        source = self._store.get(source_id)
        target = self._store.get(target_id)
        if not source or not target:
            return None
        target.items.extend(source.items)
        self._store.pop(source_id, None)
        return target


# ==============================
# Snippet 2: Payment Component (Strategy Pattern)
# ==============================

class PaymentProcessor(ABC):
    """Interface defining the contract for all payment processors."""
    @abstractmethod
    def process_payment(self, amount):
        pass


class CreditCardProcessor(PaymentProcessor):
    """Concrete strategy for credit card payments."""

    def process_payment(self, amount):
        print(f"Processing {amount} via Credit Card.")


class PayPalProcessor(PaymentProcessor):
    """Concrete strategy for PayPal payments."""

    def process_payment(self, amount):
        print(f"Processing {amount} via PayPal.")


class ProcessorRegistry:
    """Registry for managing available payment strategies."""

    def __init__(self):
        self._processors = {}

    def register(self, method, processor):
        """Registers a payment processor by method name."""
        self._processors[method] = processor

    def get(self, method):
        """Retrieves a processor by method name or raises an error if unsupported."""
        processor = self._processors.get(method)
        if not processor:
            raise ValueError("Unsupported payment method.")
        return processor


# Registry configuration
registry = ProcessorRegistry()
registry.register("credit_card", CreditCardProcessor())
registry.register("paypal", PayPalProcessor())


def process_payment(method, amount):
    """Selects and executes the appropriate payment processor."""
    processor = registry.get(method)
    processor.process_payment(amount)


# ==============================
# Snippet 3: Inventory Component (Façade Pattern)
# ==============================

class InventoryRepository:
    """Repository abstraction for storing item quantities."""

    def __init__(self):
        self._stock = {}

    def get_quantity(self, item):
        """Returns current stock level for an item."""
        return self._stock.get(item, 0)

    def set_quantity(self, item, quantity):
        """Sets stock level for an item."""
        self._stock[item] = quantity

    def all(self):
        """Returns a snapshot of all stock quantities."""
        return dict(self._stock)


class InventoryService:
    """Façade providing simplified inventory operations."""

    def __init__(self, repository):
        self.repository = repository

    def add_stock(self, item, quantity):
        """Adds stock for an item."""
        current = self.repository.get_quantity(item)
        self.repository.set_quantity(item, current + quantity)
        print(f"Added {quantity} {item}(s) to inventory.")

    def remove_stock(self, item, quantity):
        """Removes stock with nonnegative validation."""
        current = self.repository.get_quantity(item)
        if current >= quantity:
            self.repository.set_quantity(item, current - quantity)
            print(f"Removed {quantity} {item}(s) from inventory.")
        else:
            print(f"Not enough {item} in stock to remove {quantity} units.")
