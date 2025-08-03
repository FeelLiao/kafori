<template>
  <div class="membership-page">
    <h2>选择会员套餐</h2>

    <el-row :gutter="20" justify="center">
      <!-- 月卡套餐 -->
      <el-col :span="8">
        <el-card
          :class="{ selected: selectedPlan === 1 }"
          @click="selectPlan(1)"
          class="plan-card"
        >
          <h3>月度会员</h3>
          <p class="price">¥18 / 月</p>
          <p class="desc">适合短期使用，灵活开通</p>
        </el-card>
      </el-col>

      <!-- 年卡套餐 -->
      <el-col :span="8">
        <el-card
          :class="{ selected: selectedPlan === 2 }"
          @click="selectPlan(2)"
          class="plan-card"
        >
          <h3>年度会员</h3>
          <p class="price">¥50 / 年</p>
          <p class="desc">超值优惠，长期使用更划算</p>
        </el-card>
      </el-col>
    </el-row>

    <div class="pay-button-wrapper">
      <el-button
        type="primary"
        size="large"
        :disabled="!selectedPlan"
        @click="open"
      >
        立即支付
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { h } from 'vue'
import { ElMessage,ElMessageBox } from 'element-plus'
import { createOrder,payOrder} from '@/api/system'
import { UserStore } from '@/stores/modules/user'
import json from '@eslint/json'

const user = UserStore()

const selectedPlan = ref<string | null>(null)

const order_No = ref<string>('');

function selectPlan(plan: number) {
  selectedPlan.value = plan
}

function handlePay() {
  if (!selectedPlan.value) {
    ElMessage.warning('请先选择一个套餐')
    return
  }

  const planName = selectedPlan.value === 1 ? '月度会员' : '年度会员'
  ElMessage.success(`您选择了 ${planName}，正在跳转到支付...`)
  open()
  // 这里可以调用后端支付接口或跳转到支付页面
}

// 支付确认弹窗
const open = async () => {
  if (!selectedPlan.value) {
    ElMessage.warning('请先选择套餐');
    return;
  }

  // 在弹窗打开之前创建订单
  try {
    const result = await create_order();
    if(result) {
      ElMessage.success("订单创建成功");
    }else {
      ElMessage.error('订单创建失败');
      return;
    }
  } catch (e) {
    ElMessage.error('订单创建失败');
    return;
  }

  ElMessageBox({
    title: '确认支付',
    message: '是否确认支付？',
    showCancelButton: true,
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    beforeClose: async (action, instance, done) => {
      if (action === 'confirm') {
        instance.confirmButtonLoading = true;
        instance.confirmButtonText = '支付中...';

        try {
          const result = await pay_order(); // 使用创建的订单号进行支付
          if(result) {
            ElMessage.success('支付成功');
            done(); // 关闭弹窗
          }else {
            done();
            ElMessage.error('支付失败');
          }
        } catch (e) {
          done();
          ElMessage.error(e.message || '支付失败');
        } finally {
          setTimeout(() => {
            instance.confirmButtonLoading = false;
            instance.confirmButtonText = '确认';
          }, 300);
        }
      } else {
        done(); // 点击取消直接关闭
      }
    },
  });
};

/** 生成 [base, base+max) 的随机整数 */
const getRandom = (max: number, base: number = 0): number =>
  Math.floor(Math.random() * max) + base;

/** 加权因子 */
const WEIGHT = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2] as const;
/** 校验码 */
const CHECK = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2'] as const;

/** 根据前 17 位计算第 18 位校验码 */
const cnNewID = (id17: string): string => {
  const sum = id17
    .slice(0, 17)
    .split('')
    .reduce((s, c, i) => s + Number(c) * WEIGHT[i], 0);
  return CHECK[sum % 11];
};

/** 已生成的身份证号缓存（内存级） */
const idPool = new Set<string>();

/** 生成一个 18 位身份证号，保证当前进程内不重复 */
const generateIdCard = (): string => {
  let id: string;

  do {
    let id17 = '';

    /* 1-6 位：行政区划码，这里简单用 0-9 随机 */
    for (let i = 0; i < 6; i++) id17 += getRandom(10);

    /* 7-10 位：年份 19xx 或 20xx */
    const yearPrefix = getRandom(2, 1); // 1 或 2
    const yearStr =
      yearPrefix === 1
        ? '19' + getRandom(100).toString().padStart(2, '0')
        : '20' + getRandom(22).toString().padStart(2, '0');
    id17 += yearStr;

    /* 11-12 位：月份 01-12 */
    const month = getRandom(12, 1).toString().padStart(2, '0');
    id17 += month;

    /* 13-14 位：日期，根据年月计算最大天数 */
    const maxDay = new Date(Number(yearStr), Number(month), 0).getDate();
    const day = getRandom(maxDay, 1).toString().padStart(2, '0');
    id17 += day;

    /* 15-17 位：顺序码，随机 3 位数字 */
    for (let i = 0; i < 3; i++) id17 += getRandom(10);

    /* 第 18 位：校验码 */
    id = id17 + cnNewID(id17);
  } while (idPool.has(id));

  idPool.add(id);
  return id;
};

const create_order = async () => {

  try {
    order_No.value = generateIdCard();
    // 准备订单数据
    const orderData = {
      orderNo: order_No.value, // 这里应该是动态生成的订单号
      userId: 148, // 这里应该是从用户会话或状态中获取的用户ID
      planId: selectedPlan.value // 这里应该是根据用户选择的套餐获取的套餐ID
    };

    // 调用创建订单的 API 函数
    const result = await createOrder(orderData);

    // 检查创建订单的结果
    if (!result.code) {
      return true;
      // 这里可以添加一些成功后的操作，如跳转到订单详情页、显示成功提示等
    } else {
      return false;
      // 这里可以添加一些失败后的操作，如显示错误提示等
    }
  } catch (error) {
    return false;
    // 这里可以添加一些错误处理的操作，如显示错误提示等
  }
};

const pay_order = async () => {
  try {
    console.log(order_No.value);
    const result = await payOrder(order_No.value);
    // 检查创建订单的结果
    if (!result.code) {
      console.log('订单支付成功', result.data);
      return true;
      // 这里可以添加一些成功后的操作，如跳转到订单详情页、显示成功提示等
    } else {
      console.error('订单支付失败', result.message);
      return false;
      // 这里可以添加一些失败后的操作，如显示错误提示等
    }
  } catch (error) {
    console.error('支付订单时发生错误', error);
    return false;
    // 这里可以添加一些错误处理的操作，如显示错误提示等
  }
}

</script>

<style scoped>
.membership-page {
  padding: 40px;
  text-align: center;
}

.plan-card {
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.plan-card:hover {
  transform: translateY(-5px);
}

.plan-card.selected {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.price {
  font-size: 24px;
  color: #f56c6c;
  margin: 10px 0;
}

.desc {
  color: #999;
}

.pay-button-wrapper {
  margin-top: 40px;
}
</style>