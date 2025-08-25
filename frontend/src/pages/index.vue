<template>
  <div class="w-full flex flex-col gap-1 mainContainer">
    <h3 class="ml-4 text-sm font-semibold text-inactive">
      Overviews
    </h3>
    <p class="content">
      Plant isoform sequencing database (PISO) collected PacBio iso-seq data from 19 plants, and used TAPIS to analyze diploids with sequenced genomes including Amborella trichopoda, Arabidopsis thaliana, Beta vulgaris subsp. vulgaris, Coffea arabica, Fragaria vesca, Hevea brasiliensis, Phyllostachys edulis, Sorghum bicolor, Zea mays; and sequenced polyploids including Chenopodium quinoa, Gossypium barbadense, Panax ginseng, Triticum aestivum. Iso-seq data with no reference genomes including Allium sativum, Astragalus membranaceus, Dipteryx oleifera, Nepenthes ampullaria, Nepenthes rafflesiana and Salvia miltiorrhiza, were analyzed with Cogent. The obtained transcripts for each species were listed in PISO and compared with their annotation. Alternative splicing events were calculated for each species, and novel genes not annotated in reference genomes were listed. Furthermore, GBrowse, BLAST and searching tools were also provided. PISO provides a comprehensive repertory of sequenced iso-seq full-length transcripts in plant genomes.
    </p>
    <h3 class="ml-4 text-sm font-semibold text-inactive">
      Selected Species
    </h3>

    <el-table :data="tableData1" style="width: 100%">
      <el-table-column prop="date" label="Date" width="150" />
      <el-table-column label="Delivery Info">
        <el-table-column prop="name" label="Name" width="120" />
        <el-table-column label="Address Info">
          <el-table-column prop="state" label="State" width="120" />
          <el-table-column prop="city" label="City" width="120" />
          <el-table-column prop="address" label="Address" />
          <el-table-column prop="zip" label="Zip" width="120" />
        </el-table-column>
      </el-table-column>
    </el-table>

    <h3 class="ml-4 text-sm font-semibold text-inactive">
      DataStatic
    </h3>

    <el-table :data="tableData2" style="width: 100%" height="250">
      <el-table-column fixed prop="date" label="Date" width="150" />
      <el-table-column prop="name" label="Name" width="120" />
      <el-table-column prop="state" label="State" width="120" />
      <el-table-column prop="city" label="City" width="320" />
      <el-table-column prop="address" label="Address" width="600" />
      <el-table-column prop="zip" label="Zip" />
    </el-table>



  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { useTransition } from '@vueuse/core'
import { ChatLineRound, Male } from '@element-plus/icons-vue'

const source = ref(0)
const outputValue = useTransition(source, {
  duration: 1500,
})
source.value = 172000




/* 示例数据展示 */

const tableData1 = [
  {
    date: '2016-05-03',
    name: 'Tom',
    state: 'California',
    city: 'Los Angeles',
    address: 'No. 189, Grove St, Los Angeles',
    zip: 'CA 90036',
  },
  {
    date: '2016-05-02',
    name: 'Tom',
    state: 'California',
    city: 'Los Angeles',
    address: 'No. 189, Grove St, Los Angeles',
    zip: 'CA 90036',
  },
  {
    date: '2016-05-04',
    name: 'Tom',
    state: 'California',
    city: 'Los Angeles',
    address: 'No. 189, Grove St, Los Angeles',
    zip: 'CA 90036',
  },
  {
    date: '2016-05-01',
    name: 'Tom',
    state: 'California',
    city: 'Los Angeles',
    address: 'No. 189, Grove St, Los Angeles',
    zip: 'CA 90036',
  },
  {
    date: '2016-05-08',
    name: 'Tom',
    state: 'California',
    city: 'Los Angeles',
    address: 'No. 189, Grove St, Los Angeles',
    zip: 'CA 90036',
  },
  {
    date: '2016-05-06',
    name: 'Tom',
    state: 'California',
    city: 'Los Angeles',
    address: 'No. 189, Grove St, Los Angeles',
    zip: 'CA 90036',
  },
  {
    date: '2016-05-07',
    name: 'Tom',
    state: 'California',
    city: 'Los Angeles',
    address: 'No. 189, Grove St, Los Angeles',
    zip: 'CA 90036',
  },
]


const tableData2 = [
  {
    date: '2016-05-03',
    name: 'Tom',
    state: 'California',
    city: 'Los Angeles',
    address: 'No. 189, Grove St, Los Angeles',
    zip: 'CA 90036',
  },
  {
    date: '2016-05-02',
    name: 'Tom',
    state: 'California',
    city: 'Los Angeles',
    address: 'No. 189, Grove St, Los Angeles',
    zip: 'CA 90036',
  },
  {
    date: '2016-05-04',
    name: 'Tom',
    state: 'California',
    city: 'Los Angeles',
    address: 'No. 189, Grove St, Los Angeles',
    zip: 'CA 90036',
  },
  {
    date: '2016-05-01',
    name: 'Tom',
    state: 'California',
    city: 'Los Angeles',
    address: 'No. 189, Grove St, Los Angeles',
    zip: 'CA 90036',
  },
  {
    date: '2016-05-08',
    name: 'Tom',
    state: 'California',
    city: 'Los Angeles',
    address: 'No. 189, Grove St, Los Angeles',
    zip: 'CA 90036',
  },
  {
    date: '2016-05-06',
    name: 'Tom',
    state: 'California',
    city: 'Los Angeles',
    address: 'No. 189, Grove St, Los Angeles',
    zip: 'CA 90036',
  },
  {
    date: '2016-05-07',
    name: 'Tom',
    state: 'California',
    city: 'Los Angeles',
    address: 'No. 189, Grove St, Los Angeles',
    zip: 'CA 90036',
  },
]

</script>

<style scoped>

.el-col {
  text-align: center;
}


.mainContainer {
  /*display: flex;*/
  padding: 0 100px;
}
</style>
