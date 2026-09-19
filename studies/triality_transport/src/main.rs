#![forbid(unsafe_code)]
#![deny(warnings)]

use std::env;
use std::fs;
use std::path::{Path, PathBuf};

use sundials_core::sundials_utils::fmt_e;
use triality_transport::{
    integrate, Config, Invariants, RunResult, SPLIT_FIXTURE_SHA256, TRIALITY_FIXTURE_SHA256,
};

const DRIFT_LIMIT: f64 = 1.0e-8;

fn parse_output_directory() -> Result<PathBuf, String> {
    let arguments: Vec<String> = env::args().skip(1).collect();
    match arguments.as_slice() {
        [] => Ok(PathBuf::from("artifacts/triality-transport")),
        [flag, path] if flag == "--output" => Ok(PathBuf::from(path)),
        _ => Err("usage: triality_transport [--output DIRECTORY]".to_string()),
    }
}

fn write_csv(directory: &Path, result: &RunResult) -> Result<(), String> {
    let mut lines = Vec::with_capacity(result.samples.len() + 1);
    let state_headings = (0..24).map(|index| format!("y{index}"));
    lines.push(
        std::iter::once("t".to_string())
            .chain(state_headings)
            .chain(
                ["norm_v", "norm_plus", "norm_minus", "trilinear"]
                    .into_iter()
                    .map(str::to_string),
            )
            .collect::<Vec<_>>()
            .join(","),
    );
    for sample in &result.samples {
        let mut values = Vec::with_capacity(29);
        values.push(sample.time);
        values.extend(sample.state);
        values.push(sample.invariants.vector_norm);
        values.push(sample.invariants.plus_norm);
        values.push(sample.invariants.minus_norm);
        values.push(sample.invariants.trilinear);
        lines.push(
            values
                .into_iter()
                .map(|value| fmt_e(value, 17))
                .collect::<Vec<_>>()
                .join(","),
        );
    }
    fs::write(directory.join("trajectory.csv"), lines.join("\n") + "\n")
        .map_err(|error| format!("write trajectory.csv failed: {error}"))
}

fn write_summary(
    directory: &Path,
    config: &Config,
    result: &RunResult,
    drift: &Invariants,
    passed: bool,
) -> Result<(), String> {
    let content = format!(
        concat!(
            "{{\n",
            "  \"schemaVersion\": 1,\n",
            "  \"study\": \"triality-transport\",\n",
            "  \"stateDimension\": 24,\n",
            "  \"trialityFixtureSha256\": \"{}\",\n",
            "  \"splitFixtureSha256\": \"{}\",\n",
            "  \"finalTime\": {},\n",
            "  \"outputStep\": {},\n",
            "  \"relativeTolerance\": {},\n",
            "  \"absoluteTolerance\": {},\n",
            "  \"maximumStep\": {},\n",
            "  \"sampleCount\": {},\n",
            "  \"solverSteps\": {},\n",
            "  \"rhsEvaluations\": {},\n",
            "  \"maximumDrift\": {{\n",
            "    \"vectorNorm\": {},\n",
            "    \"plusNorm\": {},\n",
            "    \"minusNorm\": {},\n",
            "    \"trilinear\": {}\n",
            "  }},\n",
            "  \"verdict\": \"{}\"\n",
            "}}\n"
        ),
        TRIALITY_FIXTURE_SHA256,
        SPLIT_FIXTURE_SHA256,
        fmt_e(config.final_time, 17),
        fmt_e(config.output_step, 17),
        fmt_e(config.relative_tolerance, 17),
        fmt_e(config.absolute_tolerance, 17),
        fmt_e(config.maximum_step, 17),
        result.samples.len(),
        result.stats.steps,
        result.stats.rhs_evaluations,
        fmt_e(drift.vector_norm, 17),
        fmt_e(drift.plus_norm, 17),
        fmt_e(drift.minus_norm, 17),
        fmt_e(drift.trilinear, 17),
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
    let output_directory = parse_output_directory()?;
    fs::create_dir_all(&output_directory)
        .map_err(|error| format!("create output directory failed: {error}"))?;
    let config = Config::default();
    let result = integrate(&config)?;
    let drift = result.maximum_invariant_drifts();
    let mut passed = true;
    passed &= check(
        "sample_count",
        result.samples.len() == 41,
        &format!("{} samples including endpoints", result.samples.len()),
    );
    passed &= check(
        "vector_norm",
        drift.vector_norm <= DRIFT_LIMIT,
        &format!("maximum drift {}", fmt_e(drift.vector_norm, 6)),
    );
    passed &= check(
        "plus_norm",
        drift.plus_norm <= DRIFT_LIMIT,
        &format!("maximum drift {}", fmt_e(drift.plus_norm, 6)),
    );
    passed &= check(
        "minus_norm",
        drift.minus_norm <= DRIFT_LIMIT,
        &format!("maximum drift {}", fmt_e(drift.minus_norm, 6)),
    );
    passed &= check(
        "trilinear",
        drift.trilinear <= DRIFT_LIMIT,
        &format!("maximum drift {}", fmt_e(drift.trilinear, 6)),
    );
    write_csv(&output_directory, &result)?;
    write_summary(&output_directory, &config, &result, &drift, passed)?;
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
