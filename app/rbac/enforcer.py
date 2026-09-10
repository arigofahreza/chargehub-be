import os
import casbin
import casbin_sqlalchemy_adapter

from app.database import engine

_enforcer: casbin.Enforcer | None = None


def get_enforcer() -> casbin.Enforcer:
    global _enforcer
    if _enforcer is None:
        base = os.path.dirname(__file__)
        adapter = casbin_sqlalchemy_adapter.Adapter(engine)
        _enforcer = casbin.Enforcer(os.path.join(base, "model.conf"), adapter)
    return _enforcer
