try:
    from .production import *
except ImportError as e_prod:
    try:
        from .dev import *
    except ImportError as e_dev:
        raise ImportError(
            "Neither 'production.py' nor 'dev.py' could be imported. "
            "Make sure you have copied and renamed the example configuration files correctly."
        ) from e_dev
