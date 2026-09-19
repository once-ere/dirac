#![forbid(unsafe_code)]
#![deny(warnings)]
#![allow(non_snake_case)]
#![allow(non_camel_case_types)]
#![allow(non_upper_case_globals)]

use std::any::Any;

use cvode_rs::prelude::*;

mod generated;

pub use generated::{
    LIE_DIMENSION, LIE_PAIRS, METRIC_DIAGONAL, MODULE_DIMENSION, PARA_TENSOR, REPRESENTATIONS,
    SPLIT_FIXTURE_SHA256, STATE_DIMENSION, TRIALITY_FIXTURE_SHA256,
};

pub type State = [f64; STATE_DIMENSION];

const ACTIVE_GENERATORS: [usize; 4] = [0, 9, 22, 16];
const DEFAULT_FINAL_TIME: f64 = 4.0;

#[derive(Clone, Copy, Debug)]
pub struct TransportParameters {
    pub rate_scale: f64,
}

#[derive(Clone, Copy, Debug)]
pub struct Config {
    pub final_time: f64,
    pub output_step: f64,
    pub relative_tolerance: f64,
    pub absolute_tolerance: f64,
    pub maximum_step: f64,
    pub rate_scale: f64,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            final_time: DEFAULT_FINAL_TIME,
            output_step: 0.1,
            relative_tolerance: 1.0e-11,
            absolute_tolerance: 1.0e-13,
            maximum_step: 0.02,
            rate_scale: 1.0,
        }
    }
}

#[derive(Clone, Copy, Debug)]
pub struct Invariants {
    pub vector_norm: f64,
    pub plus_norm: f64,
    pub minus_norm: f64,
    pub trilinear: f64,
}

#[derive(Clone, Debug)]
pub struct Sample {
    pub time: f64,
    pub state: State,
    pub invariants: Invariants,
}

#[derive(Clone, Copy, Debug, Default)]
pub struct SolverStats {
    pub steps: i64,
    pub rhs_evaluations: i64,
}

#[derive(Clone, Debug)]
pub struct RunResult {
    pub samples: Vec<Sample>,
    pub stats: SolverStats,
}

impl RunResult {
    pub fn maximum_invariant_drifts(&self) -> Invariants {
        let initial = self.samples[0].invariants;
        let mut maximum = Invariants {
            vector_norm: 0.0,
            plus_norm: 0.0,
            minus_norm: 0.0,
            trilinear: 0.0,
        };
        for sample in &self.samples {
            maximum.vector_norm = maximum
                .vector_norm
                .max((sample.invariants.vector_norm - initial.vector_norm).abs());
            maximum.plus_norm = maximum
                .plus_norm
                .max((sample.invariants.plus_norm - initial.plus_norm).abs());
            maximum.minus_norm = maximum
                .minus_norm
                .max((sample.invariants.minus_norm - initial.minus_norm).abs());
            maximum.trilinear = maximum
                .trilinear
                .max((sample.invariants.trilinear - initial.trilinear).abs());
        }
        maximum
    }
}

pub fn initial_state() -> State {
    let mut state = [0.0; STATE_DIMENSION];
    state[0] = 1.0;
    state[MODULE_DIMENSION] = 1.0;
    state[2 * MODULE_DIMENSION] = 1.0;
    state
}

pub fn path_coefficients(time: f64) -> [f64; 4] {
    [
        1.0 / 5.0,
        3.0 / 20.0 + time / 40.0,
        -1.0 / 10.0 + time / 50.0,
        time * (4.0 - time) / 80.0,
    ]
}

fn module(state: &State, module_index: usize) -> [f64; MODULE_DIMENSION] {
    let mut result = [0.0; MODULE_DIMENSION];
    let offset = module_index * MODULE_DIMENSION;
    result.copy_from_slice(&state[offset..offset + MODULE_DIMENSION]);
    result
}

fn split_norm(vector: &[f64; MODULE_DIMENSION]) -> f64 {
    vector
        .iter()
        .zip(METRIC_DIAGONAL)
        .map(|(value, metric)| metric * value * value)
        .sum()
}

pub fn triality_trilinear(
    plus: &[f64; MODULE_DIMENSION],
    minus: &[f64; MODULE_DIMENSION],
    vector: &[f64; MODULE_DIMENSION],
) -> f64 {
    let mut value = 0.0;
    for left in 0..MODULE_DIMENSION {
        for right in 0..MODULE_DIMENSION {
            for output in 0..MODULE_DIMENSION {
                value += plus[left]
                    * minus[right]
                    * PARA_TENSOR[left][right][output]
                    * METRIC_DIAGONAL[output]
                    * vector[output];
            }
        }
    }
    value
}

pub fn invariants(state: &State) -> Invariants {
    let vector = module(state, 0);
    let plus = module(state, 1);
    let minus = module(state, 2);
    Invariants {
        vector_norm: split_norm(&vector),
        plus_norm: split_norm(&plus),
        minus_norm: split_norm(&minus),
        trilinear: triality_trilinear(&plus, &minus, &vector),
    }
}

pub fn rhs_values(time: f64, state: &State, rate_scale: f64) -> State {
    let coefficients = path_coefficients(time);
    let mut derivative = [0.0; STATE_DIMENSION];
    for (module_index, representation) in REPRESENTATIONS.iter().enumerate() {
        let offset = module_index * MODULE_DIMENSION;
        for (coefficient_index, generator_index) in ACTIVE_GENERATORS.iter().enumerate() {
            let coefficient = rate_scale * coefficients[coefficient_index];
            for row in 0..MODULE_DIMENSION {
                for column in 0..MODULE_DIMENSION {
                    derivative[offset + row] += coefficient
                        * representation[*generator_index][row][column]
                        * state[offset + column];
                }
            }
        }
    }
    derivative
}

pub fn rhs(time: f64, y: &N_Vector, ydot: &N_Vector, user_data: &mut Option<Box<dyn Any>>) -> i32 {
    let parameters = match user_data
        .as_mut()
        .and_then(|value| value.downcast_mut::<TransportParameters>())
    {
        Some(parameters) => parameters,
        None => return -1,
    };
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
    let derivative = rhs_values(time, &state, parameters.rate_scale);
    let mut output = match N_VGetArrayPointer(ydot) {
        Some(output) => output,
        None => return -1,
    };
    output[..STATE_DIMENSION].copy_from_slice(&derivative);
    0
}

fn read_state(vector: &N_Vector) -> Result<State, String> {
    let data = N_VGetArrayPointer(vector)
        .ok_or_else(|| "N_VGetArrayPointer returned None for state".to_string())?;
    let mut state = [0.0; STATE_DIMENSION];
    state.copy_from_slice(&data[..STATE_DIMENSION]);
    Ok(state)
}

pub fn integrate(config: &Config) -> Result<RunResult, String> {
    if config.final_time <= 0.0
        || config.output_step <= 0.0
        || config.relative_tolerance <= 0.0
        || config.absolute_tolerance <= 0.0
        || config.maximum_step <= 0.0
    {
        return Err("all integration configuration values must be positive".to_string());
    }
    let output_count_float = config.final_time / config.output_step;
    let output_count = output_count_float.round() as usize;
    if (output_count as f64 - output_count_float).abs() > 1.0e-12 {
        return Err("final_time must be an integer multiple of output_step".to_string());
    }

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
    flag = CVodeSetUserData(
        &cvode,
        Some(Box::new(TransportParameters {
            rate_scale: config.rate_scale,
        })),
    );
    if flag != CV_SUCCESS {
        return Err(format!("CVodeSetUserData failed: {flag}"));
    }
    flag = CVodeSetMaxNumSteps(&cvode, 1_000_000);
    if flag != CV_SUCCESS {
        return Err(format!("CVodeSetMaxNumSteps failed: {flag}"));
    }
    flag = CVodeSetMaxStep(&cvode, config.maximum_step);
    if flag != CV_SUCCESS {
        return Err(format!("CVodeSetMaxStep failed: {flag}"));
    }
    flag = CVodeSetStopTime(&cvode, config.final_time);
    if flag != CV_SUCCESS {
        return Err(format!("CVodeSetStopTime failed: {flag}"));
    }

    let initial = initial_state();
    let mut samples = vec![Sample {
        time: 0.0,
        state: initial,
        invariants: invariants(&initial),
    }];
    let mut time = 0.0;
    for output_index in 1..=output_count {
        let output_time = if output_index == output_count {
            config.final_time
        } else {
            output_index as f64 * config.output_step
        };
        flag = CVode(&cvode, output_time, &state_vector, &mut time, CV_NORMAL);
        if flag < 0 {
            return Err(format!("CVode failed with flag {flag} at t={time}"));
        }
        let state = read_state(&state_vector)?;
        samples.push(Sample {
            time,
            state,
            invariants: invariants(&state),
        });
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

    Ok(RunResult { samples, stats })
}

#[cfg(test)]
mod tests {
    use super::*;

    fn directional_norm_derivative(state: &[f64; 8], derivative: &[f64; 8]) -> f64 {
        2.0 * state
            .iter()
            .zip(derivative)
            .zip(METRIC_DIAGONAL)
            .map(|((value, rate), metric)| metric * value * rate)
            .sum::<f64>()
    }

    #[test]
    fn initial_invariants_are_one() {
        let values = invariants(&initial_state());
        assert_eq!(values.vector_norm, 1.0);
        assert_eq!(values.plus_norm, 1.0);
        assert_eq!(values.minus_norm, 1.0);
        assert_eq!(values.trilinear, 1.0);
    }

    #[test]
    fn rhs_preserves_all_invariants_instantaneously() {
        let mut state = [0.0; STATE_DIMENSION];
        for (index, value) in state.iter_mut().enumerate() {
            *value = (index as f64 - 7.0) / 11.0;
        }
        let derivative = rhs_values(1.25, &state, 1.0);
        let vector = module(&state, 0);
        let plus = module(&state, 1);
        let minus = module(&state, 2);
        let vector_rate = module(&derivative, 0);
        let plus_rate = module(&derivative, 1);
        let minus_rate = module(&derivative, 2);
        assert!(directional_norm_derivative(&vector, &vector_rate).abs() < 1.0e-14);
        assert!(directional_norm_derivative(&plus, &plus_rate).abs() < 1.0e-14);
        assert!(directional_norm_derivative(&minus, &minus_rate).abs() < 1.0e-14);
        let trilinear_rate = triality_trilinear(&plus_rate, &minus, &vector)
            + triality_trilinear(&plus, &minus_rate, &vector)
            + triality_trilinear(&plus, &minus, &vector_rate);
        assert!(trilinear_rate.abs() < 1.0e-14);
    }

    #[test]
    fn cvode_smoke_run_preserves_invariants() {
        let config = Config {
            final_time: 0.2,
            output_step: 0.1,
            ..Config::default()
        };
        let result = integrate(&config).expect("CVODE smoke run failed");
        assert_eq!(result.samples.len(), 3);
        let drift = result.maximum_invariant_drifts();
        assert!(drift.vector_norm <= 1.0e-9);
        assert!(drift.plus_norm <= 1.0e-9);
        assert!(drift.minus_norm <= 1.0e-9);
        assert!(drift.trilinear <= 1.0e-9);
    }
}
