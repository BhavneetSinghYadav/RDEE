from __future__ import annotations

"""Validation adapter functions for the orchestration layer."""

from interface.parameter_schema import RDEEParameterSchema
from validation.constraints import validate_physical_constraints
from validation.sanity_checks import check_parameter_sanity
from validation.validator import validate_parameters


def validate_full_parameters(parameters: RDEEParameterSchema) -> bool:
    """Validate ``parameters`` using the full validation pipeline.

    This function sequentially applies physical constraint checks, sanity
    validations, and the aggregated pipeline validator. Any exception raised
    by these checks will propagate upward to the caller.

    Parameters
    ----------
    parameters:
        Instance of :class:`RDEEParameterSchema` to validate.

    Returns
    -------
    bool
        ``True`` if all validation stages pass.

    Raises
    ------
    validation.constraints.ValidationError
        If physical constraints are violated.
    validation.sanity_checks.SanityCheckError
        If sanity checks fail.
    validation.validator.ValidationPipelineError
        If the aggregated pipeline validation fails.
    """

    validate_physical_constraints(parameters)
    check_parameter_sanity(parameters)
    validate_parameters(parameters)

    return True
