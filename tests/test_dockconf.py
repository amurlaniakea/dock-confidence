"""Tests: each Acceptance Criterion isolated (SDD verification rule)."""
from __future__ import annotations

from pathlib import Path

import pytest

from dockconf.parse import read_poses, Pose, NEAR_NATIVE_THRESHOLD
from dockconf.rmsd import rmsd_to_native, annotate_rmsd
from dockconf.calibrate import calibrate, fit_platt, platt_predict
from dockconf.metrics import (
    expected_calibration_error,
    raw_score_ece,
    top1_accuracy,
    random_baseline_accuracy,
)
from dockconf.report import filter_decoys, write_json, reliability_diagram
from dockconf.data.fixture import make_fixture

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "sample.sdf"
NATIVE = ROOT / "sample_native.pdb"


# ---- AC1: parser reads multimodel SDF, extracts scores -------------------
def test_ac1_parse_sdf_multi():
    poses = read_poses(str(SAMPLE), fmt="sdf", system_id="sys_001")
    assert len(poses) == 6, f"expected 6 poses, got {len(poses)}"
    scored = [p for p in poses if p.raw_score is not None]
    assert len(scored) == 6, "every pose should carry minimizedAffinity"


# ---- AC2: RMSD to native + near_native label -------------------------
def test_ac2_rmsd_native():
    poses = read_poses(str(SAMPLE), fmt="sdf", system_id="sys_001")
    poses = annotate_rmsd(poses, str(NATIVE))
    rmsds = [p.rmsd for p in poses]
    assert all(r is not None for r in rmsds), "all poses should have RMSD"
    best = min(poses, key=lambda p: float(p.rmsd))
    assert best.rmsd < NEAR_NATIVE_THRESHOLD, "best pose should be near-native"
    assert best.near_native is True
    worst = max(poses, key=lambda p: float(p.rmsd))
    assert worst.near_native is False


# ---- AC3: CLI emits valid JSON ------------------------------------------
def test_ac3_cli_json(tmp_path):
    from dockconf.cli import main
    out = tmp_path / "o.json"
    rc = main(["parse", "--input", str(SAMPLE), "--native", str(NATIVE),
                "--out", str(out)])
    assert rc == 0
    import json
    data = json.loads(out.read_text())
    assert isinstance(data, list) and len(data) == 6
    assert all("rmsd" in d and "near_native" in d for d in data)


# ---- AC4: P(near-native) per pose -------------------------------------
def test_ac4_calibrated_p():
    poses, train = make_fixture(seed=42, n_systems=20)
    cal = calibrate(poses, mode="platt", train=train)
    assert all(p.p_near_native is not None for p in cal)
    assert all(0.0 <= p.p_near_native <= 1.0 for p in cal)


# ---- AC5: ECE scalar in [0,1] --------------------------------------
def test_ac5_ece_scalar():
    poses, train = make_fixture(seed=42, n_systems=20)
    cal = calibrate(poses, mode="platt", train=train)
    ece = expected_calibration_error(cal)
    assert ece is not None and 0.0 <= ece <= 1.0


# ---- AC6: reliability diagram PNG non-empty ---------------------------
def test_ac6_reliability_png(tmp_path):
    poses, train = make_fixture(seed=42, n_systems=20)
    cal = calibrate(poses, mode="platt", train=train)
    png = tmp_path / "rel.png"
    path = reliability_diagram(cal, str(png))
    assert path is not None
    assert png.exists() and png.stat().st_size > 1024


# ---- AC7: calibrated ECE < raw ECE (validation) --------------------
def test_ac7_ece_improvement():
    poses, train = make_fixture(seed=42, n_systems=20)
    cal = calibrate(poses, mode="platt", train=train)
    ece_cal = expected_calibration_error(cal)
    ece_raw = raw_score_ece(poses)
    assert ece_cal is not None and ece_raw is not None
    assert ece_cal < ece_raw, f"ECE not improved: {ece_cal} >= {ece_raw}"


# ---- AC8: decoy filter flags >=1 decoy ------------------------------
def test_ac8_decoy_filter():
    poses = read_poses(str(SAMPLE), fmt="sdf", system_id="sys_001")
    poses = annotate_rmsd(poses, str(NATIVE))
    poses = calibrate(poses, mode="heuristic")  # attach p_near_native
    poses = filter_decoys(poses, threshold=0.5)
    n_decoy = sum(1 for p in poses if p.is_decoy is True)
    assert n_decoy >= 1, "should flag at least one decoy"
    # the highest-RMSD pose must be a decoy
    worst = max(poses, key=lambda p: float(p.rmsd))
    assert worst.is_decoy is True


# ---- bonus: platt fit sanity ----------------------------------------
def test_platt_fit():
    scores = [-9.5, -9.4, -3.0, -2.8, -8.1, -1.5]
    labels = [1, 1, 0, 0, 1, 0]
    coef = fit_platt(scores, labels)
    # higher (more negative) score -> higher P
    assert platt_predict(coef, -9.5) > platt_predict(coef, -2.0)
