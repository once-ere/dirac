#![forbid(unsafe_code)]
#![deny(warnings)]

use std::env;
use std::fs;
use std::path::{Path, PathBuf};

use sundials_core::sundials_utils::fmt_e;
use weitzenbock_spinor_44::{
    boundary_identity_residual, boundary_term, dirac_equivalence_residual, hubble_derivative,
    levi_civita_ricci_scalar, solve, torsion_scalar, torsion_trace_time, Config, MaximumErrors,
    RunResult, CL44_FIXTURE_SHA256, CURVED_GEOMETRY_FIXTURE_SHA256, KAPPA_8, MASS_COEFFICIENT,
    OUTPUT_STEP, SELF_COEFFICIENT, SELF_EXPONENT, T_MAX, T_MIN,
    WEITZENBOCK_GEOMETRY_FIXTURE_SHA256,
};

const ERROR_LIMIT: f64 = 1.0e-8;

fn parse_positive(value: &str, flag: &str) -> Result<f64, String> {
    let parsed = value
        .parse::<f64>()
        .map_err(|error| format!("invalid value for {flag}: {error}"))?;
    if !parsed.is_finite() || parsed <= 0.0 {
        return Err(format!("{flag} must be finite and positive"));
    }
    Ok(parsed)
}

fn parse_options() -> Result<(PathBuf, Config), String> {
    let arguments: Vec<String> = env::args().skip(1).collect();
    let mut output_directory = PathBuf::from("artifacts/weitzenbock-spinor-44");
    let mut config = Config::default();
    let mut index = 0;
    while index < arguments.len() {
        let flag = &arguments[index];
        let value = arguments
            .get(index + 1)
            .ok_or_else(|| format!("missing value for {flag}"))?;
        match flag.as_str() {
            "--output" => output_directory = PathBuf::from(value),
            "--relative-tolerance" => {
                config.relative_tolerance = parse_positive(value, flag)?;
            }
            "--absolute-tolerance" => {
                config.absolute_tolerance = parse_positive(value, flag)?;
            }
            "--maximum-step" => {
                config.maximum_step = parse_positive(value, flag)?;
            }
            _ => {
                return Err(format!(
                    "unknown option {flag}; expected --output, \
                     --relative-tolerance, --absolute-tolerance, or \
                     --maximum-step"
                ));
            }
        }
        index += 2;
    }
    Ok((output_directory, config))
}

fn teleparallel_values(hubble: f64, density: f64, pressure: f64) -> [f64; 7] {
    let rate = hubble_derivative(density, pressure);
    [
        rate,
        torsion_trace_time(hubble),
        torsion_scalar(hubble),
        levi_civita_ricci_scalar(hubble, rate),
        boundary_term(hubble, rate),
        boundary_identity_residual(hubble, rate),
        dirac_equivalence_residual(hubble),
    ]
}

fn write_csv(directory: &Path, result: &RunResult) -> Result<(), String> {
    let mut headings = vec!["t".to_string(), "a".to_string(), "H".to_string()];
    headings.extend((0..16).map(|index| format!("psi{index}")));
    headings.extend(
        [
            "S",
            "rho",
            "pressure",
            "w",
            "dust_like_fraction",
            "negative_pressure_fraction",
            "acceleration",
            "Hdot",
            "torsion_trace_time",
            "torsion_scalar",
            "levi_civita_ricci_scalar",
            "boundary_term",
            "boundary_identity_residual",
            "dirac_equivalence_residual",
            "S_relative_error",
            "density_relative_error",
            "friedmann_relative_error",
        ]
        .into_iter()
        .map(str::to_string),
    );
    let mut lines = vec![headings.join(",")];
    for sample in &result.samples {
        let mut values = vec![sample.time, sample.state[0], sample.state[1]];
        values.extend_from_slice(&sample.state[2..]);
        values.extend([
            sample.condensate,
            sample.density,
            sample.pressure,
            sample.equation_of_state,
            sample.dust_like_fraction,
            sample.negative_pressure_fraction,
            sample.acceleration,
        ]);
        values.extend(teleparallel_values(
            sample.state[1],
            sample.density,
            sample.pressure,
        ));
        values.extend([
            sample.condensate_relative_error,
            sample.density_relative_error,
            sample.friedmann_relative_error,
        ]);
        lines.push(
            values
                .into_iter()
                .map(|value| fmt_e(value, 17))
                .collect::<Vec<_>>()
                .join(","),
        );
    }
    fs::write(directory.join("history.csv"), lines.join("\n") + "\n")
        .map_err(|error| format!("write history.csv failed: {error}"))
}

fn maximum_teleparallel_errors(result: &RunResult) -> (f64, f64) {
    result
        .samples
        .iter()
        .fold((0.0_f64, 0.0_f64), |maximum, sample| {
            let values = teleparallel_values(sample.state[1], sample.density, sample.pressure);
            (
                maximum.0.max(values[5].abs()),
                maximum.1.max(values[6].abs()),
            )
        })
}

fn write_summary(
    directory: &Path,
    config: &Config,
    result: &RunResult,
    errors: &MaximumErrors,
    teleparallel_errors: (f64, f64),
    passed: bool,
) -> Result<(), String> {
    let (transition_time, transition_scale) = result
        .acceleration_transition()
        .ok_or_else(|| "acceleration transition was not found".to_string())?;
    let present = result
        .samples
        .iter()
        .find(|sample| sample.time.abs() <= 1.0e-15)
        .ok_or_else(|| "present sample was not found".to_string())?;
    let final_sample = result
        .samples
        .last()
        .ok_or_else(|| "solution has no samples".to_string())?;
    let content = format!(
        concat!(
            "{{\n",
            "  \"schemaVersion\": 1,\n",
            "  \"study\": \"weitzenbock-spinor-44\",\n",
            "  \"connection\": \"flat inertial Spin(4,4) connection in diagonal Weitzenbock gauge\",\n",
            "  \"stateDimension\": 18,\n",
            "  \"baseDimension\": 8,\n",
            "  \"signature\": [4, 4],\n",
            "  \"cl44FixtureSha256\": \"{}\",\n",
            "  \"curvedGeometryFixtureSha256\": \"{}\",\n",
            "  \"weitzenbockGeometryFixtureSha256\": \"{}\",\n",
            "  \"parameters\": {{\n",
            "    \"kappa8\": {},\n",
            "    \"massCoefficient\": {},\n",
            "    \"selfCoefficient\": {},\n",
            "    \"selfExponent\": {}\n",
            "  }},\n",
            "  \"tMin\": {},\n",
            "  \"tMax\": {},\n",
            "  \"outputStep\": {},\n",
            "  \"relativeTolerance\": {},\n",
            "  \"absoluteTolerance\": {},\n",
            "  \"maximumStep\": {},\n",
            "  \"sampleCount\": {},\n",
            "  \"solverSteps\": {},\n",
            "  \"rhsEvaluations\": {},\n",
            "  \"accelerationTransitionTime\": {},\n",
            "  \"accelerationTransitionScaleFactor\": {},\n",
            "  \"maximumRelativeError\": {{\n",
            "    \"condensate\": {},\n",
            "    \"density\": {},\n",
            "    \"friedmann\": {},\n",
            "    \"teleparallelBoundaryIdentityAbsolute\": {},\n",
            "    \"homogeneousDiracEquivalenceAbsolute\": {}\n",
            "  }},\n",
            "  \"darkSectorDiagnostics\": {{\n",
            "    \"presentEquationOfState\": {},\n",
            "    \"presentDustLikeFraction\": {},\n",
            "    \"presentNegativePressureFraction\": {},\n",
            "    \"finalEquationOfState\": {},\n",
            "    \"finalDustLikeFraction\": {},\n",
            "    \"finalNegativePressureFraction\": {}\n",
            "  }},\n",
            "  \"interpretation\": {{\n",
            "    \"massTerm\": \"homogeneous dust-like effective fluid\",\n",
            "    \"selfInteraction\": \"homogeneous negative-pressure effective fluid\",\n",
            "    \"torsionSector\": \"TEGR rewriting of curvature, not an additional dark component\",\n",
            "    \"observationalClaim\": false\n",
            "  }},\n",
            "  \"verdict\": \"{}\"\n",
            "}}\n"
        ),
        CL44_FIXTURE_SHA256,
        CURVED_GEOMETRY_FIXTURE_SHA256,
        WEITZENBOCK_GEOMETRY_FIXTURE_SHA256,
        fmt_e(KAPPA_8, 17),
        fmt_e(MASS_COEFFICIENT, 17),
        fmt_e(SELF_COEFFICIENT, 17),
        fmt_e(SELF_EXPONENT, 17),
        fmt_e(T_MIN, 17),
        fmt_e(T_MAX, 17),
        fmt_e(OUTPUT_STEP, 17),
        fmt_e(config.relative_tolerance, 17),
        fmt_e(config.absolute_tolerance, 17),
        fmt_e(config.maximum_step, 17),
        result.samples.len(),
        result.stats.steps,
        result.stats.rhs_evaluations,
        fmt_e(transition_time, 17),
        fmt_e(transition_scale, 17),
        fmt_e(errors.condensate, 17),
        fmt_e(errors.density, 17),
        fmt_e(errors.friedmann, 17),
        fmt_e(teleparallel_errors.0, 17),
        fmt_e(teleparallel_errors.1, 17),
        fmt_e(present.equation_of_state, 17),
        fmt_e(present.dust_like_fraction, 17),
        fmt_e(present.negative_pressure_fraction, 17),
        fmt_e(final_sample.equation_of_state, 17),
        fmt_e(final_sample.dust_like_fraction, 17),
        fmt_e(final_sample.negative_pressure_fraction, 17),
        if passed { "SUCCESS" } else { "FAILURE" },
    );
    fs::write(directory.join("summary.json"), content)
        .map_err(|error| format!("write summary.json failed: {error}"))
}

fn check(name: &str, passed: bool, detail: &str) -> bool {
    println!(
        "{} - {name}: {detail}",
        if passed { "PASS" } else { "FAIL" }
    );
    passed
}

fn run() -> Result<bool, String> {
    let (output_directory, config) = parse_options()?;
    fs::create_dir_all(&output_directory)
        .map_err(|error| format!("create output directory failed: {error}"))?;
    let result = solve(&config)?;
    let errors = result.maximum_errors();
    let teleparallel_errors = maximum_teleparallel_errors(&result);
    let transition = result
        .acceleration_transition()
        .ok_or_else(|| "acceleration transition was not found".to_string())?;
    let maximum_torsion = result
        .samples
        .iter()
        .map(|sample| torsion_scalar(sample.state[1]).abs())
        .fold(0.0_f64, f64::max);
    let mut passed = true;
    passed &= check(
        "sample_count",
        result.samples.len() == 171,
        &format!("{} samples including both branches", result.samples.len()),
    );
    passed &= check(
        "canonical_reduction",
        errors.condensate <= ERROR_LIMIT
            && errors.density <= ERROR_LIMIT
            && errors.friedmann <= ERROR_LIMIT,
        "condensate, density, and TEGR Friedmann equations",
    );
    passed &= check(
        "flat_torsionful_connection",
        maximum_torsion > 0.0,
        &format!("maximum |T|={}", fmt_e(maximum_torsion, 6)),
    );
    passed &= check(
        "boundary_identity",
        teleparallel_errors.0 <= 1.0e-12,
        &format!("maximum residual {}", fmt_e(teleparallel_errors.0, 6)),
    );
    passed &= check(
        "dirac_equivalence",
        teleparallel_errors.1 == 0.0,
        &format!("maximum residual {}", fmt_e(teleparallel_errors.1, 6)),
    );
    passed &= check(
        "acceleration_transition",
        transition.1 > 0.8 && transition.1 < 0.9,
        &format!("t={} a={}", fmt_e(transition.0, 6), fmt_e(transition.1, 6)),
    );
    write_csv(&output_directory, &result)?;
    write_summary(
        &output_directory,
        &config,
        &result,
        &errors,
        teleparallel_errors,
        passed,
    )?;
    println!("solver_steps={}", result.stats.steps);
    println!("rhs_evaluations={}", result.stats.rhs_evaluations);
    println!("output={}", output_directory.display());
    println!("{}", if passed { "SUCCESS" } else { "FAILURE" });
    Ok(passed)
}

fn main() {
    match run() {
        Ok(true) => {}
        Ok(false) => std::process::exit(1),
        Err(error) => {
            eprintln!("ERROR: {error}");
            std::process::exit(1);
        }
    }
}
