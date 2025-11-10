## Transcripts

This database integrates a large collection of _Larix kaempferi_ (Japanese larch) RNA-seq datasets from [NCBI](https://www.ncbi.nlm.nih.gov/), [CNCB](https://www.cncb.ac.cn/), and our own laboratory.  It covers various experimental conditions, including dormancy, temperature stress, and pathogen/pest responses.

To facilitate data retrieval, samples are hierarchically organized according to their metadata — by **Experiment Category** and **Experiment Name**.  
When filtering data, users can easily locate target samples through these categories.  
The main functions of this page are to:

- Filter and retrieve desired datasets from the database.
- Perform downstream analyses on the selected samples to assist specific research tasks.

### Experiment

![](/png/file-20251101152039781.png)

Users can filter data by experiment category (multiple selections supported).  
Several related sub-experiments are merged into a single category.

For instance, the “Dormancy–Activity” category includes experiments such as dormancy release and age-dependent dormancy release.

### Experiment List

![](/png/file-20251101153336559.png)

After selecting one or more experiment categories, click the **Search** button to display all related experiments.

You can further refine your search by filtering based on **Experiment Name**.

### Sample

![](/png/file-20251101153829508.png)

Once an experiment is selected, click **Search** again to view all samples associated with that experiment.

The sample table supports sorting by multiple attributes, allowing users to efficiently locate the desired samples.

### Analysis

![](/png/file-20251101154646494.png)

After selecting samples, users can perform various downstream analyses in this section.

Each analysis tool provides adjustable parameters, which can be fine-tuned according to the research objective to achieve optimal analytical results.

## Pipelines

![](/png/file-20251101162818899.png)

This section allows users to upload their own transcriptome datasets.  The sample information template can be download in the `Downloads` page.

Two upload modes are provided:

1. **Sample Information File (.xlsx) + Expression Matrix File (.csv)**
    - The `SampleID` field in the sample information file must match the column names in the expression matrix.
    - TPM and Counts matrices must be uploaded together; uploading only one type is not supported.
2. **Sample Information File (.xlsx) + Raw Sequencing Data (.fa or .fa.gz)**
    - All raw sequencing files for samples listed in the sample information file must be uploaded.
    - After uploading, click **Start Upstream Analysis** to launch the automated processing pipeline.
    - You can monitor progress through **Check Status**; when the status changes to `finish`, click **Fetch Results** to obtain alignment statistics and other metrics.
    - Finally, click **Write to Database** to store the analysis results in the database.

> All uploaded files must pass validation before they can be written into the database.

## Downloads

This page provides access to downloadable datasets related to the project, including：

- _L. kaempferi_ genome sequences
- Genome annotations
- CDS sequences, and other reference resources.

## Tools

This section offers a **BLAST** tool for sequence comparison.

Users can perform BLAST searches against the genome, CDS, or protein databases to quickly identify genes corresponding to a given DNA sequence.