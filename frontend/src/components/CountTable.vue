<template>
  <div class="flex flex-col items-center justify-center h-screen dark:bg-gray-900">


    <div class="w-full card_box">
      <el-card class="mb-4 card">
        <el-table
            :data="exp_counts"
            border
            class="data-table"
        >
          <el-table-column prop="ExperimentCategory" :label="$t('home_ExperimentCategory')" />
          <el-table-column prop="Experiment" :label="$t('home_Experiment')" />
          <el-table-column prop="SampleCounts" :label="$t('home_SampleCounts')" />
        </el-table>
      </el-card>
    </div>
  </div>



</template>

<script lang="ts" setup>
import {ref, h } from 'vue'

import type { VNode } from 'vue'
import type { TableColumnCtx } from 'element-plus'
import {ExpClassDTO} from '@/api/interface.ts'
import {getAllExpCounts} from '@/api/index.ts'
const exp_data: ExpClassDTO = ref(null);

const exp_counts = ref(null)

const fetch_exp_Data = async () => {

  exp_data.value = await getAllExpClass({
    "query_type": "exp_class",
    "query_value": [
      "string"
    ]
  });
  console.log(exp_data.value);
};

const fetch_exp_Counts = async () => {
  exp_counts.value = await getAllExpCounts(exp_data.value)
  console.log(exp_counts.value);
}

const fetch = async () => {
  await fetch_exp_Data();

  await fetch_exp_Counts();
}

// 调用 fetchData 函数
fetch();


const getSummaries = (param: SummaryMethodProps) => {
  const { columns, data } = param
  const sums: (string | VNode)[] = []
  columns.forEach((column, index) => {
    if (index === 0) {
      sums[index] = h('div', { style: { textDecoration: 'underline' } }, [
        'Total Cost',
      ])
      return
    }
    const values = data.map((item) => Number(item[column.property]))
    if (!values.every((value) => Number.isNaN(value))) {
      sums[index] = `$ ${values.reduce((prev, curr) => {
        const value = Number(curr)
        if (!Number.isNaN(value)) {
          return prev + curr
        } else {
          return prev
        }
      }, 0)}`
    } else {
      sums[index] = 'N/A'
    }
  })

  return sums
}

</script>

<style scoped>

/*
卡片容器，用来调整卡片位置和大小
*/
.card_box {
  display: flex;
  width: 40%;
  height: 40%;
  justify-content: center;
  align-items: center;
}

.card {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.data-table {
  height: 240px;
  flex: 1; /* 让表格占满卡片的剩余空间 */
  overflow: auto; /* 如果内容超出表格大小，自动滚动 */
  margin-top: 5px;
  margin-bottom: 5px;
}

/*--------------- exp复选框 */
.custom-header {
  .el-checkbox {
    display: flex;
    height: unset;
  }
}

</style>
