#!/usr/bin/env python3
# d780_microservices_combined.py
# Combined version of D780 Task 2 microservices: Cart, Inventory, Payment, Orchestrator.
# Uses Python stdlib only (no external frameworks).

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse

# Shared helpers


def _read_json(handler):
    length = int(handler.headers.get("Content-Length", 0))
    raw = handler.rfile.read(length) if length > 0 else b"{}"
    try:
        return json.loads(raw.decode("utf-8") or "{}")
    except Exception:
        return {}


def _send(handler, status, payload):
    data = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _amount_str(a):
    try:
        f = float(a)
        return str(int(f)) if f.is_integer() else str(f)
    except Exception:
        return str(a)


def _pretty_method(m):
    if not isinstance(m, str):
        return "Unknown"
    return m.replace("_", " ").title()


# ============================================================
# Cart Service
# ============================================================
CARTS = {}  # { user: { item: qty } }


class CartHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        parts = parsed.path.strip("/").split("/")
        if self.path == "/health":
            return _send(self, 200, {"status": "ok", "service": "cart"})
        if len(parts) == 2 and parts[0] == "cart":
            user = parts[1]
            return _send(self, 200, {"user": user, "cart": CARTS.get(user, {})})
        return _send(self, 404, {"error": "not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        parts = parsed.path.strip("/").split("/")
        if len(parts) == 3 and parts[0] == "cart" and parts[2] == "add":
            user = parts[1]
            data = _read_json(self)
            item = data.get("item")
            qty = int(data.get("quantity", 0))
            if not item or qty <= 0:
                return _send(self, 400, {"error": "item and positive quantity required"})
            cart = CARTS.setdefault(user, {})
            cart[item] = cart.get(item, 0) + qty
            return _send(self, 200, {"message": "added", "user": user, "cart": cart})
        return _send(self, 404, {"error": "not found"})


# ============================================================
# Inventory Service
# ============================================================
STOCK = {}  # { item: int }


class InventoryHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        parts = parsed.path.strip("/").split("/")
        if self.path == "/health":
            return _send(self, 200, {"status": "ok", "service": "inventory"})
        if len(parts) == 2 and parts[0] == "inventory":
            item = parts[1]
            return _send(self, 200, {"item": item, "stock": int(STOCK.get(item, 0))})
        return _send(self, 404, {"error": "not found"})

    def do_PUT(self):
        parsed = urlparse(self.path)
        parts = parsed.path.strip("/").split("/")
        if len(parts) == 2 and parts[0] == "inventory":
            item = parts[1]
            data = _read_json(self)
            qty = int(data.get("quantity", 0))
            if qty < 0:
                return _send(self, 400, {"error": "quantity must be >= 0"})
            STOCK[item] = qty
            return _send(self, 200, {"message": f"{item} stock updated."})
        return _send(self, 404, {"error": "not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        parts = parsed.path.strip("/").split("/")
        if len(parts) == 3 and parts[0] == "inventory":
            item, action = parts[1], parts[2]
            data = _read_json(self)
            qty = int(data.get("quantity", 0))
            if qty <= 0:
                return _send(self, 400, {"error": "quantity must be > 0"})
            current = int(STOCK.get(item, 0))
            if action == "reserve":
                if current < qty:
                    return _send(self, 409, {"error": "insufficient_stock", "available": current})
                STOCK[item] = current - qty
                return _send(self, 200, {"message": "reserved", "item": item, "remaining": STOCK[item]})
            if action == "release":
                STOCK[item] = current + qty
                return _send(self, 200, {"message": "released", "item": item, "stock": STOCK[item]})
        return _send(self, 404, {"error": "not found"})


# ============================================================
# Payment Service
# ============================================================
class PaymentHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            return _send(self, 200, {"status": "ok", "service": "payment"})
        return _send(self, 404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/pay":
            data = _read_json(self)
            method = data.get("method")
            amount = data.get("amount")
            try:
                amt = float(amount)
            except Exception:
                return _send(self, 400, {"error": "amount must be numeric"})
            if amt <= 0:
                return _send(self, 400, {"error": "amount must be > 0"})
            msg = f"Processed {_amount_str(amount)} via {_pretty_method(method)}."
            return _send(self, 200, {"message": msg})
        return _send(self, 404, {"error": "not found"})


# ============================================================
# Orchestrator Service
# ============================================================
INVENTORY_URL = "http://127.0.0.1:5001"
PAYMENT_URL = "http://127.0.0.1:5002"


def _http_get(url):
    req = Request(url, method="GET")
    try:
        with urlopen(req, timeout=5) as r:
            return r.getcode(), json.loads(r.read().decode("utf-8"))
    except HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except Exception:
            return e.code, {"error": "http_error"}
    except URLError as e:
        return 503, {"error": f"unreachable: {e.reason}"}


def _http_post(url, payload):
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers={
                  "Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(req, timeout=5) as r:
            return r.getcode(), json.loads(r.read().decode("utf-8"))
    except HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except Exception:
            return e.code, {"error": "http_error"}
    except URLError as e:
        return 503, {"error": f"unreachable: {e.reason}"}


class OrchestratorHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            return _send(self, 200, {"status": "ok", "service": "orchestrator"})
        return _send(self, 404, {"error": "not found"})

    def do_POST(self):
        if self.path == "/checkout":
            data = _read_json(self)
            item = data.get("item")
            qty = int(data.get("quantity", 0))
            amount = data.get("amount")
            method = data.get("method")

            if not item or qty <= 0:
                return _send(self, 400, {"error": "item and positive quantity required"})
            try:
                amt = float(amount)
            except Exception:
                return _send(self, 400, {"error": "amount must be numeric"})
            if amt <= 0:
                return _send(self, 400, {"error": "amount must be > 0"})

            # Check inventory
            code, inv = _http_get(f"{INVENTORY_URL}/inventory/{item}")
            if code != 200:
                return _send(self, 503, {"error": "inventory_unreachable"})
            if int(inv.get("stock", 0)) < qty:
                return _send(self, 409, {"error": "insufficient_stock", "available": inv.get("stock", 0)})

            # Reserve stock
            code, res = _http_post(
                f"{INVENTORY_URL}/inventory/{item}/reserve", {"quantity": qty})
            if code != 200:
                return _send(self, 409, {"error": "inventory_reserve_failed", "details": res})

            # Process payment
            code, pay = _http_post(
                f"{PAYMENT_URL}/pay", {"method": method, "amount": amt})
            if code != 200:
                _http_post(
                    f"{INVENTORY_URL}/inventory/{item}/release", {"quantity": qty})
                return _send(self, 402, {"error": "payment_failed", "details": pay})

            msg = f"Processed {_amount_str(amount)} via {_pretty_method(method)}."
            return _send(self, 200, {"message": msg})

        return _send(self, 404, {"error": "not found"})


# ============================================================
# Entry Point
# ============================================================
def main():
    global INVENTORY_URL, PAYMENT_URL
    args = sys.argv[1:]
    service = "orchestrator"
    port = 5000

    i = 0
    while i < len(args):
        if args[i] == "--service" and i + 1 < len(args):
            service = args[i + 1]
            i += 2
            continue
        if args[i] == "--port" and i + 1 < len(args):
            port = int(args[i + 1])
            i += 2
            continue
        if args[i] == "--inventory" and i + 1 < len(args):
            INVENTORY_URL = f"http://127.0.0.1:{int(args[i + 1])}"
            i += 2
            continue
        if args[i] == "--payment" and i + 1 < len(args):
            PAYMENT_URL = f"http://127.0.0.1:{int(args[i + 1])}"
            i += 2
            continue
        i += 1

    if service == "cart":
        handler = CartHandler
    elif service == "inventory":
        handler = InventoryHandler
    elif service == "payment":
        handler = PaymentHandler
    else:
        handler = OrchestratorHandler

    server = ThreadingHTTPServer(("0.0.0.0", port), handler)
    print(f"{service.title()} service listening on http://0.0.0.0:{port}")
    if service == "orchestrator":
        print(
            f"Using INVENTORY_URL={INVENTORY_URL}, PAYMENT_URL={PAYMENT_URL}")
    server.serve_forever()


if __name__ == "__main__":
    main()
