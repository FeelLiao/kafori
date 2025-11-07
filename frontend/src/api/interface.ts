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


// 参数的公共字段
interface BaseParam {
  title?: string;
  description?: string;
  default?: any;
}

// number 参数
export interface NumberParam extends BaseParam {
  TYPE: 'number';
  minimum?: number;
  maximum?: number;
}

// string 参数（你后端以后加上就行）
export interface StringParam extends BaseParam {
  TYPE: 'string';
}

// enum 参数
export interface EnumParam extends BaseParam {
  TYPE: 'enum';
  ENUM: string[];
}

export type ParamProperty = NumberParam | StringParam | EnumParam;

export interface ParamsSchema {
  title: string;
  type: 'object';
  properties: Record<string, ParamProperty>;
}


// catalog对应的数据类型
export interface AnalysisCatalog {
  id: string;                 // e.g. "pca"
  title: string;              // e.g. "PCA"
  input_type: string;         // "tpm" | "counts" | ...
  gene_filter: boolean;
  params_schema: ParamsSchema;
}


