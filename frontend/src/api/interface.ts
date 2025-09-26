export const API = {
  // 你的 API 定义
};

export interface PlaylistSong {
  songId: number
  songName: string
  artistName: string
  album: string
  duration: string
  coverUrl: string | null
  audioUrl: string
  likeStatus: number
  releaseTime: string | null
}

export interface PlaylistComment {
  commentId: number
  username: string
  userAvatar: string | null
  content: string
  createTime: string
  likeCount: number
}

export interface PlaylistDetail {
  playlistId: number
  title: string
  coverUrl: string | null
  introduction: string
  songs: PlaylistSong[]
  likeStatus: number
  comments: PlaylistComment[]
  isCollected: boolean
}

// 导出 Song 类型
export interface Song {
  songId: number
  songName: string
  artistName: string
  album: string
  lyric: string | null
  duration: string
  coverUrl: string
  audioUrl: string
  likeStatus: number
  releaseTime: string
}

export interface PlaylistComment {
  commentId: number
  username: string
  userAvatar: string | null
  content: string
  createTime: string
  likeCount: number
}

export interface PlaylistDetail {
  playlistId: number
  title: string
  coverUrl: string | null
  introduction: string
  songs: PlaylistSong[]
  likeStatus: number
  comments: PlaylistComment[]
  isCollected: boolean
}

export interface Comment {
  commentId: number
  username: string
  userAvatar: string | null
  content: string
  createTime: string
  likeCount: number
}

export interface SongDetail {
  songId: number
  songName: string
  artistName: string
  album: string
  lyric: string | null
  duration: string
  coverUrl: string
  audioUrl: string
  releaseTime: string
  likeStatus: boolean | null
  comments: Comment[]
}

export interface LyricsResponse{

}

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


