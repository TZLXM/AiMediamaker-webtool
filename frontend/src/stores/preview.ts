import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { PreviewState, FileItem } from '@/types'

export const usePreviewStore = defineStore('preview', () => {
  const preview = ref<PreviewState>({
    visible: false,
    isVideo: false,
  })

  function openPreview(file: FileItem) {
    preview.value = {
      visible: true,
      file,
      isVideo: file.file_type === 'video',
    }
  }

  function closePreview() {
    preview.value.visible = false
  }

  return {
    preview,
    openPreview,
    closePreview,
  }
})
