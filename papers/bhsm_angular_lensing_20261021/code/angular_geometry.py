"""Normalized n=2 scalar harmonics on S^3 and their optical screen Hessian.

This module contains geometry, not a physical initial-state selection.  The
four-dimensional embedding coordinate X has unit norm; the sphere radius R
enters the physical volume and derivatives.  The nine matrices have
Tr(A_i A_j)=delta_ij, so N=sqrt(6)/(pi R**1.5) gives unit L2 harmonics.
"""
from __future__ import annotations

import numpy as np


def harmonic_basis():
    matrices = []
    names = []
    matrices.append(np.diag([3., -1., -1., -1.]) / np.sqrt(6.))
    names.append("monopole")
    for j, axis in enumerate("xyz", 1):
        a = np.zeros((4, 4)); a[0, j] = a[j, 0] = 1.
        matrices.append(a); names.append("dipole_" + axis)
    a = np.zeros((4, 4)); a[1:, 1:] = np.diag([1., -1., 0.])
    matrices.append(a); names.append("quadrupole_xx_yy")
    a = np.zeros((4, 4)); a[1:, 1:] = np.diag([1., 1., -2.]) / np.sqrt(3.)
    matrices.append(a); names.append("quadrupole_zz")
    for i, j, label in [(1, 2, "xy"), (1, 3, "xz"), (2, 3, "yz")]:
        a = np.zeros((4, 4)); a[i, j] = a[j, i] = 1.
        matrices.append(a); names.append("quadrupole_" + label)
    return names, np.asarray(matrices) / np.sqrt(2.)


def normalization(radius):
    return np.sqrt(6.) / (np.pi * radius ** 1.5)


def embedding(u, direction):
    n = np.asarray(direction, dtype=float)
    n = n / np.linalg.norm(n)
    return np.concatenate(([np.cos(u)], np.sin(u) * n))


def screen(direction):
    n = np.asarray(direction, dtype=float)
    n = n / np.linalg.norm(n)
    trial = np.eye(3)[np.argmin(np.abs(n))]
    e1 = trial - np.dot(trial, n) * n
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(n, e1)
    return np.column_stack((e1, e2))


def harmonic(a, x, radius):
    return normalization(radius) * np.einsum("...i,ij,...j->...", x, a, x)


def screen_hessian_tf(a, direction, radius):
    e = screen(direction)
    block = e.T @ np.asarray(a)[1:, 1:] @ e
    return 2. * normalization(radius) / radius**2 * (
        block - .5 * np.trace(block) * np.eye(2))


def quadrupole_pattern(c, direction, screen_basis=None):
    """Dimensionless H_C, for symmetric tracefree C with Tr(C^2)=1."""
    n = np.asarray(direction, dtype=float)
    n /= np.linalg.norm(n)
    e = screen(n) if screen_basis is None else np.asarray(screen_basis)
    c = np.asarray(c, dtype=float)
    return 2. * e.T @ c @ e + (n @ c @ n) * np.eye(2)

