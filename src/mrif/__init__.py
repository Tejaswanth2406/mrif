"""
Meta-Recursive Intelligence Framework (MRIF)

A production-grade recursive meta-intelligence operating system.

State:     M = (K, T, R, I, C, E, G)
Update:    M_{t+1} = F(M_t, O_t)
"""

from mrif.core.meta_core import MetaCore
from mrif.core.state import CoreState

__version__ = "0.1.0"
__all__ = ["MetaCore", "CoreState"]
