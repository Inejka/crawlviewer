<template>
  <div id="main">
    <el-slider v-model="divider_percent" />
    <div id="view">
      <div :style="{ width: divider_percent + '%', display: 'flex', flexDirection: 'column' }">
        <el-input-number
          v-model="page_of_pages"
          :min="0"
          @change="handleChange"
          style="margin-top: 10%; margin-bottom: 10px"
        />
        <el-table
          :data="tableData"
          style="width: 100%"
          height="70vh"
          max-height="70vh"
          :border="true"
          :cell-style="{ textAlign: 'center' }"
          :header-cell-style="{ textAlign: 'center' }"
          highlight-current-row
          @current-change="handleCurrentChange"
          ref="singleTableRef"
        >
          <el-table-column prop="name" label="Name" fixed width="200px" />
          <el-table-column prop="metadata" label="Metadata" style="width: 30%"/>
          <el-table-column prop="created" label="Downloading date" style="width: 20%" />
          <el-table-column prop="page_type" label="Source" style="width: 25%" />
        </el-table>
      </div>
      <el-divider direction="vertical" />
      <iframe :style="{ width: 100 - divider_percent + '%' }" id="html_viewer" :src="url_to_load" />
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useBackUrlStore } from '@/stores/store'
import { ElTable } from 'element-plus'

const divider_percent = ref(50)
const page_of_pages = ref(0)
const store = useBackUrlStore()
const tableData = ref<[]>([])
const url_to_load = ref('')
const singleTableRef = ref<InstanceType<typeof ElTable>>()
const current_selected_item = ref(-1)
const pages_to_request = ref(15)

const reload_table = async () => {
  const response = await axios.post(store.back_url + '/pages', {
    page: page_of_pages.value,
    pages_per_page: pages_to_request.value
  })
  tableData.value = response.data
}

const handleKeyEvent = async (event: KeyboardEvent) => {
  if (event.key == 'ArrowUp') handleArrowUp()
  if (event.key == 'ArrowDown') handleArrowDown()
  if (event.key == 'ArrowLeft') handleArrowLeft()
  if (event.key == 'ArrowRight') handleArrowRight()
}

const handleArrowUp = async () => {
  current_selected_item.value -= 1
  if (current_selected_item.value < 0) {
    handleArrowLeft()
    return
  }
  singleTableRef.value?.setCurrentRow(tableData.value[current_selected_item.value])
}

const handleArrowDown = async () => {
  current_selected_item.value += 1
  if (current_selected_item.value > pages_to_request.value - 1) {
    handleArrowRight()
    return
  }
  singleTableRef.value?.setCurrentRow(tableData.value[current_selected_item.value])
}

const handleArrowLeft = async () => {
  page_of_pages.value -= 1
  await reload_table()
  current_selected_item.value = pages_to_request.value - 1
  singleTableRef.value?.setCurrentRow(tableData.value[current_selected_item.value])
}

const handleArrowRight = async () => {
  page_of_pages.value += 1
  await reload_table()
  current_selected_item.value = 0
  singleTableRef.value?.setCurrentRow(tableData.value[current_selected_item.value])
}
const handleChange = () => {
  reload_table()
}
onMounted(async () => {
  reload_table()
  window.addEventListener('keydown', handleKeyEvent)
})

interface DataEntry {
  name: string
  metadata: {}
  created: Date
  page_type: string
}

const handleCurrentChange = (val: DataEntry | undefined) => {
  if (val) url_to_load.value = store.back_url + 'site/' + val?.name + '/' + val?.name + '.html'
  current_selected_item.value = tableData.value.findIndex(
    (element: DataEntry) => element.name == val?.name
  )
}
</script>

<style>
#main {
  height: 100%;
  width: 100%;
  padding-top: 0.5%;
  display: flex;
  flex-direction: column;
  padding-left: 0.5%;
}
#view {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: row;
}
.el-divider--vertical {
  display: inline-block;
  width: 2px;
  height: 100%;
  margin: 0 8px;
  vertical-align: middle;
  position: relative;
  border-left: 1px var(--el-border-color) var(--el-border-style);
}
</style>
