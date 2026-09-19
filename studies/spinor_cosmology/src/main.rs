#![forbid(unsafe_code)]
#![deny(warnings)]

use std::env;
use std::fs;
use std::path::{Path, PathBuf};

use spinor_cosmology::{
    integrate, Config, MaximumErrors, RunResult, CL44_FIXTURE_SHA256, N_MAX, N_MIN, OMEGA_M0,
    OMEGA_PSI0, OMEGA_R0, OUTPUT_STEP, W0, WA,
};
use sundials_core::sundials_utils::fmt_e;

const ERROR_LIMIT: f64 = 1.0e-8;

fn parse_output_directory() -> Result<PathBuf, String> {
    let arguments: Vec<String> = env::args().skip(1).collect();
    match arguments.as_slice() {
        [] => Ok(PathBuf::from("artifacts/spinor-cosmology")),
        [flag, path] if flag == "--output" => Ok(PathBuf::from(path)),
        _ => Err("usage: spinor_cosmology [--output DIRECTORY]".to_string()),
    }
}

fn write_csv(directory: &Path, result: &RunResult) -> Result<(), String> {
    let mut headings = vec![
        "N".to_string(),
        "a".to_string(),
        "tau".to_string(),
        "rho".to_string(),
    ];
    headings.extend((0..16).map(|index| format!("psi{index}")));
    headings.extend(
        [
            "S",
            "U",
            "w",
            "E",
            "S_relative_error",
            "rho_relative_error",
            "potential_relative_error",
            "friedmann_relative_error",
        ]
        .into_iter()
        .map(str::to_string),
    );
    let mut lines = vec![headings.join(",")];
    for sample in &result.samples {
        let mut values = vec![
            sample.e_fold,
            sample.scale_factor,
            sample.state[0],
            sample.state[1],
        ];
        values.extend_from_slice(&sample.state[2..]);
        values.extend([
            sample.condensate,
            sample.potential,
            sample.equation_of_state,
            sample.hubble_ratio,
            sample.condensate_relative_error,
            sample.density_relative_error,
            sample.potential_relative_error,
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
    fs::write(directory.join("background.csv"), lines.join("\n") + "\n")
        .map_err(|error| format!("write background.csv failed: {error}"))
}

fn write_summary(
    directory: &Path,
    config: &Config,
    result: &RunResult,
    errors: &MaximumErrors,
    passed: bool,
) -> Result<(), String> {
    let crossing_scale = 1.0 + (1.0 + W0) / WA;
    let content = format!(
        concat!(
            "{{\n",
            "  \"schemaVersion\": 1,\n",
            "  \"study\": \"real-spinor-cosmology\",\n",
            "  \"stateDimension\": 18,\n",
            "  \"cl44FixtureSha256\": \"{}\",\n",
            "  \"parameters\": {{\n",
            "    \"omegaM0\": {},\n",
            "    \"omegaR0\": {},\n",
            "    \"omegaPsi0\": {},\n",
            "    \"w0\": {},\n",
            "    \"wa\": {}\n",
            "  }},\n",
            "  \"nMin\": {},\n",
            "  \"nMax\": {},\n",
            "  \"outputStep\": {},\n",
            "  \"relativeTolerance\": {},\n",
            "  \"absoluteTolerance\": {},\n",
            "  \"maximumStep\": {},\n",
            "  \"sampleCount\": {},\n",
            "  \"solverSteps\": {},\n",
            "  \"rhsEvaluations\": {},\n",
            "  \"wMinusOneCrossingScale\": {},\n",
            "  \"maximumRelativeError\": {{\n",
            "    \"condensate\": {},\n",
            "    \"density\": {},\n",
            "    \"potential\": {},\n",
            "    \"friedmann\": {}\n",
            "  }},\n",
            "  \"verdict\": \"{}\"\n",
            "}}\n"
        ),
        CL44_FIXTURE_SHA256,
        fmt_e(OMEGA_M0, 17),
        fmt_e(OMEGA_R0, 17),
        fmt_e(OMEGA_PSI0, 17),
        fmt_e(W0, 17),
        fmt_e(WA, 17),
        fmt_e(N_MIN, 17),
        fmt_e(N_MAX, 17),
        fmt_e(OUTPUT_STEP, 17),
        fmt_e(config.relative_tolerance, 17),
        fmt_e(config.absolute_tolerance, 17),
        fmt_e(config.maximum_step, 17),
        result.samples.len(),
        result.stats.steps,
        result.stats.rhs_evaluations,
        fmt_e(crossing_scale, 17),
        fmt_e(errors.condensate, 17),
        fmt_e(errors.density, 17),
        fmt_e(errors.potential, 17),
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
    let output_directory = parse_output_directory()?;
    fs::create_dir_all(&output_directory)
        .map_err(|error| format!("create output directory failed: {error}"))?;
    let config = Config::default();
    let result = integrate(&config)?;
    let errors = result.maximum_errors();
    let mut passed = true;
    passed &= check(
        "sample_count",
        result.samples.len() == 1201,
        &format!(
            "{} samples including the present epoch once",
            result.samples.len()
        ),
    );
    passed &= check(
        "condensate_dilution",
        errors.condensate <= ERROR_LIMIT,
        &format!("maximum relative error {}", fmt_e(errors.condensate, 6)),
    );
    passed &= check(
        "analytic_density",
        errors.density <= ERROR_LIMIT,
        &format!("maximum relative error {}", fmt_e(errors.density, 6)),
    );
    passed &= check(
        "potential_reconstruction",
        errors.potential <= ERROR_LIMIT,
        &format!("maximum relative error {}", fmt_e(errors.potential, 6)),
    );
    passed &= check(
        "friedmann_history",
        errors.friedmann <= ERROR_LIMIT,
        &format!("maximum relative error {}", fmt_e(errors.friedmann, 6)),
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
