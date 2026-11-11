"""Contratos versionados do CECyber AppSec Labs.

Este pacote define o manifesto declarativo ``AppSecLab`` (``labs.cecyber.io/v1alpha1``),
suas regras de validação estrutural e semântica e o cálculo de digest canônico.
Não contém lógica de runtime nem de laboratórios específicos.
"""

from cecyber_contracts.digest import canonical_manifest_digest
from cecyber_contracts.manifest import (
    API_VERSION,
    KIND,
    AppSecLab,
    Hint,
    LabStep,
    LabVariant,
)
from cecyber_contracts.profiles import DEFAULT_RUNTIME_PROFILES, RuntimeProfile
from cecyber_contracts.validation import (
    ManifestIssue,
    ManifestValidationError,
    load_manifest,
    validate_manifest,
)

__all__ = [
    "API_VERSION",
    "DEFAULT_RUNTIME_PROFILES",
    "KIND",
    "AppSecLab",
    "Hint",
    "LabStep",
    "LabVariant",
    "ManifestIssue",
    "ManifestValidationError",
    "RuntimeProfile",
    "canonical_manifest_digest",
    "load_manifest",
    "validate_manifest",
]
