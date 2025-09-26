import * as system from '@/api/system.ts';
import * as struct from '@/api/interface.ts';
import { ElNotification } from 'element-plus';

type QueryResult<T extends struct.QueryType> =
    T extends "exp_class" ? struct.ExpClassDTO[] :
    T extends "exp_name" ? struct.Experiment[] :
    T extends "sample_id" ? struct.Sample[] :
    never;

export const transcriptsQuery = <T extends struct.QueryType>(
    query_type: T,
    query_value: object
): Promise<QueryResult<T>> => {
  return system.transcriptsQuery(query_type, query_value).then((res): QueryResult<T> => {
    if (res.code === 0 && res.data) {
      ElNotification({
        type: 'success',
        message: '获取列表成功',
        duration: 2000,
      });
      return res.data;
    } else {
      ElNotification({
        type: 'error',
        message: '获取列表失败',
      });
      // 返回空数组，类型安全
      return [] as QueryResult<T>;
    }
  }).catch((error) => {
    console.error('请求失败:', error);
    return [] as QueryResult<T>;
  });
};


export const getAllExpCounts = (param):Promise<struct.ExpClassDTO[]> => {
  return system.getAllExpCounts(param).then((res):Promise<struct.ExpClassDTO[]> => {
    if (res.code === 0 && res.data) {
      ElNotification({
        type: 'success',
        message: '获取counts列表成功',
        duration: 2000,
      });
      return res.data;
    } else {
      ElNotification({
        type: 'error',
        message: '获取counts列表失败',
        duration: 2000,
      });
      return struct.ExpClassDTO;
    }
  }).catch((error) => {
    ElNotification({
      type: 'error',
      message: '获取counts列表失败',
      duration: 2000,
    });
    return [] as struct.ExpClassDTO;
  })
}

export const getYearCounts = (): Promise<any[]> => {
  return system.getYearCounts().then((res): any[] => {
    if (res.code === 0 && res.data) {
      ElNotification({
        type: 'success',
        message: '获取year counts成功',
        duration: 2000,
      });
      return res.data;
    } else {
      ElNotification({
        type: 'error',
        message: '获取year counts失败',
      });
      return [];
    }
  }).catch((error) => {
    ElNotification({
      type: 'error',
      message: '获取year counts失败',
      duration: 2000,
    });
    return [];
  });
}


export const getTranscriptType = (): Promise<any[]> => {
  return system.getTranscriptType().then((res): any[] => {
    if (res.code === 0 && res.data) {
      ElNotification({
        type: 'success',
        message: '获取transcript类型成功',
        duration: 2000,
      });
      return res.data;
    } else {
      ElNotification({
        type: 'error',
        message: '获取transcript类型失败',
      });
      return [];
    }
  }).catch((error) => {
    ElNotification({
      type: 'error',
      message: '获取transcript类型失败',
      duration: 2000,
    });
    return [];
  });
};


export const transcript_analysis = (analysis:string,
                                    width:number,
                                    height:number,
                                    unique_id: string[],
                                    gene_name: string[] = [],
                                    all_gene: boolean = false):Promise<any> =>
{
  const request_data = {
    "analysis": analysis,
    "params": {"width": width, "height": height},
    "data_filter": {
      "unique_id": unique_id,
      "gene_name": gene_name,
      "all_gene": all_gene,
    }
  }
  console.log(request_data)
  return system.transcript_analysis(request_data).then((res):Promise<any> => {
    if (res.code === 0 && res.data) {
      ElNotification({
        type: 'success',
        message: 'transcript_analysis成功',
        duration: 2000,
      });
      return res.data;
    } else {
      ElNotification({
        type: 'error',
        message: 'transcript_analysis失败',
      });
      return [];
    }
  }).catch((error) => {
    ElNotification({
      type: 'error',
      message: 'transcript_analysis失败',
      duration: 2000,
    });
    return [];
  });

}


export const getDownloadCatalog = (): Promise<any[]> => {
  return system.getDownloadCatalog().then((res): any[] => {
    if (res.code === 0 && res.data) {
      ElNotification({
        type: 'success',
        message: '获取DownloadCatalog成功',
        duration: 2000,
      });
      return res.data;
    } else {
      ElNotification({
        type: 'error',
        message: '获取DownloadCatalog失败',
      });
      return [];
    }
  }).catch((error) => {
    ElNotification({
      type: 'error',
      message: '获取DownloadCatalog失败',
      duration: 2000,
    });
    return [];
  });
};

export const putDatabase = (): Promise<any> => {
  return system.putDatabase().then((res): any => {
    if (res.code === 0) {
      ElNotification({
        type: 'success',
        message: '写入数据库成功',
        duration: 2000,
      });
      return res.data;
    } else {
      ElNotification({
        type: 'error',
        message: '写入数据库失败',
      });
      return ;
    }
  }).catch((error) => {
    ElNotification({
      type: 'error',
      message: '写入数据库失败',
      duration: 2000,
    });
    return ;
  });
};

export const rawdataMd5Check = (md5list: string[]): Promise<any> => {
  return system.rawdataMd5Check(md5list).then((res): any => {
    if (res.code === 0) {
      ElNotification({
        type: 'success',
        message: 'md5校验成功',
        duration: 2000,
      });
      return res.data;
    } else {
      ElNotification({
        type: 'error',
        message: 'md5校验失败',
      });
      return ;
    }
  }).catch((error) => {
    ElNotification({
      type: 'error',
      message: 'md5校验失败',
      duration: 2000,
    });
    return ;
  });
};


export const getRawdataResults = () : Promise<any[]> => {
  return system.getRawdataResults().then((res): any[] => {
    if (res.code === 0 && res.data) {
      ElNotification({
        type: 'success',
        message: '获取RawdataResults成功',
        duration: 2000,
      });
      return res.data;
    } else {
      ElNotification({
        type: 'error',
        message: '获取RawdataResults失败',
      });
      return [];
    }
  }).catch((error) => {
    ElNotification({
      type: 'error',
      message: '获取RawdataResults失败',
      duration: 2000,
    });
    return [];
  });
};