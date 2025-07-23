from pathlib import Path
import pandas as pd

samples = (
	pd.read_csv(config["samples"], dtype="string")
	.set_index("sample", drop=False)
	.sort_index()
)

def get_samples():
	return samples.index.tolist()


SAMPLES = get_samples()

def get_upstream_output():
	final_output = []
	final_output.append("out/quantification/samples_merged_counts.csv")
	final_output.append("out/quantification/samples_merged_tpm.csv")

	return final_output

def get_fq(wildcards):
	file1 = samples["read1"].iloc[0]
	file2 = samples["read2"].iloc[0]
	file_path = Path(file1).parent
	end1 = file1.split("_")[-1]
	end2 = file2.split("_")[-1]
	fq1 = "{}/{}_{}".format(file_path, wildcards.sample, end1)
	fq2 = "{}/{}_{}".format(file_path, wildcards.sample, end2)
	return fq1, fq2