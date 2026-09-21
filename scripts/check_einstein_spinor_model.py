#!/usr/bin/env python3
"""Independently check the exact curved Einstein-spinor reduction."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any


DIMENSION = 8
SPINOR_DIMENSION = 16
TIME_INDEX = 4
TRANSVERSE_INDICES = (0, 1, 2, 3, 5, 6, 7)
EXPECTED_CHECK_COUNT = 4

RationalMatrix = list[list[Fraction]]
RationalVector = list[Fraction]


def fraction_matrix(values: list[list[int]]) -> RationalMatrix:
    return [[Fraction(value) for value in row] for row in values]


def zero_matrix(rows: int, columns: int) -> RationalMatrix:
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def matrix_product(
    left: RationalMatrix,
    right: RationalMatrix,
) -> RationalMatrix:
    return [
        [
            sum(
                (
                    left[row][inner] * right[inner][column]
                    for inner in range(len(right))
                ),
                Fraction(0),
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def matrix_vector(
    matrix: RationalMatrix,
    vector: RationalVector,
) -> RationalVector:
    return [
        sum(
            (
                matrix[row][column] * vector[column]
                for column in range(len(vector))
            ),
            Fraction(0),
        )
        for row in range(len(matrix))
    ]


def row_matrix(
    row_vector: RationalVector,
    matrix: RationalMatrix,
) -> RationalVector:
    return [
        sum(
            (
                row_vector[row] * matrix[row][column]
                for row in range(len(row_vector))
            ),
            Fraction(0),
        )
        for column in range(len(matrix[0]))
    ]


def vector_dot(left: RationalVector, right: RationalVector) -> Fraction:
    return sum(
        (left[index] * right[index] for index in range(len(left))),
        Fraction(0),
    )


def add_vectors(
    left: RationalVector,
    right: RationalVector,
) -> RationalVector:
    return [left[index] + right[index] for index in range(len(left))]


def scale_vector(scale: Fraction, vector: RationalVector) -> RationalVector:
    return [scale * value for value in vector]


def add_scaled_matrix(
    destination: RationalMatrix,
    source: RationalMatrix,
    scale: Fraction,
) -> None:
    for row in range(len(destination)):
        for column in range(len(destination[row])):
            destination[row][column] += scale * source[row][column]


def commutator(
    left: RationalMatrix,
    right: RationalMatrix,
) -> RationalMatrix:
    left_right = matrix_product(left, right)
    right_left = matrix_product(right, left)
    return [
        [
            left_right[row][column] - right_left[row][column]
            for column in range(len(left_right[row]))
        ]
        for row in range(len(left_right))
    ]


def derive_action_stress_tensor(
    geometry: dict[str, Any],
    clifford: dict[str, Any],
) -> tuple[Fraction, Fraction, list[list[Fraction]], Fraction]:
    signs = [
        int(geometry["tangentMetric"][index][index])
        for index in range(DIMENSION)
    ]
    gamma = [fraction_matrix(matrix) for matrix in clifford["generators"]]
    charge = fraction_matrix(geometry["spinorBilinear"]["matrix"])
    spin_connections = [
        zero_matrix(SPINOR_DIMENSION, SPINOR_DIMENSION)
        for _ in range(DIMENSION)
    ]
    for component in geometry["spinConnectionNonzero"]:
        coefficient = Fraction(int(component["coefficient"].split()[0]), 8)
        generator = commutator(
            gamma[int(component["a"])],
            gamma[int(component["b"])],
        )
        add_scaled_matrix(
            spin_connections[int(component["mu"])],
            generator,
            coefficient,
        )

    spinor = [Fraction(0) for _ in range(SPINOR_DIMENSION)]
    spinor[0] = Fraction(1)
    spinor[15] = Fraction(1, 2)
    adjoint = row_matrix(spinor, charge)
    condensate = vector_dot(adjoint, spinor)
    potential = Fraction(1, 20) * condensate + Fraction(19, 20)
    potential_rate = Fraction(1, 20) + Fraction(19, 100)
    pressure = condensate * potential_rate - potential

    time_rotation = matrix_vector(gamma[TIME_INDEX], spinor)
    spinor_time_derivative = add_vectors(
        scale_vector(Fraction(-7, 2), spinor),
        scale_vector(-potential_rate, time_rotation),
    )
    spinor_derivatives = [
        matrix_vector(spin_connections[index], spinor)
        for index in range(DIMENSION)
    ]
    spinor_derivatives[TIME_INDEX] = spinor_time_derivative
    adjoint_derivatives = [
        scale_vector(-1, row_matrix(adjoint, spin_connections[index]))
        for index in range(DIMENSION)
    ]
    adjoint_derivatives[TIME_INDEX] = row_matrix(
        spinor_time_derivative,
        charge,
    )

    gamma_upper = gamma
    gamma_lower = [
        [
            [Fraction(signs[index]) * value for value in row]
            for row in gamma[index]
        ]
        for index in range(DIMENSION)
    ]
    kinetic_left = Fraction(0)
    kinetic_right = Fraction(0)
    for index in range(DIMENSION):
        kinetic_left += vector_dot(
            row_matrix(adjoint, gamma_upper[index]),
            spinor_derivatives[index],
        )
        kinetic_right += vector_dot(
            row_matrix(adjoint_derivatives[index], gamma_upper[index]),
            spinor,
        )
    lagrangian = (kinetic_left - kinetic_right) / 2 - potential

    stress_tensor = [
        [Fraction(0) for _ in range(DIMENSION)]
        for _ in range(DIMENSION)
    ]
    for mu in range(DIMENSION):
        for nu in range(DIMENSION):
            bracket = vector_dot(
                row_matrix(adjoint, gamma_lower[mu]),
                spinor_derivatives[nu],
            )
            bracket += vector_dot(
                row_matrix(adjoint, gamma_lower[nu]),
                spinor_derivatives[mu],
            )
            bracket -= vector_dot(
                row_matrix(adjoint_derivatives[mu], gamma_lower[nu]),
                spinor,
            )
            bracket -= vector_dot(
                row_matrix(adjoint_derivatives[nu], gamma_lower[mu]),
                spinor,
            )
            metric_component = (
                Fraction(signs[mu]) if mu == nu else Fraction(0)
            )
            stress_tensor[mu][nu] = (
                -bracket / 4 + metric_component * lagrangian
            )
    return condensate, lagrangian, stress_tensor, pressure


@dataclass(frozen=True)
class TimeJet:
    value: Fraction
    first: Fraction = Fraction(0)
    second: Fraction = Fraction(0)

    @staticmethod
    def coerce(value: TimeJet | Fraction | int) -> TimeJet:
        if isinstance(value, TimeJet):
            return value
        return TimeJet(Fraction(value))

    def __add__(self, other: TimeJet | Fraction | int) -> TimeJet:
        right = self.coerce(other)
        return TimeJet(
            self.value + right.value,
            self.first + right.first,
            self.second + right.second,
        )

    def __radd__(self, other: TimeJet | Fraction | int) -> TimeJet:
        return self + other

    def __neg__(self) -> TimeJet:
        return TimeJet(-self.value, -self.first, -self.second)

    def __sub__(self, other: TimeJet | Fraction | int) -> TimeJet:
        return self + (-self.coerce(other))

    def __rsub__(self, other: TimeJet | Fraction | int) -> TimeJet:
        return self.coerce(other) - self

    def __mul__(self, other: TimeJet | Fraction | int) -> TimeJet:
        right = self.coerce(other)
        return TimeJet(
            self.value * right.value,
            self.first * right.value + self.value * right.first,
            self.second * right.value
            + 2 * self.first * right.first
            + self.value * right.second,
        )

    def __rmul__(self, other: TimeJet | Fraction | int) -> TimeJet:
        return self * other

    def reciprocal(self) -> TimeJet:
        return TimeJet(
            1 / self.value,
            -self.first / self.value**2,
            2 * self.first**2 / self.value**3
            - self.second / self.value**2,
        )

    def __truediv__(self, other: TimeJet | Fraction | int) -> TimeJet:
        return self * self.coerce(other).reciprocal()

    def __rtruediv__(self, other: TimeJet | Fraction | int) -> TimeJet:
        return self.coerce(other) / self


def time_derivative(value: TimeJet, coordinate: int) -> TimeJet:
    if coordinate != TIME_INDEX:
        return TimeJet(Fraction(0))
    return TimeJet(value.first, value.second)


def derive_einstein_tensor(
    scale_factor: Fraction,
    hubble: Fraction,
    hubble_derivative: Fraction,
    signs: list[int],
) -> tuple[list[list[Fraction]], list[list[Fraction]]]:
    scale = TimeJet(
        scale_factor,
        scale_factor * hubble,
        scale_factor * (hubble * hubble + hubble_derivative),
    )
    zero = TimeJet(Fraction(0))
    metric = [[zero for _ in range(DIMENSION)] for _ in range(DIMENSION)]
    inverse_metric = [
        [zero for _ in range(DIMENSION)] for _ in range(DIMENSION)
    ]
    for index in range(DIMENSION):
        value = (
            TimeJet(Fraction(-1))
            if index == TIME_INDEX
            else signs[index] * scale * scale
        )
        metric[index][index] = value
        inverse_metric[index][index] = value.reciprocal()

    christoffel = [
        [[zero for _ in range(DIMENSION)] for _ in range(DIMENSION)]
        for _ in range(DIMENSION)
    ]
    for rho in range(DIMENSION):
        for mu in range(DIMENSION):
            for nu in range(DIMENSION):
                value = zero
                for sigma in range(DIMENSION):
                    derivatives = (
                        time_derivative(metric[nu][sigma], mu)
                        + time_derivative(metric[mu][sigma], nu)
                        - time_derivative(metric[mu][nu], sigma)
                    )
                    value += inverse_metric[rho][sigma] * derivatives / 2
                christoffel[rho][mu][nu] = value

    ricci = [
        [Fraction(0) for _ in range(DIMENSION)]
        for _ in range(DIMENSION)
    ]
    for mu in range(DIMENSION):
        for nu in range(DIMENSION):
            value = Fraction(0)
            for rho in range(DIMENSION):
                value += time_derivative(
                    christoffel[rho][mu][nu], rho
                ).value
                value -= time_derivative(
                    christoffel[rho][mu][rho], nu
                ).value
                for sigma in range(DIMENSION):
                    value += (
                        christoffel[rho][rho][sigma].value
                        * christoffel[sigma][mu][nu].value
                    )
                    value -= (
                        christoffel[rho][nu][sigma].value
                        * christoffel[sigma][mu][rho].value
                    )
            ricci[mu][nu] = value

    scalar_curvature = sum(
        (
            inverse_metric[mu][nu].value * ricci[mu][nu]
            for mu in range(DIMENSION)
            for nu in range(DIMENSION)
        ),
        Fraction(0),
    )
    einstein = [
        [
            ricci[mu][nu]
            - metric[mu][nu].value * scalar_curvature / 2
            for nu in range(DIMENSION)
        ]
        for mu in range(DIMENSION)
    ]
    metric_values = [
        [metric[mu][nu].value for nu in range(DIMENSION)]
        for mu in range(DIMENSION)
    ]
    return metric_values, einstein


def verify_model(
    geometry_path: Path,
    clifford_path: Path,
) -> dict[str, Any]:
    geometry = json.loads(geometry_path.read_text(encoding="utf-8"))
    clifford = json.loads(clifford_path.read_text(encoding="utf-8"))
    signs = [
        int(geometry["tangentMetric"][index][index])
        for index in range(DIMENSION)
    ]
    condensate, lagrangian, stress_tensor, pressure = (
        derive_action_stress_tensor(geometry, clifford)
    )
    potential = Fraction(1)
    expected_stress = [
        [Fraction(0) for _ in range(DIMENSION)]
        for _ in range(DIMENSION)
    ]
    expected_stress[TIME_INDEX][TIME_INDEX] = potential
    for index in TRANSVERSE_INDICES:
        expected_stress[index][index] = Fraction(signs[index]) * pressure

    curvature_cases = (
        (Fraction(1), Fraction(1), Fraction(-21, 25)),
        (Fraction(3, 2), Fraction(2, 3), Fraction(-5, 7)),
    )
    curvature_passed = True
    for scale_factor, hubble, hubble_derivative in curvature_cases:
        metric, einstein = derive_einstein_tensor(
            scale_factor,
            hubble,
            hubble_derivative,
            signs,
        )
        expected_time = Fraction(21) * hubble * hubble
        spatial_coefficient = -(
            Fraction(6) * hubble_derivative
            + Fraction(21) * hubble * hubble
        )
        for mu in range(DIMENSION):
            for nu in range(DIMENSION):
                if mu == nu == TIME_INDEX:
                    expected = expected_time
                elif mu == nu:
                    expected = spatial_coefficient * metric[mu][nu]
                else:
                    expected = Fraction(0)
                curvature_passed &= einstein[mu][nu] == expected

    _, initial_einstein = derive_einstein_tensor(
        Fraction(1),
        Fraction(1),
        Fraction(-21, 25),
        signs,
    )
    coupled_passed = all(
        initial_einstein[mu][nu]
        == Fraction(21) * stress_tensor[mu][nu]
        for mu in range(DIMENSION)
        for nu in range(DIMENSION)
    )
    checks = {
        "positiveInitialCondensate": condensate == 1,
        "actionStressTensor": lagrangian == pressure
        and stress_tensor == expected_stress,
        "einsteinTensorFromMetric": curvature_passed,
        "coupledEinsteinEquations": coupled_passed,
    }
    return {
        "checks": checks,
        "measurements": {
            "initialCondensate": str(condensate),
            "onShellLagrangian": str(lagrangian),
            "energyDensity": str(stress_tensor[TIME_INDEX][TIME_INDEX]),
            "pressure": str(pressure),
            "initialEinsteinTimeTime": str(
                initial_einstein[TIME_INDEX][TIME_INDEX]
            ),
        },
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--geometry-fixture",
        type=Path,
        default=Path("artifacts/curved-spin-geometry/geometry.json"),
    )
    parser.add_argument(
        "--clifford-fixture",
        type=Path,
        default=Path("artifacts/exact/cl44-seed.json"),
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    report = verify_model(
        arguments.geometry_fixture.resolve(),
        arguments.clifford_fixture.resolve(),
    )
    failures = [
        name for name, passed in report["checks"].items() if not passed
    ]
    for name, passed in report["checks"].items():
        print(f"check_{name}={str(passed).lower()}")
    for name, value in report["measurements"].items():
        print(f"measurement_{name}={value}")
    print(f"check_count={len(report['checks'])}")
    print(f"failed_check_count={len(failures)}")
    if len(report["checks"]) != EXPECTED_CHECK_COUNT:
        print(f"ERROR: expected {EXPECTED_CHECK_COUNT} checks")
        return 1
    if failures:
        print(f"failed_checks={','.join(failures)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
