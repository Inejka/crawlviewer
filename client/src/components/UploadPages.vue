<template>
  <div id="main">
    <el-upload
      class="upload-demo"
      drag
      ref="upload"
      :on-change="handleChange"
      :auto-upload="false"
      :limit="1"
      :on-exceed="handleExceed"
      v-model:file-list="fileList"
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">Drop file here or <em>click to upload</em></div>
    </el-upload>
    <el-select v-model="value" class="m-2" placeholder="Select" size="large">
      <el-option
        v-for="item in available_providers"
        :key="item.value"
        :label="item.label"
        :value="item.value"
      />
    </el-select>
    <el-button id="submit" class="ml-3" type="success" @click="submitUpload">
      upload to server
    </el-button>
    <el-text
      class="mx-1"
      type="info"
      style="padding-top: 25px; font-size: x-large; padding-bottom: 25px"
      >Downloads status</el-text
    >
    <el-table
      :data="tableData"
      style="width: 100%; padding-top: 10px"
      :cell-style="{ textAlign: 'center' }"
      :header-cell-style="{ textAlign: 'center' }"
    >
      <el-table-column prop="total_pages" label="Total pages to download" style="width: 50%" />
      <el-table-column prop="total_pages" label="" width="50px"/>
      <el-table-column prop="saved_pages" label="Downloaded pages" style="width: 50%" />
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { UploadFilled } from '@element-plus/icons-vue'
import { ref, onMounted } from 'vue'
import type { UploadProps, UploadUserFile, UploadInstance, UploadRawFile } from 'element-plus'
import { ElNotification, genFileId } from 'element-plus'
import axios from 'axios'
import { useBackUrlStore } from '@/stores/store'

const fileList = ref<UploadUserFile[]>([])
const upload = ref<UploadInstance>()
const store = useBackUrlStore()
interface Provider {
  value: any
  label: any
}
const available_providers = ref<Provider[]>([])
const value = ref('')
const tableData = ref<[]>([])

const handleChange: UploadProps['onChange'] = (uploadFile) => {
  fileList.value.pop()
  fileList.value.push(uploadFile)
}

const handleExceed: UploadProps['onExceed'] = (files) => {
  upload.value!.clearFiles()
  const file = files[0] as UploadRawFile
  file.uid = genFileId()
  upload.value!.handleStart(file)
}

const updateDownloadStatus = async () => {
  const response = await axios.get(store.back_url + 'save/status')
  tableData.value = response.data
}

const submitUpload = async () => {
  if (fileList.value.length == 0) {
    ElNotification({
      title: 'Failed to upload',
      message: 'No file were specified',
      type: 'error'
    })
    return
  }

  if (!value.value) {
    ElNotification({
      title: 'Failed to upload',
      message: 'No provider were specified',
      type: 'error'
    })
    return
  }

  let text = await fileList.value.at(0)?.raw?.text()
  let post_data = { crawler_type: value.value, text: text }
  let respone = await axios.post(store.back_url + 'save', post_data)

  if (respone.data == 'Started download') {
    ElNotification({
      title: 'Success',
      message: 'Download started',
      type: 'success'
    })
  } else {
    ElNotification({
      title: 'Something goes wrong',
      message: respone.data,
      type: 'error'
    })
  }
  upload.value!.clearFiles()
  fileList.value.pop()
}

onMounted(async () => {
  const response = await axios.get(store.back_url + 'available_providers')
  for (let i = 0; i < response.data.length; i++) {
    available_providers.value.push({ value: response.data[i], label: response.data[i] })
  }
  setInterval(updateDownloadStatus, 500)
})
</script>

<style scoped>
#main {
  height: 100%;
  width: 100%;
  padding-top: 4%;
  display: flex;
  flex-direction: column;
  padding-left: 2%;
  padding-right: 2%;
}

#submit {
  margin-top: 15px;
}
</style>
