<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../stores/user'
import axios from 'axios'
import { Upload, Document, Picture, Delete } from '@element-plus/icons-vue'

const props = defineProps({
  accept: {
    type: String,
    default: '.png,.jpg,.jpeg,.gif,.pdf,.doc,.docx'
  },
  maxSize: {
    type: Number,
    default: 5 * 1024 * 1024 // 5MB
  },
  multiple: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['upload-success', 'upload-error'])

const userStore = useUserStore()
const file = ref(null)
const previewUrl = ref('')
const uploadProgress = ref(0)
const isUploading = ref(false)
const errorMessage = ref('')
const uploadedFiles = ref([])

const isImage = computed(() => {
  if (!file.value) return false
  return ['image/jpeg', 'image/png', 'image/gif', 'image/jpg'].includes(file.value.type)
})

const fileSize = computed(() => {
  if (!file.value) return '0 KB'
  const size = file.value.size
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(2)} KB`
  return `${(size / (1024 * 1024)).toFixed(2)} MB`
})

function handleFileSelect(e) {
  const selectedFile = e.target.files[0]
  if (!selectedFile) return
  
  // 检查文件大小
  if (selectedFile.size > props.maxSize) {
    errorMessage.value = '文件大小超过限制'
    file.value = null
    return
  }
  
  file.value = selectedFile
  errorMessage.value = ''
  
  // 如果是图片，创建预览
  if (isImage.value) {
    const reader = new FileReader()
    reader.onload = (e) => {
      previewUrl.value = e.target.result
    }
    reader.readAsDataURL(file.value)
  } else {
    previewUrl.value = ''
  }
}

async function uploadFile() {
  if (!file.value) {
    errorMessage.value = '请先选择文件'
    return
  }
  
  isUploading.value = true
  uploadProgress.value = 0
  errorMessage.value = ''
  
  const formData = new FormData()
  formData.append('file', file.value)
  
  try {
    const response = await axios.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${userStore.token}`
      },
      onUploadProgress: (progressEvent) => {
        uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
      }
    })
    
    // 上传成功
    uploadedFiles.value.push({
      name: file.value.name,
      url: response.data.url,
      size: fileSize.value,
      type: file.value.type
    })
    
    // 清空当前选择
    file.value = null
    previewUrl.value = ''
    
    // 触发成功事件
    emit('upload-success', response.data)
  } catch (error) {
    errorMessage.value = error.response?.data?.error || '上传失败，请重试'
    emit('upload-error', error)
  } finally {
    isUploading.value = false
  }
}

function clearFile() {
  file.value = null
  previewUrl.value = ''
  errorMessage.value = ''
}

function removeUploadedFile(index) {
  uploadedFiles.value.splice(index, 1)
}
</script>

<template>
  <div class="file-uploader">
    <div class="upload-container">
      <div 
        class="upload-area" 
        :class="{ 'has-file': file, 'is-uploading': isUploading }"
      >
        <div v-if="!file">
          <div class="upload-icon">
            <el-icon><Upload /></el-icon>
          </div>
          <div class="upload-text">
            <p>点击或拖拽文件到此处上传</p>
            <p class="upload-tip">支持 {{ props.accept.replace(/\./g, '') }} 格式，单个文件不超过 {{ props.maxSize / (1024 * 1024) }}MB</p>
          </div>
          <input 
            type="file" 
            class="file-input" 
            :accept="props.accept"
            :multiple="props.multiple"
            @change="handleFileSelect"
          />
        </div>
        
        <div v-else class="file-preview">
          <div v-if="isImage && previewUrl" class="image-preview">
            <img :src="previewUrl" alt="预览图" />
          </div>
          <div v-else class="file-info">
            <el-icon><Document /></el-icon>
            <span>{{ file.name }}</span>
          </div>
          
          <div class="file-details">
            <p>文件类型: {{ file.type || '未知' }}</p>
            <p>文件大小: {{ fileSize }}</p>
          </div>
          
          <div v-if="isUploading" class="progress-bar">
            <div class="progress" :style="{ width: `${uploadProgress}%` }"></div>
            <span>{{ uploadProgress }}%</span>
          </div>
          
          <div class="action-buttons">
            <button 
              class="upload-button" 
              @click="uploadFile"
              :disabled="isUploading"
            >
              上传
            </button>
            <button 
              class="cancel-button" 
              @click="clearFile"
              :disabled="isUploading"
            >
              取消
            </button>
          </div>
        </div>
      </div>
      
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
    </div>
    
    <div v-if="uploadedFiles.length > 0" class="uploaded-files">
      <h3>已上传文件</h3>
      <ul>
        <li v-for="(file, index) in uploadedFiles" :key="index" class="uploaded-file">
          <div class="file-info">
            <el-icon v-if="file.type.includes('image')"><Picture /></el-icon>
            <el-icon v-else><Document /></el-icon>
            <a :href="file.url" target="_blank">{{ file.name }}</a>
            <span class="file-size">{{ file.size }}</span>
          </div>
          <button class="remove-button" @click="removeUploadedFile(index)">
            <el-icon><Delete /></el-icon>
          </button>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.file-uploader {
  width: 100%;
  margin-bottom: 20px;
}

.upload-container {
  width: 100%;
  border: 2px dashed #dcdfe6;
  border-radius: 6px;
  background-color: #f5f7fa;
  transition: all 0.3s;
}

.upload-container:hover {
  border-color: #409eff;
}

.upload-area {
  padding: 20px;
  text-align: center;
  position: relative;
  min-height: 180px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.upload-area.has-file {
  background-color: #fff;
}

.upload-icon {
  font-size: 48px;
  color: #8c939d;
  margin-bottom: 10px;
}

.upload-text {
  color: #606266;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 10px;
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.file-preview {
  width: 100%;
}

.image-preview {
  width: 100%;
  max-height: 200px;
  overflow: hidden;
  margin-bottom: 15px;
}

.image-preview img {
  max-width: 100%;
  max-height: 200px;
  object-fit: contain;
}

.file-info {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.file-info i {
  font-size: 24px;
  margin-right: 10px;
  color: #909399;
}

.file-details {
  text-align: left;
  margin-bottom: 15px;
  color: #606266;
  font-size: 14px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background-color: #ebeef5;
  border-radius: 3px;
  margin-bottom: 15px;
  position: relative;
}

.progress {
  height: 100%;
  background-color: #409eff;
  border-radius: 3px;
  transition: width 0.3s;
}

.progress-bar span {
  position: absolute;
  right: 0;
  top: -20px;
  font-size: 12px;
  color: #606266;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.upload-button,
.cancel-button {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.upload-button {
  background-color: #409eff;
  color: white;
}

.upload-button:hover {
  background-color: #66b1ff;
}

.upload-button:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.cancel-button {
  background-color: #f56c6c;
  color: white;
}

.cancel-button:hover {
  background-color: #f78989;
}

.cancel-button:disabled {
  background-color: #fab6b6;
  cursor: not-allowed;
}

.error-message {
  color: #f56c6c;
  margin-top: 10px;
  font-size: 14px;
}

.uploaded-files {
  margin-top: 20px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 10px;
}

.uploaded-files h3 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 16px;
  color: #303133;
}

.uploaded-files ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.uploaded-file {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  border-bottom: 1px solid #ebeef5;
}

.uploaded-file:last-child {
  border-bottom: none;
}

.uploaded-file .file-info {
  display: flex;
  align-items: center;
  margin-bottom: 0;
}

.uploaded-file .file-info a {
  color: #409eff;
  text-decoration: none;
  margin-right: 10px;
}

.uploaded-file .file-info a:hover {
  text-decoration: underline;
}

.uploaded-file .file-size {
  color: #909399;
  font-size: 12px;
}

.remove-button {
  background: none;
  border: none;
  color: #f56c6c;
  cursor: pointer;
  font-size: 16px;
  padding: 4px;
}

.remove-button:hover {
  color: #f78989;
}

@media (max-width: 768px) {
  .upload-area {
    padding: 15px;
    min-height: 150px;
  }
  
  .image-preview {
    max-height: 150px;
  }
  
  .image-preview img {
    max-height: 150px;
  }
}
</style> 