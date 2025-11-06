import { http } from '../utils/http'

export type Result = {
  code: number
  message: string
  data?: Array<any> | number | string | object
}

export type ResultTable = {
  code: number
  message: string
  data?: {
    /** 列表数据 */
    items: Array<any>
    /** 总条目数 */
    total?: number
    /** 每页显示条目个数 */
    pageSize?: number
    /** 当前页数 */
    currentPage?: number
  }
}

/** 用户登录 */
export const login = (data: object) => {
  return http<Result>('post', '/user/login', { data })
}

/** 用户登出 */
export const logout = () => {
  return http<Result>('post', '/user/logout')
}

/** 发送邮箱验证码 */
export const sendEmailCode = (email: string) => {
  return http<Result>('get', '/user/sendVerificationCode', {
    params: { email },
  })
}

/** 用户注册 */
export const register = (data: object) => {
  return http<Result>('post', '/user/register', { data })
}

/** 重置密码 */
export const resetPassword = (data: object) => {
  return http<Result>('patch', '/user/resetUserPassword', { data })
}

/** 获取用户信息 */
export const getUserInfo = () => {
  return http<Result>('get', '/user/getUserInfo')
}

/** 更新用户信息 */
export const updateUserInfo = (data: object) => {
  return http<Result>('put', '/user/updateUserInfo', { data })
}

/** 更新用户头像 */
export const updateUserAvatar = (formData: FormData) => {
  return http<Result>('patch', '/user/updateUserAvatar', {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    data: formData,
    transformRequest: [(data) => data], // 防止 axios 处理 FormData
  })
}

/** 注销账号 */
export const deleteUser = () => {
  return http<Result>('delete', '/user/deleteAccount')
}


/** 新增反馈 */
export const addFeedback = (data: { content: string }) => {
  return http<Result>('post', '/feedback/addFeedback', { params: data })
}



export const transcriptsQuery = (query_type: string, query_value: object) => {
    return http<ResultTable>('post', '/transcripts/query', {
      data: {
        query_type: query_type,
        query_value: query_value
      }
    })
}


export const getAllExpCounts = (data: object) => {
  return http<ResultTable>('get', '/transcripts/get_allexp_counts', { data })
}

export const getYearCounts = () => {
  return http<Result>('get', '/transcripts/get_year_counts')
}

export const uploadSampleSheet = (formData: FormData) => {
  return http<Result>('post', '/pipeline/sample_sheet/', {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    data: formData,
    transformRequest: [(data) => data], // 防止 axios 处理 FormData
    timeout: 0, // 不超时
  })
}



export const uploadGeneExTpm = (formData: FormData) => {
  return http<Result>('post', '/pipeline/gene_ex_tpm/', {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    data: formData,
    transformRequest: [(data) => data], // 防止 axios 处理 FormData
    timeout: 0, // 不超时
  })
}

export const uploadGeneExCounts = (formData: FormData) => {
  return http<Result>('post', '/pipeline/gene_ex_counts/', {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    data: formData,
    transformRequest: [(data) => data], // 防止 axios 处理 FormData
    timeout: 0, // 不超时
  })
}

export const getTranscriptType = () => {
  return http<ResultTable>('get', '/transcripts/analysis/catalog')
}

export const transcript_analysis = (data: object) => {
  return http<Result>('post', '/transcripts/analysis', {
    data:data,
    timeout: 0, // 10分钟
  })
}

export const uploadTranscriptFile = (rawFile: any, onProgress?: (percent: number) => void) => {
  const filename =
      rawFile.name ||
      `${Date.now()}_${Math.floor(Math.random() * 1000000)}`;
  return http<Result>('put', `/pipeline/rawdata_upload?filename=${filename}`, {
    headers: {
      'Content-Type': 'application/octet-stream',
    },
    data: rawFile,
    onUploadProgress: (progressEvent: ProgressEvent) => {
      if (progressEvent.total) {
        const percent = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress && onProgress(percent);
      }
    },
    timeout: 600000, // 10分钟
  });
};

export const getDownloadCatalog = () => {
  return http<Result>('get', `/download/catalog`)
}

export const downloadFile = (classes: string, filename: string) => {
  const API_BASE = ((import.meta as any).env?.VITE_APP_BASE_API || '').replace(/\/$/, '')
  const cls = encodeURIComponent(classes);
  const fn = encodeURIComponent(filename);
  return `${API_BASE}/download/${cls}/${fn}`;
};


export const putDatabase = () => {
  return http<Result>('post',`/pipeline/put_database/`,{timeout: 0} )
}

export const rawdataMd5Check = (md5list: string[]) => {
  return http<Result>('post', `/pipeline/rawdata_md5_check/`, {data: {files: md5list}, timeout: 0})
}


export const rawdataProcessing = () => {
    return http<Result>('post', `/pipeline/rawdata_processing/`, {timeout: 0})
}

export const getRawdataProcessingStatus = () => {
    return http<Result>('post', `/pipeline/rawdata_status/`)
}

export const getRawdataResults = () => {
    return http<Result>('post', `/pipeline/rawdata_results/` ,{timeout: 0} )
}
