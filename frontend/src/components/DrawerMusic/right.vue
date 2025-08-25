<template>
    <div class="song-lyric overflow-y-auto">
      <transition-group name="lyric-fade">
        <!-- 有歌词 -->
        <ul
          ref="lyricList"
          :style="{ transform: `translateY(${lrcTop}px)` }"
          class="has-lyric font-semibold text-primary-foreground"
          v-if="lyricArr.length"
          key="has-lyric"
          @wheel.prevent="onLyricScroll"
        >
          <li v-for="(item, index) in lyricArr" :key="index" :class="{ active: index === activeLyricIndex }">
            <div>{{ item.lrc }}</div>
<!--            <div>{{ item.tlyric }}</div>-->
          </li>
        </ul>
        <!-- 没歌词 -->
        <div v-else class="no-lyric" key="no-lyric">
          <span>暂无歌词</span>
        </div>
      </transition-group>
    </div>





  <div class="h-full p-6 overflow-y-auto mr-16">
    <div v-if="songDetail" class="space-y-6">
      <!-- 歌曲信息 -->
      <div class="space-y-2">
        <h3 class="text-xl font-semibold text-primary-foreground">歌曲信息</h3>
        <div class="grid grid-cols-2 gap-4 text-sm text-muted-foreground">
          <div>
            <span class="text-primary-foreground">专辑：</span>
            {{ songDetail.album }}
          </div>
          <div>
            <span class="text-primary-foreground">发行时间：</span>
            {{ formatDate(songDetail.releaseTime) }}
          </div>
        </div>
      </div>

      <!-- 评论区 -->
      <div class="space-y-4">
        <h3 class="text-xl font-semibold text-primary-foreground mt-12">
          评论（{{ formatNumber(songDetail.comments?.length || 0) }}）
        </h3>

        <!-- 评论输入框 -->
        <div class="mb-4">
          <div class="flex items-start gap-3">
            <div class="flex-1">
              <el-input
                v-model="commentContent"
                type="textarea"
                :rows="4"
                :maxlength="maxLength"
                placeholder="说点什么吧"
                resize="none"
                show-word-limit
              />
              <div class="flex justify-end items-center mt-4">
                <button
                  @click="handleComment"
                  :disabled="!commentContent.trim()"
                  class="px-6 py-1.5 bg-primary text-white rounded-full text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-primary/90 transition-colors"
                >
                  发布
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 评论列表 -->
        <div v-if="comments.length > 0" class="space-y-4">
          <template v-for="comment in comments" :key="comment.commentId">
            <div class="flex gap-3 group">
              <div
                class="w-10 h-10 rounded-full overflow-hidden flex-shrink-0 mt-0.5"
              >
                <img
                  :src="comment.userAvatar || coverImg"
                  alt="avatar"
                  class="w-full h-full object-cover"
                />
              </div>
              <div class="flex-1">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-medium text-blue-500">{{
                      comment.username
                    }}</span>
                </div>
                <p class="text-sm mt-1 mb-2">{{ comment.content }}</p>
                <div
                  class="flex items-center justify-between text-sm text-gray-400"
                >
                  <span class="text-xs">{{ comment.createTime }}</span>
                  <div class="flex items-center gap-4">
                    <!-- 如果是用户自己的评论，显示删除按钮 -->
                    <button
                      v-if="comment.username === currentUsername"
                      class="flex items-center gap-1 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                      @click="handleDelete(comment)"
                    >
                      <icon-material-symbols:delete-outline />
                      <span>删除</span>
                    </button>
                    <button
                      class="flex items-center gap-1 hover:text-gray-600"
                      @click="handleLike(comment)"
                    >
                      <span>{{ formatNumber(comment.likeCount) }}</span>
                      <icon-material-symbols:thumb-up />
                    </button>
                  </div>
                </div>
              </div>
            </div>
            <div class="border-b border-gray-300/70"></div>
          </template>
        </div>
        <div v-else class="text-center py-8 text-gray-500">
          <p>暂无评论，快来抢沙发吧~</p>
        </div>
      </div>
    </div>
    <div v-else class="flex items-center justify-center h-full">
      <el-empty description="暂无歌曲信息" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue';
import { useAudioPlayer } from '@/hooks/useAudioPlayer';
import { parseLyrics } from '@/utils/parsedLyrics';

import type { SongDetail } from '@/api/interface'
import { inject, type Ref, computed } from 'vue'
import { formatNumber } from '@/utils'
import coverImg from '@/assets/cover.png'
import {
  likeComment,
  addSongComment,
  getSongDetail,
  deleteComment,
} from '@/api/system'
import { ElMessage } from 'element-plus'
import { UserStore } from '@/stores/modules/user'

const lrcTop = ref(0); // 控制歌词滚动的偏移量
const activeLyricIndex = ref(0); // 当前高亮的歌词索引
const lyricList = ref(null); // 歌词列表的 DOM 引用
const lineHeight = 34; // 每行歌词的高度
const visibleLines = 8; // 歌词框中显示的行数
const halfVisibleLines = Math.floor(visibleLines / 2); // 歌词框中显示的行数的一半

const {
  currentTrack,
  isPlaying,
  currentTime,
  lyrics,
  duration,
  nextTrack,
  prevTrack,
  togglePlayPause,
  seek,
  setPlayMode,
} = useAudioPlayer();

const lyricArr = ref(parseLyrics(lyrics.value)); // 解析歌词数据

// 更新歌词滚动位置
const updateLyricPosition = (currentTime) => {
  if (!lyricArr.value || lyricArr.value.length === 0) {
    console.warn('Lyrics array is not loaded yet');
    return;
  }

  const currentTimeMs = currentTime * 1000; // 将 currentTime 转换为毫秒
  const index = lyricArr.value.findIndex(item => item.time > currentTimeMs);

  if (index !== -1) {
    activeLyricIndex.value = index - 1;
    // 计算偏移量，使当前高亮歌词垂直居中
    lrcTop.value = -(activeLyricIndex.value - halfVisibleLines) * lineHeight;
  } else {
    // 如果没有找到合适的索引，可能是当前时间超过了所有歌词的时间
    activeLyricIndex.value = lyricArr.value.length - 1;
    lrcTop.value = -(activeLyricIndex.value - halfVisibleLines) * lineHeight;
    // lrcTop.value = -(lyricArr.value.length - visibleLines) * lineHeight;
  }
};

// 鼠标滚动事件处理
let debounceTimeout = null; // 用于存储定时器

const onLyricScroll = (event) => {
  // 清除之前的定时器
  if (debounceTimeout) {
    clearTimeout(debounceTimeout);
  }

  // 设置新的定时器
  debounceTimeout = setTimeout(() => {
    const delta = event.deltaY; // 获取滚动方向
    const step = lineHeight; // 每次滚动的固定步长，直接使用歌词行高
    const currentTop = lrcTop.value; // 当前的偏移量
    const maxTop = (lyricArr.value.length - visibleLines) * lineHeight; // 最大滚动距离

    // 根据滚动方向计算新的偏移量
    let newTop = currentTop - (delta > 0 ? step : -step);

    // 边界处理，确保滚动不会超出范围
    newTop = Math.max(Math.min(newTop, 0), -maxTop);

    lrcTop.value = newTop;
  }, 10); // 防抖时间间隔，可以根据需要调整
};

// 监听 currentTime 的变化
watch(currentTime, (newTime, oldTime) => {
  if (newTime !== oldTime) {
    updateLyricPosition(newTime);
  }
});

// 监听 lyrics 的变化
watch(lyrics, (newLyrics, oldLyrics) => {
  if (newLyrics !== oldLyrics) {
    // console.log(parseLyrics(lyrics.value));
    lyricArr.value = parseLyrics(lyrics.value);
    lrcTop.value = 0; // 重置偏移量
    activeLyricIndex.value = 0; // 重置高亮索引
  }
});

// 初始化歌词列表高度
onMounted(() => {
  nextTick(() => {
    if (lyricList.value) {
      lyricList.value.style.height = `${lyricArr.value.length * lineHeight}px`;
    }
  });
});


// ------------------------------------

const songDetail = inject<Ref<SongDetail | null>>('songDetail')
const userStore = UserStore()

// 获取当前用户名
const currentUsername = computed(() => userStore.userInfo?.username || '')

// 评论相关
const commentContent = ref('')
const maxLength = 180

// 对评论进行排序，最新的显示在前面
const comments = computed(() => {
  if (!songDetail.value?.comments) return []
  return [...songDetail.value.comments].sort(
    (a, b) => b.commentId - a.commentId
  )
})

// 发布评论
const handleComment = async () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }

  if (!commentContent.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }

  try {
    const songId = songDetail.value?.songId
    if (!songId) return

    const content = commentContent.value.trim()
    const res = await addSongComment({
      songId,
      content,
    })

    if (res.code === 0) {
      ElMessage.success('评论发布成功')
      commentContent.value = ''
      // 重新获取歌曲详情以更新评论列表
      const detailRes = await getSongDetail(songId)
      if (detailRes.code === 0 && detailRes.data) {
        songDetail.value = detailRes.data as unknown as SongDetail
      }
    } else {
      ElMessage.error('评论发布失败')
    }
  } catch (error) {
    ElMessage.error('评论发布失败')
  }
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

// 处理点赞
const handleLike = async (comment: any) => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    return
  }

  try {
    // 调用点赞接口
    const res = await likeComment(comment.commentId)
    if (res.code === 0) {
      // 更新评论的点赞数量
      if (songDetail.value && songDetail.value.comments) {
        const updatedComments = songDetail.value.comments.map((item) => {
          if (item.commentId === comment.commentId) {
            return {
              ...item,
              likeCount: item.likeCount + 1,
            }
          }
          return item
        })

        songDetail.value = {
          ...songDetail.value,
          comments: updatedComments,
        }
      }

      ElMessage.success('点赞成功')
    }
  } catch (error) {
    ElMessage.error('点赞失败')
  }
}

// 删除评论
const handleDelete = async (comment: any) => {
  try {
    const res = await deleteComment(comment.commentId)
    if (res.code === 0) {
      ElMessage.success('删除成功')
      // 重新获取歌曲详情以更新评论列表
      const songId = songDetail.value?.songId
      if (songId) {
        const detailRes = await getSongDetail(songId)
        if (detailRes.code === 0 && detailRes.data) {
          songDetail.value = detailRes.data as unknown as SongDetail
        }
      }
    } else {
      ElMessage.error('删除失败')
    }
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

</script>

<style scoped>
.lyric-container {
  width: 100%;
  max-width: 600px;
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.0); /* 半透明背景 */
  //border-radius: 15px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.0);
  color: #ffffff; /* 文字颜色 */
  font-family: Arial, sans-serif;
}

.song-lyric {
  position: relative;
  height: 300px;
  overflow: hidden; /* 确保滚动条可以显示 */
  background-color: rgba(0, 0, 0, 0.0); /* 半透明背景 */
  border: 1px solid rgba(255, 255, 255, 0.0); /* 半透明边框 */
  border-radius: 10px;
}

.has-lyric {
  position: absolute;
  width: 100%;
  text-align: center; /* 歌词水平居中 */
  transition: transform 0.3s ease;
}

.has-lyric li {
  margin-bottom: 10px;
  font-size: 16px;
  //color: #ffffff;
  transition: opacity 0.3s ease;
}

.has-lyric li.active {
  font-weight: bold;
  color: #ff6600;
}

.no-lyric {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  font-size: 18px;
  color: #999;
}

/* 动画效果 */
.lyric-fade-enter-active, .lyric-fade-leave-active {
  transition: opacity 0.3s;
}
.lyric-fade-enter-from, .lyric-fade-leave-to {
  opacity: 0;
}






.el-button {
  --el-button-hover-text-color: var(--el-color-primary);
  --el-button-hover-bg-color: transparent;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-textarea__inner) {
  border-radius: 12px !important;
}
</style>