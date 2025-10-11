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

/** 获取轮播图 */
export const getBanner = () => {
  return http<Result>('get', '/banner/getBannerList')
}

/** 获取推荐歌单 */
export const getRecommendedPlaylists = () => {
  return http<Result>('get', '/playlist/getRecommendedPlaylists')
}

/** 获取推荐歌曲 */
export const getRecommendedSongs = () => {
  return http<Result>('get', '/song/getRecommendedSongs')
}

/** 获取所有歌曲 */
export const getAllSongs = (data: object) => {
  return http<ResultTable>('post', '/song/getAllSongs', { data })
}

/** 获取所有vip歌曲 */
export const getAllVipSongs = (data: object) => {
  return http<ResultTable>('post', '/song/getAllVipSongs', { data })
}

/** 获取歌曲详情 */
export const getSongDetail = (id: number) => {
  return http<ResultTable>('get', `/song/getSongDetail/${id}`)
}

/** 获取所有歌手 */
export const getAllArtists = (data: object) => {
  return http<ResultTable>('post', '/artist/getAllArtists', { data })
}

/** 获取歌手详情 */
export const getArtistDetail = (id: number) => {
  return http<Result>('get', `/artist/getArtistDetail/${id}`)
}

/** 获取所有歌单 */
export const getAllPlaylists = (data: object) => {
  return http<ResultTable>('post', '/playlist/getAllPlaylists', { data })
}

/** 获取歌单详情 */
export const getPlaylistDetail = (id: number) => {
  return http<Result>('get', `/playlist/getPlaylistDetail/${id}`)
}

/** 获取用户收藏的歌曲 */
export const getFavoriteSongs = (data: object) => {
  return http<Result>('post', '/favorite/getFavoriteSongs', { data })
}

/** 收藏歌曲 */
export const collectSong = (songId: number) => {
  return http<Result>('post', '/favorite/collectSong', { params: { songId } })
}

/** 取消收藏歌曲 */
export const cancelCollectSong = (songId: number) => {
  return http<Result>('delete', '/favorite/cancelCollectSong', {
    params: { songId },
  })
}

/** 获取用户收藏的歌单 */
export const getFavoritePlaylists = (data: object) => {
  return http<Result>('post', '/favorite/getFavoritePlaylists', { data })
}

/** 收藏歌单 */
export const collectPlaylist = (playlistId: number) => {
  return http<Result>('post', '/favorite/collectPlaylist', {
    params: { playlistId },
  })
}

/** 取消收藏歌单 */
export const cancelCollectPlaylist = (playlistId: number) => {
  return http<Result>('delete', '/favorite/cancelCollectPlaylist', {
    params: { playlistId },
  })
}

/** 新增歌曲评论 */
export const addSongComment = (data: object) => {
  return http<Result>('post', '/comment/addSongComment', { data })
}

/** 新增歌单评论 */
export const addPlaylistComment = (data: object) => {
  return http<Result>('post', '/comment/addPlaylistComment', { data })
}

/** 点赞评论 */
export const likeComment = (commentId: number) => {
  return http<Result>('patch', `/comment/likeComment/${commentId}`)
}

/** 取消点赞评论 */
export const cancelLikeComment = (commentId: number) => {
  return http<Result>('patch', `/comment/cancelLikeComment/${commentId}`)
}

/** 删除评论 */
export const deleteComment = (commentId: number) => {
  return http<Result>('delete', `/comment/deleteComment/${commentId}`)
}

/** 新增反馈 */
export const addFeedback = (data: { content: string }) => {
  return http<Result>('post', '/feedback/addFeedback', { params: data })
}


/** 创建订单 */
export const createOrder = (data: { orderNo: string, userId: number, planId: number }) => {
  return http<Result>('post', '/order/createOrder', { data })
}

/** 支付订单 */
export const payOrder = (orderNo: string) => {
  return http<Result>('put', '/order/payOrder', { params: { orderNo } })
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
  const cls = encodeURIComponent(classes);
  const fn = encodeURIComponent(filename);
  return http<Blob>('get', `/download/${cls}/${fn}`, {
    responseType: 'blob',
    timeout: 0
  });
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
