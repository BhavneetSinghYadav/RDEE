from __future__ import annotations

"""Stage-wise evaluation handlers for RDEE recursion core."""

from interface.parameter_schema import RDEEParameterSchema
from simulation_engine.core.survival_filter import (
    threshold_pass,
    survival_window,
    probabilistic_survival,
    scaled_fragility,
)


def evaluate_cosmological(parameters: RDEEParameterSchema) -> bool:
    """Evaluate cosmological parameter survival conditions.

    Parameters
    ----------
    parameters:
        The :class:`RDEEParameterSchema` containing cosmological defaults.

    Returns
    -------
    bool
        ``True`` if cosmological constants fall within survival thresholds.
    """

    try:
        cosmology = parameters.cosmological
        hubble = cosmology.hubble_constant
        constant = cosmology.cosmological_constant
        baryon = cosmology.baryon_to_photon_ratio
    except AttributeError:
        return False

    if not threshold_pass(hubble.default, hubble.min_value, hubble.max_value):
        return False
    if not threshold_pass(constant.default, constant.min_value, constant.max_value):
        return False
    if not threshold_pass(baryon.default, baryon.min_value, baryon.max_value):
        return False
    return True


def evaluate_stellar(parameters: RDEEParameterSchema) -> bool:
    """Evaluate survival likelihood of the host star.

    Parameters
    ----------
    parameters:
        The :class:`RDEEParameterSchema` containing stellar defaults.

    Returns
    -------
    bool
        ``True`` if stellar parameters are within their thresholds.
    """

    try:
        stellar = parameters.stellar
        metallicity = stellar.stellar_metallicity
        mass = stellar.stellar_mass
    except AttributeError:
        return False

    if not threshold_pass(metallicity.default, metallicity.min_value, metallicity.max_value):
        return False
    if not threshold_pass(mass.default, mass.min_value, mass.max_value):
        return False
    return True


def evaluate_planetary(parameters: RDEEParameterSchema) -> bool:
    """Evaluate planetary formation survival conditions.

    Parameters
    ----------
    parameters:
        The :class:`RDEEParameterSchema` with planetary defaults.

    Returns
    -------
    bool
        ``True`` if planetary formation parameters survive thresholds.
    """

    try:
        planetary = parameters.planetary
        p_mass = planetary.planet_mass
        p_dist = planetary.planet_distance
        multiplicity = planetary.planetary_system_multiplicity
    except AttributeError:
        return False

    if not threshold_pass(p_mass.default, p_mass.min_value, p_mass.max_value):
        return False
    if not threshold_pass(p_dist.default, p_dist.min_value, p_dist.max_value):
        return False
    if not threshold_pass(multiplicity.default, multiplicity.min_value, multiplicity.max_value):
        return False
    return True


def evaluate_habitability(parameters: RDEEParameterSchema) -> bool:
    """Evaluate basic planetary habitability.

    Parameters
    ----------
    parameters:
        The :class:`RDEEParameterSchema` containing habitability defaults.

    Returns
    -------
    bool
        ``True`` if habitability conditions are satisfied.
    """

    try:
        habitability = parameters.habitability
        planetary = parameters.planetary
        tidal_prob = habitability.tidal_locking_probability
        zone = habitability.liquid_water_zone_range
        planet_distance = planetary.planet_distance
    except AttributeError:
        return False

    if not threshold_pass(tidal_prob.default, tidal_prob.min_value, tidal_prob.max_value):
        return False

    if zone.default is not None and planet_distance.default is not None:
        window_ratio = (
            parameters.sampling.survival_corridor_sensitivity_window.default
            if parameters.sampling.survival_corridor_sensitivity_window.default
            is not None
            else 0.1
        )
        ok = survival_window(
            planet_distance.default,
            zone.default,
            window_ratio,
        )
        if not ok:
            return False

    return True


def evaluate_prebiotic(parameters: RDEEParameterSchema) -> bool:
    """Evaluate viability of prebiotic chemistry.

    Parameters
    ----------
    parameters:
        The :class:`RDEEParameterSchema` with prebiotic chemistry defaults.

    Returns
    -------
    bool
        ``True`` if prebiotic conditions allow survival.
    """

    try:
        chem = parameters.prebiotic
        synth = chem.prebiotic_synthesis_success_probability
        uv_eff = chem.uv_catalysis_efficiency
        polymer_fail = chem.polymerization_failure_rate
    except AttributeError:
        return False

    if not probabilistic_survival(synth.default):
        return False
    if not probabilistic_survival(uv_eff.default):
        return False
    if polymer_fail.default is not None:
        if not probabilistic_survival(1.0 - polymer_fail.default):
            return False

    return True


def evaluate_evolutionary(parameters: RDEEParameterSchema) -> bool:
    """Evaluate evolutionary stage survival conditions.

    Parameters
    ----------
    parameters:
        The :class:`RDEEParameterSchema` with evolutionary defaults.

    Returns
    -------
    bool
        ``True`` if evolutionary parameters permit survival.
    """

    try:
        evo = parameters.evolutionary
        complexity = evo.evolutionary_complexity_threshold
        fragility = evo.evolutionary_fragility_multiplier
        extinction = evo.mass_extinction_frequency
    except AttributeError:
        return False

    if not threshold_pass(complexity.default, complexity.min_value, complexity.max_value):
        return False

    if not scaled_fragility(fragility.default):
        return False

    if extinction.default is not None:
        if not probabilistic_survival(extinction.default):
            return False

    return True
