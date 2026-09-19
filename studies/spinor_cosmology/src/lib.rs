#![forbid(unsafe_code)]
#![deny(warnings)]
#![allow(non_snake_case)]
#![allow(non_camel_case_types)]
#![allow(non_upper_case_globals)]

use std::any::Any;

use cvode_rs::prelude::*;
use sundials_core::sundials_libm::{exp, log};

mod generated;

pub use generated::{CL44_FIXTURE_SHA256, INTERNAL_ROTATION, SPINOR_DIMENSION, STATE_DIMENSION};

pub const OMEGA_M0: f64 = 0.305;
pub const OMEGA_R0: f64 = 0.00009;
pub const OMEGA_PSI0: f64 = 0.69491;
pub const W0: f64 = -0.861;
pub const WA: f64 = -0.60;
pub const N_MIN: f64 = -4.0;
pub const N_MAX: f64 = 1.0;
pub const OUTPUT_STEP: f64 = 1.0 / 240.0;

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
            maximum_step: 0.02,
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
    pub e_fold: f64,
    pub state: State,
    pub scale_factor: f64,
    pub condensate: f64,
    pub potential: f64,
    pub equation_of_state: f64,
    pub hubble_ratio: f64,
    pub condensate_relative_error: f64,
    pub density_relative_error: f64,
    pub potential_relative_error: f64,
    pub friedmann_relative_error: f64,
}

#[derive(Clone, Debug)]
pub struct RunResult {
    pub samples: Vec<Sample>,
    pub stats: SolverStats,
}

#[derive(Clone, Copy, Debug)]
pub struct MaximumErrors {
    pub condensate: f64,
    pub density: f64,
    pub potential: f64,
    pub friedmann: f64,
}

impl RunResult {
    pub fn maximum_errors(&self) -> MaximumErrors {
        let mut result = MaximumErrors {
            condensate: 0.0,
            density: 0.0,
            potential: 0.0,
            friedmann: 0.0,
        };
        for sample in &self.samples {
            result.condensate = result.condensate.max(sample.condensate_relative_error);
            result.density = result.density.max(sample.density_relative_error);
            result.potential = result.potential.max(sample.potential_relative_error);
            result.friedmann = result.friedmann.max(sample.friedmann_relative_error);
        }
        result
    }
}

pub fn initial_state() -> State {
    let mut state = [0.0; STATE_DIMENSION];
    state[1] = OMEGA_PSI0;
    state[2] = 1.0;
    state
}

pub fn scale_factor(e_fold: f64) -> f64 {
    exp(e_fold)
}

pub fn equation_of_state(scale_factor: f64) -> f64 {
    W0 + WA * (1.0 - scale_factor)
}

pub fn analytic_condensate(e_fold: f64) -> f64 {
    exp(-3.0 * e_fold)
}

pub fn analytic_density(e_fold: f64) -> f64 {
    let scale = scale_factor(e_fold);
    let exponent = -3.0 * (1.0 + W0 + WA) * e_fold - 3.0 * WA * (1.0 - scale);
    OMEGA_PSI0 * exp(exponent)
}

pub fn potential(condensate: f64) -> f64 {
    let scale = exp(-log(condensate) / 3.0);
    let exponent = (1.0 + W0 + WA) * log(condensate) - 3.0 * WA * (1.0 - scale);
    OMEGA_PSI0 * exp(exponent)
}

pub fn potential_derivative(condensate: f64) -> f64 {
    let scale = exp(-log(condensate) / 3.0);
    potential(condensate) * (1.0 + W0 + WA - WA * scale) / condensate
}

pub fn condensate(state: &State) -> f64 {
    state[2..].iter().map(|value| value * value).sum()
}

pub fn hubble_squared(e_fold: f64, density: f64) -> f64 {
    OMEGA_R0 * exp(-4.0 * e_fold) + OMEGA_M0 * exp(-3.0 * e_fold) + density
}

pub fn rhs_values(e_fold: f64, state: &State) -> Result<State, String> {
    let density = state[1];
    let spinor_condensate = condensate(state);
    let hubble_squared_value = hubble_squared(e_fold, density);
    if density <= 0.0 || spinor_condensate <= 0.0 || hubble_squared_value <= 0.0 {
        return Err("nonpositive intermediate cosmology state".to_string());
    }
    let hubble_ratio = hubble_squared_value.sqrt();
    let scale = scale_factor(e_fold);
    let rotation_rate = potential_derivative(spinor_condensate) / hubble_ratio;
    let mut derivative = [0.0; STATE_DIMENSION];
    derivative[0] = 1.0 / hubble_ratio;
    derivative[1] = -3.0 * (1.0 + equation_of_state(scale)) * density;
    for row in 0..SPINOR_DIMENSION {
        derivative[2 + row] = -1.5 * state[2 + row];
        for column in 0..SPINOR_DIMENSION {
            derivative[2 + row] +=
                rotation_rate * INTERNAL_ROTATION[row][column] * state[2 + column];
        }
    }
    Ok(derivative)
}

pub fn rhs(
    e_fold: f64,
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
    let derivative = match rhs_values(e_fold, &state) {
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

fn sample(e_fold: f64, state: State) -> Sample {
    let scale = scale_factor(e_fold);
    let spinor_condensate = condensate(&state);
    let reconstructed_potential = potential(spinor_condensate);
    let expected_condensate = analytic_condensate(e_fold);
    let expected_density = analytic_density(e_fold);
    let numerical_hubble_squared = hubble_squared(e_fold, state[1]);
    let analytic_hubble_squared = hubble_squared(e_fold, expected_density);
    Sample {
        e_fold,
        state,
        scale_factor: scale,
        condensate: spinor_condensate,
        potential: reconstructed_potential,
        equation_of_state: equation_of_state(scale),
        hubble_ratio: numerical_hubble_squared.sqrt(),
        condensate_relative_error: relative_error(spinor_condensate, expected_condensate),
        density_relative_error: relative_error(state[1], expected_density),
        potential_relative_error: relative_error(state[1], reconstructed_potential),
        friedmann_relative_error: relative_error(numerical_hubble_squared, analytic_hubble_squared),
    }
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
    final_e_fold: f64,
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
    flag = CVodeSetStopTime(&cvode, final_e_fold);
    if flag != CV_SUCCESS {
        return Err(format!("CVodeSetStopTime failed: {flag}"));
    }

    let mut samples = vec![sample(0.0, initial_state())];
    let mut e_fold = 0.0;
    for output_index in 1..=output_count {
        let target = final_e_fold * output_index as f64 / output_count as f64;
        flag = CVode(&cvode, target, &state_vector, &mut e_fold, CV_NORMAL);
        if flag < 0 {
            return Err(format!("CVode failed with flag {flag} at N={e_fold}"));
        }
        let state = read_state(&state_vector)?;
        samples.push(sample(e_fold, state));
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

pub fn integrate(config: &Config) -> Result<RunResult, String> {
    if config.relative_tolerance <= 0.0
        || config.absolute_tolerance <= 0.0
        || config.maximum_step <= 0.0
    {
        return Err("all integration tolerances and limits must be positive".to_string());
    }
    let (mut backward, backward_stats) = integrate_branch(config, N_MIN, 960)?;
    let (forward, forward_stats) = integrate_branch(config, N_MAX, 240)?;
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

    #[test]
    fn rotation_is_real_skew_and_squares_to_minus_identity() {
        for (row, rotation_row) in INTERNAL_ROTATION.iter().enumerate() {
            for (column, value) in rotation_row.iter().enumerate() {
                assert_eq!(*value, -INTERNAL_ROTATION[column][row]);
                let square = rotation_row
                    .iter()
                    .zip(INTERNAL_ROTATION.iter())
                    .map(|(left, right_row)| left * right_row[column])
                    .sum::<f64>();
                assert_eq!(square, if row == column { -1.0 } else { 0.0 });
            }
        }
    }

    #[test]
    fn rhs_has_exact_condensate_and_density_derivatives() {
        let state = initial_state();
        let derivative = rhs_values(0.0, &state).expect("valid present state");
        let d_condensate = 2.0
            * state[2..]
                .iter()
                .zip(&derivative[2..])
                .map(|(value, rate)| value * rate)
                .sum::<f64>();
        assert!((d_condensate + 3.0).abs() < 1.0e-15);
        let expected_density_rate = -3.0 * (1.0 + W0) * OMEGA_PSI0;
        assert!((derivative[1] - expected_density_rate).abs() < 1.0e-15);
    }

    #[test]
    fn cvode_smoke_branches_match_analytic_background() {
        let config = Config::default();
        let (backward, _) = integrate_branch(&config, -0.05, 2).expect("backward branch");
        let (forward, _) = integrate_branch(&config, 0.05, 2).expect("forward branch");
        for sample in backward.iter().chain(&forward) {
            assert!(sample.condensate_relative_error <= 1.0e-8);
            assert!(sample.density_relative_error <= 1.0e-8);
            assert!(sample.potential_relative_error <= 1.0e-8);
            assert!(sample.friedmann_relative_error <= 1.0e-8);
        }
    }
}
