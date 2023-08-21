<script setup lang="ts">
import { RouterView } from 'vue-router'
import SideBar from './components/SideBar.vue'
</script>

<template>
  <div>
    <SideBar></SideBar>
    <RouterView />
  </div>
</template>

<style scoped>
div {
  min-height: 100%;
  display: flex;
  flex-direction: row;
  width: 100%;
}
</style>
