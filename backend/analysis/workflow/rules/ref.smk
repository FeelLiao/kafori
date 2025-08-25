rule hisat2_index:
		input:
				fasta=config["ref"]["genome"],
		output:
				directory("out/hisat2_index"),
		params:
				extra="--seed 42",
		priority: 50,
		cache: True,
		conda:
				"../envs/hisat2.yaml",
		log:
				"out/logs/hisat2_index.log",
		threads: 10
		script:
				"../scripts/hisat2_index.py"