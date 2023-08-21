import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useBackUrlStore = defineStore('back_url', () => {
  const back_url = ref('http://127.0.0.1:5000/')

  return { back_url }
})
