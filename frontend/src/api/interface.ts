export const API = {
  // 你的 API 定义
};

export type QueryType = "exp_class" | "exp_name" | "sample_id";

export interface ExpClassDTO {
  ExpClass?: string;
  ExperimentCategory?: string;
  Experiment?: string;
  SampleCounts?: number;
}

export interface Experiment {
  UniqueEXID: string;
  ExpClass: string;
  Experiment: string;
}

export interface Sample {
  UniqueID: string;
  UniqueEXID: string;
  SampleID: string;
  Sample: string;
  SampleAge: number;
  SampleDetail: string;
  DepositDatabase: string;
  Accession: string;
  Origin: string;
  CollectionPart: string;
  CollectionTime: string;
}


