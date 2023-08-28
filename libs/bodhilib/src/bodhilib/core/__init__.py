"""Contains constants and common functions used by bodhilib."""
import inspect

#: str: current package name, used by plugin and logger to namespace operations
package_name = "bodhilib"

__all__ = [name for name, obj in globals().items() if not (name.startswith("_") or inspect.ismodule(obj))]