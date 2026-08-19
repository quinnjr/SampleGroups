from __future__ import annotations

import os

import PyIO
import PyPluMA


class SampleGroupsPlugin:
    """Emit one numeric class label per row of a sample-indexed CSV.

    Bridges DataSplit and SVC: DataSplit writes train/test CSVs whose row
    order fixes the order SVC expects its ``traininggroups`` labels in, but
    no plugin produced that label file. Given the split CSV and a
    sample-metadata TSV (``sample-id<TAB>Description``, as in
    Samples.Svm.txt / Samples.Syn.txt), writes ``1.0`` for rows whose
    description equals ``positive`` and ``0.0`` otherwise — one value per
    line, loadable with ``numpy.loadtxt``.
    """

    def input(self, filename: str) -> None:
        self.parameters = PyIO.readParameters(filename)
        prefix = PyPluMA.prefix()
        self.csvpath = os.path.join(prefix, self.parameters["csvfile"])
        self.labelspath = os.path.join(prefix, self.parameters["labels"])
        self.positive = self.parameters["positive"].strip()
        self.delimiter = self.parameters.get("delimiter", "\t")

    def run(self) -> None:
        labels: dict[str, str] = {}
        with open(self.labelspath) as fh:
            fh.readline()  # header (sample-id<TAB>Description)
            for line in fh:
                parts = line.rstrip("\n").split(self.delimiter)
                if len(parts) >= 2 and parts[0].strip():
                    labels[parts[0].strip().strip('"')] = parts[1].strip()

        self.values: list[float] = []
        missing: list[str] = []
        with open(self.csvpath) as fh:
            fh.readline()  # header
            for line in fh:
                stripped = line.strip()
                if not stripped:
                    continue
                sample = stripped.split(",")[0].strip().strip('"')
                if sample not in labels:
                    missing.append(sample)
                    continue
                self.values.append(1.0 if labels[sample] == self.positive else 0.0)

        if missing:
            raise ValueError(
                "SampleGroups: no label for sample(s): " + ", ".join(missing[:10])
                + (" ..." if len(missing) > 10 else "")
            )
        if not self.values:
            raise ValueError("SampleGroups: no data rows in " + self.csvpath)

    def output(self, filename: str) -> None:
        with open(filename, "w") as out:
            for value in self.values:
                out.write(str(value) + "\n")
