/**
 * @description pinia 持久化参数配置
 * @param {String} key 存储到持久化的 name
 * @return persist
 * */

// 自定义类型声明（可根据实际需要扩展）
interface PiniaPersistConfig {
  key: string;
  storage?: Storage;
  paths?: string[];
  // 你可以根据实际 pinia-plugin-persistedstate 支持的参数继续补充
}

const piniaPersistConfig = (key: string): PiniaPersistConfig => {
  const persist: PiniaPersistConfig = {
    key,
    storage: localStorage,
    // storage: sessionStorage,
  }
  return persist;
}

export default piniaPersistConfig;