from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

PLUMA = Path(__file__).resolve().parent.parent / "PluMA"
sys.path.insert(0, str(PLUMA))

stub = types.ModuleType("PyPluMA")
stub._prefix = ""
stub.prefix = lambda: stub._prefix
sys.modules["PyPluMA"] = stub

from SampleGroupsPlugin import SampleGroupsPlugin  # noqa: E402


def build_inputs(tmp_path: Path, csv_rows: list[str],
                 label_rows: list[str]) -> Path:
    (tmp_path / "train.csv").write_text(
        "\n".join(['"","f1","f2"'] + csv_rows) + "\n")
    (tmp_path / "labels.txt").write_text(
        "\n".join(["sample-id\tDescription"] + label_rows) + "\n")
    params = tmp_path / "params.txt"
    params.write_text(
        "csvfile\ttrain.csv\nlabels\tlabels.txt\npositive\tParkinsons\n")
    return params


def run(params: Path, tmp_path: Path) -> list[str]:
    stub._prefix = str(tmp_path)
    plugin = SampleGroupsPlugin()
    plugin.input(str(params))
    plugin.run()
    out = tmp_path / "groups.csv"
    plugin.output(str(out))
    return out.read_text().splitlines()


def test_labels_follow_csv_row_order(tmp_path: Path) -> None:
    params = build_inputs(
        tmp_path,
        ['"CTRL_001",1.0,2.0', '"PD_001",3.0,4.0', '"PD_002",5.0,6.0'],
        ["PD_001\tParkinsons", "PD_002\tParkinsons", "CTRL_001\tControl"],
    )
    assert run(params, tmp_path) == ["0.0", "1.0", "1.0"]


def test_bare_and_quoted_ids_both_match(tmp_path: Path) -> None:
    params = build_inputs(
        tmp_path,
        ["PD_001,1.0,2.0", '"CTRL_001",3.0,4.0'],
        ["PD_001\tParkinsons", "CTRL_001\tControl"],
    )
    assert run(params, tmp_path) == ["1.0", "0.0"]


def test_missing_label_is_an_error(tmp_path: Path) -> None:
    params = build_inputs(
        tmp_path,
        ['"PD_001",1.0,2.0', '"MYSTERY_9",3.0,4.0'],
        ["PD_001\tParkinsons"],
    )
    with pytest.raises(ValueError, match="MYSTERY_9"):
        run(params, tmp_path)


def test_empty_csv_is_an_error(tmp_path: Path) -> None:
    params = build_inputs(tmp_path, [], ["PD_001\tParkinsons"])
    with pytest.raises(ValueError, match="no data rows"):
        run(params, tmp_path)
