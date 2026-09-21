#![forbid(unsafe_code)]
#![deny(warnings)]

use std::any::Any;

use cvode_rs::prelude::*;
use sundials_core::sundials_libm::{exp, log};

mod generated;

pub use generated::{
    CL44_FIXTURE_SHA256, CURVED_GEOMETRY_FIXTURE_SHA256, SPINOR_BILINEAR, SPINOR_DIMENSION,
    STATE_DIMENSION, TIME_GAMMA, WEITZENBOCK_GEOMETRY_FIXTURE_SHA256,
};

pub const TRANSVERSE_DIMENSION: f64 = 7.0;
pub const KAPPA_8: f64 = 21.0;
pub const MASS_COEFFICIENT: f64 = 1.0 / 20.0;
pub const SELF_COEFFICIENT: f64 = 19.0 / 20.0;
pub const SELF_EXPONENT: f64 = 1.0 / 5.0;
pub const T_MIN: f64 = -0.2;
pub const T_MAX: f64 = 1.5;
pub const OUTPUT_STEP: f64 = 0.01;
pub const TORSION_SCALAR_COEFFICIENT: f64 = TRANSVERSE_DIMENSION * (TRANSVERSE_DIMENSION - 1.0);
pub const RICCI_HUBBLE_DERIVATIVE_COEFFICIENT: f64 = 2.0 * TRANSVERSE_DIMENSION;
pub const RICCI_HUBBLE_SQUARED_COEFFICIENT: f64 =
    TRANSVERSE_DIMENSION * (TRANSVERSE_DIMENSION + 1.0);
pub const BOUNDARY_HUBBLE_DERIVATIVE_COEFFICIENT: f64 = 2.0 * TRANSVERSE_DIMENSION;
pub const BOUNDARY_HUBBLE_SQUARED_COEFFICIENT: f64 =
    2.0 * TRANSVERSE_DIMENSION * TRANSVERSE_DIMENSION;

pub type State = [f64; STATE_DIMENSION];

#[derive(Clone, Copy, Debug)]
pub struct Config {
    pub relative_tolerance: f64,
    pub absolute_tolerance: f64,
    pub maximum_step: f64,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            relative_tolerance: 1.0e-11,
            absolute_tolerance: 1.0e-13,
            maximum_step: 0.002,
        }
    }
}

#[derive(Clone, Copy, Debug, Default)]
pub struct SolverStats {
    pub steps: i64,
    pub rhs_evaluations: i64,
}

#[derive(Clone, Debug)]
pub struct Sample {
    pub time: f64,
    pub state: State,
    pub condensate: f64,
    pub density: f64,
    pub pressure: f64,
    pub equation_of_state: f64,
    pub dust_like_fraction: f64,
    pub negative_pressure_fraction: f64,
    pub acceleration: f64,
    pub condensate_relative_error: f64,
    pub density_relative_error: f64,
    pub friedmann_relative_error: f64,
}

#[derive(Clone, Copy, Debug, Default)]
pub struct MaximumErrors {
    pub condensate: f64,
    pub density: f64,
    pub friedmann: f64,
}

#[derive(Clone, Debug)]
pub struct RunResult {
    pub samples: Vec<Sample>,
    pub stats: SolverStats,
}

impl RunResult {
    pub fn maximum_errors(&self) -> MaximumErrors {
        let mut result = MaximumErrors::default();
        for sample in &self.samples {
            result.condensate = result.condensate.max(sample.condensate_relative_error);
            result.density = result.density.max(sample.density_relative_error);
            result.friedmann = result.friedmann.max(sample.friedmann_relative_error);
        }
        result
    }

    pub fn acceleration_transition(&self) -> Option<(f64, f64)> {
        let transition_scale = acceleration_transition_scale_factor();
        self.samples.windows(2).find_map(|pair| {
            let left = &pair[0];
            let right = &pair[1];
            if left.state[0] <= transition_scale && right.state[0] >= transition_scale {
                let fraction =
                    (transition_scale - left.state[0]) / (right.state[0] - left.state[0]);
                Some((
                    left.time + fraction * (right.time - left.time),
                    transition_scale,
                ))
            } else {
                None
            }
        })
    }
}

pub fn hubble_derivative(density: f64, pressure: f64) -> f64 {
    -KAPPA_8 / (TRANSVERSE_DIMENSION - 1.0) * (density + pressure)
}

pub fn torsion_trace_time(hubble: f64) -> f64 {
    TRANSVERSE_DIMENSION * hubble
}

pub fn torsion_scalar(hubble: f64) -> f64 {
    TORSION_SCALAR_COEFFICIENT * hubble * hubble
}

pub fn levi_civita_ricci_scalar(hubble: f64, hubble_rate: f64) -> f64 {
    RICCI_HUBBLE_DERIVATIVE_COEFFICIENT * hubble_rate
        + RICCI_HUBBLE_SQUARED_COEFFICIENT * hubble * hubble
}

pub fn boundary_term(hubble: f64, hubble_rate: f64) -> f64 {
    BOUNDARY_HUBBLE_DERIVATIVE_COEFFICIENT * hubble_rate
        + BOUNDARY_HUBBLE_SQUARED_COEFFICIENT * hubble * hubble
}

pub fn boundary_identity_residual(hubble: f64, hubble_rate: f64) -> f64 {
    levi_civita_ricci_scalar(hubble, hubble_rate) + torsion_scalar(hubble)
        - boundary_term(hubble, hubble_rate)
}

pub fn weitzenbock_dirac_trace_coefficient(hubble: f64) -> f64 {
    torsion_trace_time(hubble) / 2.0
}

pub fn levi_civita_dirac_connection_coefficient(hubble: f64) -> f64 {
    TRANSVERSE_DIMENSION * hubble / 2.0
}

pub fn dirac_equivalence_residual(hubble: f64) -> f64 {
    weitzenbock_dirac_trace_coefficient(hubble) - levi_civita_dirac_connection_coefficient(hubble)
}

pub fn acceleration_transition_scale_factor() -> f64 {
    let numerator = 5.0 * MASS_COEFFICIENT;
    let denominator = (2.0 - TRANSVERSE_DIMENSION * SELF_EXPONENT) * SELF_COEFFICIENT;
    exp(log(numerator / denominator) / (TRANSVERSE_DIMENSION * (1.0 - SELF_EXPONENT)))
}

pub fn initial_state() -> State {
    let mut state = [0.0; STATE_DIMENSION];
    state[0] = 1.0;
    state[1] = 1.0;
    state[2] = 1.0;
    state[17] = 0.5;
    state
}

pub fn spinor_bilinear(spinor: &[f64; SPINOR_DIMENSION]) -> f64 {
    let mut value = 0.0;
    for row in 0..SPINOR_DIMENSION {
        for column in 0..SPINOR_DIMENSION {
            value += spinor[row] * SPINOR_BILINEAR[row][column] * spinor[column];
        }
    }
    value
}

fn spinor(state: &State) -> [f64; SPINOR_DIMENSION] {
    let mut result = [0.0; SPINOR_DIMENSION];
    result.copy_from_slice(&state[2..]);
    result
}

pub fn self_interaction(condensate: f64) -> f64 {
    SELF_COEFFICIENT * exp(SELF_EXPONENT * log(condensate))
}

pub fn potential(condensate: f64) -> f64 {
    MASS_COEFFICIENT * condensate + self_interaction(condensate)
}

pub fn potential_derivative(condensate: f64) -> f64 {
    MASS_COEFFICIENT
        + SELF_COEFFICIENT * SELF_EXPONENT * exp((SELF_EXPONENT - 1.0) * log(condensate))
}

pub fn pressure(condensate: f64) -> f64 {
    (SELF_EXPONENT - 1.0) * self_interaction(condensate)
}

pub fn expected_condensate(scale_factor: f64) -> f64 {
    exp(-TRANSVERSE_DIMENSION * log(scale_factor))
}

pub fn expected_density(scale_factor: f64) -> f64 {
    potential(expected_condensate(scale_factor))
}

pub fn rhs_values(state: &State) -> Result<State, String> {
    let scale_factor = state[0];
    let hubble = state[1];
    let psi = spinor(state);
    let condensate = spinor_bilinear(&psi);
    if scale_factor <= 0.0 || condensate <= 0.0 {
        return Err("nonpositive scale factor or invariant condensate".to_string());
    }
    let density = potential(condensate);
    let isotropic_pressure = pressure(condensate);
    let potential_rate = potential_derivative(condensate);
    let trace = torsion_trace_time(hubble);
    let mut derivative = [0.0; STATE_DIMENSION];
    derivative[0] = scale_factor * hubble;
    derivative[1] = hubble_derivative(density, isotropic_pressure);
    for row in 0..SPINOR_DIMENSION {
        derivative[2 + row] = -0.5 * trace * psi[row];
        for column in 0..SPINOR_DIMENSION {
            derivative[2 + row] -= potential_rate * TIME_GAMMA[row][column] * psi[column];
        }
    }
    Ok(derivative)
}

pub fn rhs(
    _time: f64,
    y: &N_Vector,
    ydot: &N_Vector,
    _user_data: &mut Option<Box<dyn Any>>,
) -> i32 {
    let state = {
        let data = match N_VGetArrayPointer(y) {
            Some(data) => data,
            None => return -1,
        };
        let mut state = [0.0; STATE_DIMENSION];
        state.copy_from_slice(&data[..STATE_DIMENSION]);
        state
    };
    if state.iter().any(|value| !value.is_finite()) {
        return 1;
    }
    let derivative = match rhs_values(&state) {
        Ok(derivative) => derivative,
        Err(_) => return 1,
    };
    let mut output = match N_VGetArrayPointer(ydot) {
        Some(output) => output,
        None => return -1,
    };
    output[..STATE_DIMENSION].copy_from_slice(&derivative);
    0
}

fn relative_error(actual: f64, expected: f64) -> f64 {
    (actual - expected).abs() / expected.abs().max(1.0e-300)
}

fn sample(time: f64, state: State) -> Result<Sample, String> {
    let scale_factor = state[0];
    let hubble = state[1];
    let psi = spinor(&state);
    let condensate = spinor_bilinear(&psi);
    if scale_factor <= 0.0 || condensate <= 0.0 {
        return Err("cannot sample nonpositive geometry state".to_string());
    }
    let density = potential(condensate);
    let isotropic_pressure = pressure(condensate);
    let expected_s = expected_condensate(scale_factor);
    let expected_rho = expected_density(scale_factor);
    let rate = hubble_derivative(density, isotropic_pressure);
    let acceleration = hubble * hubble + rate;
    let matter_density = MASS_COEFFICIENT * condensate;
    let interaction_density = self_interaction(condensate);
    Ok(Sample {
        time,
        state,
        condensate,
        density,
        pressure: isotropic_pressure,
        equation_of_state: isotropic_pressure / density,
        dust_like_fraction: matter_density / density,
        negative_pressure_fraction: interaction_density / density,
        acceleration,
        condensate_relative_error: relative_error(condensate, expected_s),
        density_relative_error: relative_error(density, expected_rho),
        friedmann_relative_error: relative_error(hubble * hubble, density),
    })
}

fn read_state(vector: &N_Vector) -> Result<State, String> {
    let data = N_VGetArrayPointer(vector)
        .ok_or_else(|| "N_VGetArrayPointer returned None for state".to_string())?;
    let mut state = [0.0; STATE_DIMENSION];
    state.copy_from_slice(&data[..STATE_DIMENSION]);
    Ok(state)
}

fn integrate_branch(
    config: &Config,
    final_time: f64,
    output_count: usize,
) -> Result<(Vec<Sample>, SolverStats), String> {
    let mut context_output: Option<SUNContext> = None;
    let mut flag = SUNContext_Create(SUN_COMM_NULL, &mut context_output);
    if flag != 0 {
        return Err(format!("SUNContext_Create failed: {flag}"));
    }
    let context =
        context_output.ok_or_else(|| "SUNContext_Create returned no context".to_string())?;
    let state_vector = N_VNew_Serial(STATE_DIMENSION as i64, &context)
        .ok_or_else(|| "N_VNew_Serial(state) returned None".to_string())?;
    N_VGetArrayPointer(&state_vector)
        .ok_or_else(|| "N_VGetArrayPointer returned None for state".to_string())?
        .copy_from_slice(&initial_state());
    let absolute_tolerance = N_VNew_Serial(STATE_DIMENSION as i64, &context)
        .ok_or_else(|| "N_VNew_Serial(abstol) returned None".to_string())?;
    N_VGetArrayPointer(&absolute_tolerance)
        .ok_or_else(|| "N_VGetArrayPointer returned None for abstol".to_string())?
        .fill(config.absolute_tolerance);

    let cvode = CVodeCreate(CV_BDF, &context)
        .ok_or_else(|| "CVodeCreate(CV_BDF) returned None".to_string())?;
    flag = CVodeInit(&cvode, rhs, 0.0, &state_vector);
    if flag != CV_SUCCESS {
        return Err(format!("CVodeInit failed: {flag}"));
    }
    flag = CVodeSVtolerances(&cvode, config.relative_tolerance, &absolute_tolerance);
    if flag != CV_SUCCESS {
        return Err(format!("CVodeSVtolerances failed: {flag}"));
    }
    let matrix = SUNDenseMatrix(STATE_DIMENSION as i64, STATE_DIMENSION as i64, &context)
        .ok_or_else(|| "SUNDenseMatrix returned None".to_string())?;
    let linear_solver = SUNLinSol_Dense(&state_vector, &matrix, &context)
        .ok_or_else(|| "SUNLinSol_Dense returned None".to_string())?;
    flag = CVodeSetLinearSolver(&cvode, &linear_solver, Some(&matrix));
    if flag != CV_SUCCESS {
        return Err(format!("CVodeSetLinearSolver failed: {flag}"));
    }
    flag = CVodeSetMaxNumSteps(&cvode, 1_000_000);
    if flag != CV_SUCCESS {
        return Err(format!("CVodeSetMaxNumSteps failed: {flag}"));
    }
    flag = CVodeSetMaxStep(&cvode, config.maximum_step);
    if flag != CV_SUCCESS {
        return Err(format!("CVodeSetMaxStep failed: {flag}"));
    }
    flag = CVodeSetStopTime(&cvode, final_time);
    if flag != CV_SUCCESS {
        return Err(format!("CVodeSetStopTime failed: {flag}"));
    }

    let mut samples = vec![sample(0.0, initial_state())?];
    let mut time = 0.0;
    for output_index in 1..=output_count {
        let target = final_time * output_index as f64 / output_count as f64;
        flag = CVode(&cvode, target, &state_vector, &mut time, CV_NORMAL);
        if flag < 0 {
            return Err(format!("CVode failed with flag {flag} at t={time}"));
        }
        samples.push(sample(time, read_state(&state_vector)?)?);
    }

    let mut stats = SolverStats::default();
    flag = CVodeGetNumSteps(&cvode, &mut stats.steps);
    if flag != CV_SUCCESS {
        return Err(format!("CVodeGetNumSteps failed: {flag}"));
    }
    flag = CVodeGetNumRhsEvals(&cvode, &mut stats.rhs_evaluations);
    if flag != CV_SUCCESS {
        return Err(format!("CVodeGetNumRhsEvals failed: {flag}"));
    }

    let mut cvode_output = Some(cvode);
    CVodeFree(&mut cvode_output);
    let _ = SUNLinSolFree(Some(linear_solver));
    SUNMatDestroy(matrix);
    N_VDestroy(state_vector);
    N_VDestroy(absolute_tolerance);
    let mut context_output = Some(context);
    let _ = SUNContext_Free(&mut context_output);
    Ok((samples, stats))
}

pub fn solve(config: &Config) -> Result<RunResult, String> {
    if config.relative_tolerance <= 0.0
        || config.absolute_tolerance <= 0.0
        || config.maximum_step <= 0.0
    {
        return Err("all integration tolerances and limits must be positive".to_string());
    }
    let backward_count = ((-T_MIN / OUTPUT_STEP).round()) as usize;
    let forward_count = ((T_MAX / OUTPUT_STEP).round()) as usize;
    let (mut backward, backward_stats) = integrate_branch(config, T_MIN, backward_count)?;
    let (forward, forward_stats) = integrate_branch(config, T_MAX, forward_count)?;
    backward.reverse();
    backward.extend(forward.into_iter().skip(1));
    Ok(RunResult {
        samples: backward,
        stats: SolverStats {
            steps: backward_stats.steps + forward_stats.steps,
            rhs_evaluations: backward_stats.rhs_evaluations + forward_stats.rhs_evaluations,
        },
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    fn condensate_derivative(state: &State, derivative: &State) -> f64 {
        let psi = spinor(state);
        2.0 * psi
            .iter()
            .enumerate()
            .map(|(row, value)| {
                let conjugate_rate = (0..SPINOR_DIMENSION)
                    .map(|column| SPINOR_BILINEAR[row][column] * derivative[2 + column])
                    .sum::<f64>();
                value * conjugate_rate
            })
            .sum::<f64>()
    }

    #[test]
    fn invariant_matrices_have_required_adjoint_properties() {
        for row in 0..SPINOR_DIMENSION {
            for column in 0..SPINOR_DIMENSION {
                assert_eq!(SPINOR_BILINEAR[row][column], SPINOR_BILINEAR[column][row]);
                let charge_square = (0..SPINOR_DIMENSION)
                    .map(|inner| SPINOR_BILINEAR[row][inner] * SPINOR_BILINEAR[inner][column])
                    .sum::<f64>();
                assert_eq!(charge_square, if row == column { 1.0 } else { 0.0 });
                let gamma_square = (0..SPINOR_DIMENSION)
                    .map(|inner| TIME_GAMMA[row][inner] * TIME_GAMMA[inner][column])
                    .sum::<f64>();
                assert_eq!(gamma_square, if row == column { -1.0 } else { 0.0 });
                let adjoint = (0..SPINOR_DIMENSION)
                    .map(|inner| {
                        TIME_GAMMA[inner][row] * SPINOR_BILINEAR[inner][column]
                            + SPINOR_BILINEAR[row][inner] * TIME_GAMMA[inner][column]
                    })
                    .sum::<f64>();
                assert_eq!(adjoint, 0.0);
            }
        }
    }

    #[test]
    fn present_rhs_comes_from_torsion_trace_equation() {
        let state = initial_state();
        let derivative = rhs_values(&state).expect("valid present state");
        let psi = spinor(&state);
        let condensate = spinor_bilinear(&psi);
        assert!((condensate - 1.0).abs() < 1.0e-15);
        assert!((potential(condensate) - 1.0).abs() < 1.0e-15);
        assert!((pressure(condensate) + 0.76).abs() < 1.0e-15);
        assert!((derivative[1] + 0.84).abs() < 1.0e-15);
        assert!((condensate_derivative(&state, &derivative) + 7.0).abs() < 1.0e-14);
    }

    #[test]
    fn rejects_nonpositive_geometry_or_condensate() {
        let mut zero_scale = initial_state();
        zero_scale[0] = 0.0;
        assert!(rhs_values(&zero_scale).is_err());

        let mut zero_condensate = initial_state();
        zero_condensate[2..].fill(0.0);
        assert!(rhs_values(&zero_condensate).is_err());

        let mut negative_condensate = initial_state();
        negative_condensate[17] = -0.5;
        assert!(spinor_bilinear(&spinor(&negative_condensate)) < 0.0);
        assert!(rhs_values(&negative_condensate).is_err());
    }

    #[test]
    fn teleparallel_boundary_identity_is_exact_in_reduction() {
        for (hubble, hubble_rate) in [(0.0, 0.0), (1.0, -0.84), (-0.25, 0.125)] {
            assert!(boundary_identity_residual(hubble, hubble_rate).abs() < 1.0e-13);
        }
    }

    #[test]
    fn torsion_trace_replaces_homogeneous_spin_connection() {
        for hubble in [-2.0, 0.0, 0.75, 1.0] {
            assert_eq!(dirac_equivalence_residual(hubble), 0.0);
        }
    }

    #[test]
    fn zero_expansion_has_zero_teleparallel_invariants() {
        assert_eq!(torsion_trace_time(0.0), 0.0);
        assert_eq!(torsion_scalar(0.0), 0.0);
        assert_eq!(boundary_term(0.0, 0.0), 0.0);
    }

    #[test]
    fn cvode_solution_satisfies_teleparallel_reduction() {
        let result = solve(&Config::default()).expect("CVODE integration");
        assert_eq!(result.samples.len(), 171);
        let errors = result.maximum_errors();
        assert!(errors.condensate < 1.0e-7);
        assert!(errors.density < 1.0e-7);
        assert!(errors.friedmann < 1.0e-7);
        assert!(result
            .samples
            .iter()
            .all(|sample| dirac_equivalence_residual(sample.state[1]) == 0.0));
        assert!(result.samples.iter().all(|sample| {
            let rate = hubble_derivative(sample.density, sample.pressure);
            boundary_identity_residual(sample.state[1], rate).abs() < 1.0e-13
        }));
    }
}
