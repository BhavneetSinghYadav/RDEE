from __future__ import annotations

"""Master parameter validation for RDEE."""

from dataclasses import dataclass
from typing import List

from interface.parameter_schema import RDEEParameterSchema
from validation.constraints import ValidationError, validate_physical_constraints
from validation.sanity_checks import SanityCheckError, check_parameter_sanity


@dataclass
class ValidationPipelineError(Exception):
    """Aggregated validation error for parameter pipeline."""

    errors: List[Exception]

    def __post_init__(self) -> None:
        message = "; ".join(str(err) for err in self.errors)
        super().__init__(message)


def validate_parameters(parameters: RDEEParameterSchema) -> bool:
    """Run full validation pipeline on ``parameters``.

    Parameters
    ----------
    parameters:
        The ``RDEEParameterSchema`` instance to validate.

    Returns
    -------
    bool
        ``True`` if all validations succeed.

    Raises
    ------
    ValidationPipelineError
        If any constraint or sanity check fails.
    """

    errors: List[Exception] = []

    try:
        validate_physical_constraints(parameters)
    except ValidationError as exc:
        errors.append(exc)

    try:
        check_parameter_sanity(parameters)
    except SanityCheckError as exc:
        errors.append(exc)

    if errors:
        raise ValidationPipelineError(errors)

    return True
