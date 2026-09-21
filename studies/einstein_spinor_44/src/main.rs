#![forbid(unsafe_code)]
#![deny(warnings)]

use std::env;
use std::fs;
use std::path::{Path, PathBuf};

use einstein_spinor_44::{
    integrate, Config, MaximumErrors, RunResult, CL44_FIXTURE_SHA256, GEOMETRY_FIXTURE_SHA256,
    KAPPA_8, MASS_COEFFICIENT, OUTPUT_STEP, SELF_COEFFICIENT, SELF_EXPONENT, T_MAX, T_MIN,
};
use sundials_core::sundials_utils::fmt_e;

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
    let mut output_directory = PathBuf::from("artifacts/einstein-spinor-44");
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

fn write_summary(
    directory: &Path,
    config: &Config,
    result: &RunResult,
    errors: &MaximumErrors,
    passed: bool,
) -> Result<(), String> {
    let (transition_time, transition_scale) = result
        .acceleration_transition()
        .ok_or_else(|| "acceleration transition was not found".to_string())?;
    let content = format!(
        concat!(
            "{{\n",
            "  \"schemaVersion\": 1,\n",
            "  \"study\": \"einstein-spinor-44\",\n",
            "  \"stateDimension\": 18,\n",
            "  \"baseDimension\": 8,\n",
            "  \"signature\": [4, 4],\n",
            "  \"cl44FixtureSha256\": \"{}\",\n",
            "  \"geometryFixtureSha256\": \"{}\",\n",
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
            "    \"friedmann\": {}\n",
            "  }},\n",
            "  \"verdict\": \"{}\"\n",
            "}}\n"
        ),
        CL44_FIXTURE_SHA256,
        GEOMETRY_FIXTURE_SHA256,
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
    let result = integrate(&config)?;
    let errors = result.maximum_errors();
    let transition = result
        .acceleration_transition()
        .ok_or_else(|| "acceleration transition was not found".to_string())?;
    let mut passed = true;
    passed &= check(
        "sample_count",
        result.samples.len() == 171,
        &format!("{} samples including both branches", result.samples.len()),
    );
    passed &= check(
        "condensate_dilution",
        errors.condensate <= ERROR_LIMIT,
        &format!("maximum relative error {}", fmt_e(errors.condensate, 6)),
    );
    passed &= check(
        "density_reconstruction",
        errors.density <= ERROR_LIMIT,
        &format!("maximum relative error {}", fmt_e(errors.density, 6)),
    );
    passed &= check(
        "friedmann_constraint",
        errors.friedmann <= ERROR_LIMIT,
        &format!("maximum relative error {}", fmt_e(errors.friedmann, 6)),
    );
    passed &= check(
        "acceleration_transition",
        transition.1 > 0.8 && transition.1 < 0.9,
        &format!("t={} a={}", fmt_e(transition.0, 6), fmt_e(transition.1, 6)),
    );
    write_csv(&output_directory, &result)?;
    write_summary(&output_directory, &config, &result, &errors, passed)?;
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
