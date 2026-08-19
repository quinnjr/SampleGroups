# SampleGroups

PluMA plugin that emits one numeric class label per row of a sample-indexed
CSV, in that CSV's row order.

## Why

`DataSplit` writes `train_data.csv` / `test_data.csv`, and `SVC` then loads a
`traininggroups` file whose *i*-th line must be the label of the *i*-th
training row — but nothing in the pipeline produced that file. SampleGroups
closes the gap: point it at the split CSV and the cohort metadata and it
writes the aligned label vector.

## Parameters (tab-delimited)

| key | value |
| --- | --- |
| `csvfile` | sample-indexed CSV whose row order defines the output order (e.g. `Syn/train_data.csv`) |
| `labels` | metadata file: header line, then `sample-id<TAB>Description` rows (`Samples.Svm.txt` / `Samples.Syn.txt` format) |
| `positive` | Description value mapped to `1.0`; every other value maps to `0.0` |
| `delimiter` | optional, labels-file delimiter (default tab) |

Sample IDs are matched after stripping surrounding double quotes, so quoted
(`"PD_001"`) and bare (`PD_001`) indices both resolve. A sample in `csvfile`
with no metadata entry is an error.

## Output

One label per line (`1.0` / `0.0`), readable with
`numpy.loadtxt(path, delimiter=",")` — exactly what `SVC` expects for
`traininggroups`.

## Example

```
Plugin DataSplit inputfile parameters/parameters.datasplit.txt outputfile CSV
Plugin SampleGroups inputfile parameters/parameters.samplegroups.txt outputfile CSV/traininggroups.csv
Plugin SVC inputfile parameters/parameters.svc.txt outputfile CSV/output_svc.csv
```

with `parameters.samplegroups.txt`:

```
csvfile	CSV/train_data.csv
labels	Samples.Svm.txt
positive	Parkinsons
```
