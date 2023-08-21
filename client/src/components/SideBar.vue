<template>
  <el-menu
    default-active="2"
    class="el-menu-vertical-demo"
    menu-trigger="click"
    :collapse="isCollapse"
    :router="true"
    @open="handleOpen"
    @close="handleClose"
  >
    <el-menu-item index="view_pages" style="margin-top: auto">
      <el-icon><Notebook /></el-icon>
      <template #title>View pages</template>
    </el-menu-item>
    <el-menu-item index="upload_pages">
      <el-icon><Download /></el-icon>
      <template #title>Upload pages</template>
    </el-menu-item>
    <el-menu-item @click="setClose" id="last-item">
      <el-icon><Switch /></el-icon>
      <template #title>Collapse</template>
    </el-menu-item>
  </el-menu>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { Notebook, Download, Switch } from '@element-plus/icons-vue'

const isCollapse = ref(true)
const handleOpen = (key: string, keyPath: string[]) => {
  console.log(key, keyPath)
}
const handleClose = (key: string, keyPath: string[]) => {
  console.log(key, keyPath)
}

const setClose = () => {
  isCollapse.value = !isCollapse.value
}
</script>

<style scoped>
.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 200px;
  min-height: 400px;
}
.el-menu-vertical-demo {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 100%;
  margin-right: 0;
}

#last-item {
  margin-top: auto;
}
</style>
