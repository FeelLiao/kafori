import { useNavigatorLanguage } from '@vueuse/core'
/*
*/
import { getCurrentInstance } from 'vue';
import { useI18n } from 'vue-i18n'
import ElementPlus from 'element-plus';
import zhCn from 'element-plus/dist/locale/zh-cn.mjs';
import en from 'element-plus/dist/locale/en.mjs';
/**
 * 获取浏览器语言
 * @returns {string} 当前浏览器的语言代码
 */

/**
 * 定义的全局变量
 */


const elementLocales = { zh: zhCn, en };


export function useLangSwitcher() {
  const { locale } = useI18n(); // 调用 useI18n 钩子
  const instance = getCurrentInstance();

  function setLang(lang: string) {
    locale.value = lang; // 更新 locale
    localStorage.setItem('lang', lang);
    // instance?.appContext.app.use(ElementPlus, { locale: elementLocales[lang] });
  }

  function initLang() {
    const savedLang = localStorage.getItem('lang');
    if (savedLang && elementLocales[savedLang]) {
      setLang(savedLang);
    } else {
      setLang('en'); // 默认语言
    }
  }

  return { setLang, initLang };
}




export function formatTime(seconds: number): string {
  // 将秒数转换为整数分钟数和剩余秒数
  const min = Math.floor(seconds / 60)
  const sec = Math.floor(seconds % 60)

  // 返回格式化的字符串，确保分钟和秒数都至少有两位数
  return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`
}

export function formatMillisecondsToTime(totalMilliseconds: number) {
  const totalSeconds = Math.floor(totalMilliseconds / 1000)
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds - hours * 3600) / 60)
  const seconds = totalSeconds % 60

  return [hours, minutes, seconds]
    .map((n) => (n < 10 ? `0${n}` : n.toString()))
    .filter((val, index) => val !== '00' || index > 0) // 移除开头的"00"小时
    .join(':')
}

/**
 * @description 获取当前时间对应的提示语
 * @returns {String}
 */
export function getTimeState() {
  const timeNow = new Date()
  const hours = timeNow.getHours()
  if (hours >= 6 && hours <= 10) return `早上好 ⛅`
  if (hours >= 10 && hours <= 14) return `中午好 🌞`
  if (hours >= 14 && hours <= 18) return `下午好 🌞`
  if (hours >= 18 && hours <= 24) return `晚上好 🌛`
  if (hours >= 0 && hours <= 6) return `凌晨好 🌛`
}

export function formatNumber(num: number): string {
  if (num >= 1e8) {
    return (num / 1e8).toFixed(0) + '亿' // 1亿
  } else if (num >= 1e4) {
    return (num / 1e4).toFixed(0) + 'W' // 1万
  } else {
    return num.toString() // 小于1万的直接返回
  }
}

export function replaceUrlParams(url: string, newParam: string): string {
  // 找到第一个出现问号的位置
  const questionMarkIndex = url.indexOf('?')

  // 如果没有找到问号，直接返回原始的 URL
  if (questionMarkIndex === -1) {
    return url
  }

  // 提取问号之前的部分（即基本 URL）
  const baseUrl = url.substring(0, questionMarkIndex)

  // 生成新的 URL，替换参数
  return `${baseUrl}?${newParam}`
}

export function parseTimestamp(timestamp: string): string {
  // 创建一个 Date 对象
  const date = new Date(timestamp)

  // 获取年、月、日、时、分、秒
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0') // 月份从0开始，所以要加1
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')

  // 返回格式化后的日期字符串
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}
