"""Chapter 04 — context managers.

Exposes the context-manager demos so tests can import and exercise them.
"""

from ch04_context_managers.example import ManagedConnection, aspan, span

__all__ = ["ManagedConnection", "aspan", "span"]
