import { defineStore } from 'pinia'
import piniaPersistConfig from '@/stores/helper/persist'
import type { UserState } from '@/stores/interface'
import { login, logout, getUserInfo } from '@/api/system'
// import { AudioStore } from './audio'

interface UserInfo {
  userId?: number
  username?: string
  phone?: string
  email?: string
  avatarUrl?: string
  introduction?: string
  token?: string
}

interface UserVO {
  Id?: number
  Username?: string
  Phone?: string
  Email?: string
  UserAvatar?: string
  Introduction?: string
  Token?: string
}

/**
 * 用户信息
 */
export const UserStore = defineStore('UserStore', {
  state: (): UserState => ({
    userInfo: {} as UserInfo,
    isLoggedIn: false,
  }),
  actions: {
    // 设置用户信息
    setUserInfo(UserVO: any, token?: string) {
      this.userInfo = {
        userId: UserVO.Id,
        username: UserVO.Username,
        phone: UserVO.Phone,
        email: UserVO.Email,
        avatarUrl: UserVO.UserAvatar,
        introduction: UserVO.Introduction,
        token: token,
      }
      this.isLoggedIn = true
    },
    // 更新头像
    updateUserAvatar(avatarUrl: string) {
      if (this.userInfo) {
        this.userInfo.avatarUrl = avatarUrl
      }
    },
    // 清除用户信息
    clearUserInfo() {
      this.userInfo = {}
      this.isLoggedIn = false

      // 清空所有缓存信息
    },
    // 用户登录
    async userLogin(loginData: { username: string; password: string }) {
      try {
        const response = (await login(loginData))

        if (response.code === 0) {
          // 先保存token
          const token= response.data

          console.log(token)

          // 设置token到userInfo
          this.userInfo.token = token

          try {
            // 再获取用户信息
            console.log("获取用户信息")
            const userInfoResponse = (await getUserInfo())
            console.log(userInfoResponse)
            if (userInfoResponse.code === 0) {
              this.setUserInfo(userInfoResponse.data, token)
              console.log("userInfo: ", this.userInfo)
              return { success: true, message: '登录成功' }
            }
            return {
              success: false,
              message: userInfoResponse.message || '获取用户信息失败',
            }
          } catch (error: any) {
            return {
              success: false,
              message: error.message || '获取用户信息失败',
            }
          }
        }
        return { success: false, message: response.message || '登录失败' }
      } catch (error: any) {
        return { success: false, message: error.message || '登录失败' }
      }
    },
    // 用户退出
    async userLogout() {
      try {
        const response = await logout()
        if (response.code === 0) {
          this.clearUserInfo()
          return { success: true, message: '退出成功' }
        }
        return { success: false, message: response.message }
      } catch (error: any) {
        return { success: false, message: error.message || '退出失败' }
      }
    },
  },
  persist: piniaPersistConfig('UserStore'),
})
