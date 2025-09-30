<script setup lang="ts">
import { Icon } from '@iconify/vue'
import { formatTime } from '@/utils'
import { UserStore } from '@/stores/modules/user'
// import { AudioStore } from '@/stores/modules/audio'
import { collectSong, cancelCollectSong } from '@/api/system'
import { ElMessage } from 'element-plus'
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useLibraryStore } from '@/stores/modules/library'
import { useArtistStore } from '@/stores/modules/artist'
import { usePlaylistStore } from '@/stores/modules/playlist'

const userStore = UserStore()
const route = useRoute()
const libraryStore = useLibraryStore()

const {
  isPlaying,
  currentTime,
  duration,
  nextTrack,
  prevTrack,
  togglePlayPause,
  seek,
} = useAudioPlayer()

// 获取当前播放歌曲的喜欢状态
const currentSongLikeStatus = computed(() => {
  const currentTrack = audioStore.trackList[audioStore.currentSongIndex]
  return currentTrack?.likeStatus || 0
})

// 更新所有相同歌曲的喜欢状态
const updateAllSongLikeStatus = (songId: number, status: number) => {
  // 更新播放列表中的状态
  audioStore.trackList.forEach((track) => {
    if (Number(track.id) === songId) {
      track.likeStatus = status
    }
  })

  // 更新当前页面的歌曲列表状态
  if (audioStore.currentPageSongs) {
    audioStore.currentPageSongs.forEach((song) => {
      if (song.songId === songId) {
        song.likeStatus = status
      }
    })
  }

  // 更新曲库页面的数据
  if (route.path === '/library' && libraryStore.tableData?.items) {
    const song = libraryStore.tableData.items.find(
      (song) => song.songId === songId
    )
    if (song) {
      song.likeStatus = status
    }
  }

  // 更新歌手详情页的数据
  if (route.path.startsWith('/artist/')) {
    const artistStore = useArtistStore()
    if (artistStore.artistInfo?.songs) {
      const song = artistStore.artistInfo.songs.find(
        (song) => song.songId === songId
      )
      if (song) {
        song.likeStatus = status
      }
    }
  }

  // 更新歌单详情页的数据
  if (route.path.startsWith('/playlist/')) {
    const playlistStore = usePlaylistStore()
    if (playlistStore.songs) {
      const song = playlistStore.songs.find((song) => song.songId === songId)
      if (song) {
        song.likeStatus = status
      }
    }
  }
}

// 处理喜欢/取消喜欢
const handleLike = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }

  const currentTrack = audioStore.trackList[audioStore.currentSongIndex]
  if (!currentTrack) return

  try {
    const songId = Number(currentTrack.id)
    if (currentSongLikeStatus.value === 0) {
      // 收藏歌曲
      const res = await collectSong(songId)
      if (res.code === 0) {
        updateAllSongLikeStatus(songId, 1)
        ElMessage.success('已添加到我的喜欢')
      } else {
        ElMessage.error(res.message || '添加到我的喜欢失败')
      }
    } else {
      // 取消收藏
      const res = await cancelCollectSong(songId)
      if (res.code === 0) {
        updateAllSongLikeStatus(songId, 0)
        ElMessage.success('已取消喜欢')
      } else {
        ElMessage.error(res.message || '取消喜欢失败')
      }
    }
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}
</script>

<template>
  <div class="flex items-center flex-1">

  </div>
</template>


<style scoped>
/* 自定义进度条颜色 */

</style>
