<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useContentStore } from '../stores/content'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const contentStore = useContentStore()

const currentLanguage = computed(() => contentStore.currentLanguage)
const currentUser = computed(() => userStore.user || {})
const loading = ref(false)
const activeTab = ref('password')
const avatarUrl = ref(currentUser.value.avatar || '')
const uploadLoading = ref(false)

// 个人资料表单
const profileForm = ref({
  username: currentUser.value.username || '',
  email: currentUser.value.email || '',
  nickname: currentUser.value.nickname || '',
  bio: currentUser.value.bio || ''
})

// 密码修改表单
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 收藏统计数据
const newsFavoritesCount = computed(() => userStore.getFavoritesByType('news').length)
const policyFavoritesCount = computed(() => userStore.getFavoritesByType('policy').length)

// 格式化日期
function formatDate(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr)
  return date.toLocaleDateString(
    currentLanguage.value === 'zh' ? 'zh-CN' : 'en-US',
    { year: 'numeric', month: 'long', day: 'numeric' }
  )
}



// 修改密码
async function changePassword() {
  // 表单验证
  if (!passwordForm.value.oldPassword) {
    ElMessage.warning(currentLanguage.value === 'zh' ? '请输入原密码' : 'Please enter your current password')
    return
  }
  
  if (!passwordForm.value.newPassword) {
    ElMessage.warning(currentLanguage.value === 'zh' ? '请输入新密码' : 'Please enter your new password')
    return
  }
  
  if (passwordForm.value.newPassword.length < 6) {
    ElMessage.warning(currentLanguage.value === 'zh' ? '新密码不能少于6个字符' : 'New password must be at least 6 characters')
    return
  }
  
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    ElMessage.warning(currentLanguage.value === 'zh' ? '两次输入的新密码不一致' : 'New passwords do not match')
    return
  }
  
  loading.value = true
  
  try {
    const result = await userStore.changePassword(
      passwordForm.value.oldPassword,
      passwordForm.value.newPassword
    )
    
    if (result.success) {
      ElMessage.success(currentLanguage.value === 'zh' ? '密码修改成功' : 'Password changed successfully')
      // 清空表单
      passwordForm.value = {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
    } else {
      ElMessage.error(result.error || (currentLanguage.value === 'zh' ? '密码修改失败' : 'Failed to change password'))
    }
  } catch (error) {
    ElMessage.error(currentLanguage.value === 'zh' ? '提交失败' : 'Failed to submit')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 处理头像上传
async function handleAvatarUpload(e) {
  const file = e.target.files[0]
  if (!file) return
  
  // 验证文件类型
  if (!file.type.includes('image/')) {
    ElMessage.error(currentLanguage.value === 'zh' ? '请上传图片文件' : 'Please upload an image file')
    return
  }
  
  uploadLoading.value = true
  
  try {
    // 创建FormData对象
    const formData = new FormData()
    formData.append('file', file)
    
    // 上传图片
    const response = await fetch('http://localhost:5000/api/upload-image', {
      method: 'POST',
      body: formData,
      headers: {
        'Authorization': `Bearer ${userStore.user.token}`
      }
    })
    
    const data = await response.json()
    
    if (data.url) {
      avatarUrl.value = `http://localhost:5000${data.url}`
      ElMessage.success(currentLanguage.value === 'zh' ? '头像上传成功' : 'Avatar uploaded successfully')
    } else {
      throw new Error(data.error || 'Upload failed')
    }
  } catch (error) {
    ElMessage.error(currentLanguage.value === 'zh' ? '上传失败' : 'Upload failed')
    console.error(error)
  } finally {
    uploadLoading.value = false
  }
}

// 退出登录
async function handleLogout() {
  try {
    await ElMessageBox.confirm(
      currentLanguage.value === 'zh' 
        ? '确定要退出登录吗？' 
        : 'Are you sure you want to log out?',
      currentLanguage.value === 'zh' ? '提示' : 'Confirm',
      {
        confirmButtonText: currentLanguage.value === 'zh' ? '确定' : 'Confirm',
        cancelButtonText: currentLanguage.value === 'zh' ? '取消' : 'Cancel',
        type: 'warning'
      }
    )
    
    userStore.logout()
    ElMessage.success(currentLanguage.value === 'zh' ? '已成功退出登录' : 'Logged out successfully')
    router.push('/')
  } catch (error) {
    // 用户取消操作，不做处理
  }
}

onMounted(() => {
  // 如果用户信息有更新，更新表单数据
  if (currentUser.value) {
    profileForm.value = {
      username: currentUser.value.username || '',
      email: currentUser.value.email || '',
      nickname: currentUser.value.nickname || '',
      bio: currentUser.value.bio || ''
    }
    avatarUrl.value = currentUser.value.avatar || ''
  }
})
</script>

<template>
  <div class="profile-container">
    <div class="profile-bg"></div>
    
    <div class="profile-content">

      
      <el-row :gutter="20">
        <!-- 左侧用户信息卡片 -->
        <el-col :span="6">
          <el-card class="user-card animate__animated animate__fadeInLeft">
    
            
            <h2 class="username">{{ currentUser.username }}</h2>
            <p class="nickname" v-if="currentUser.nickname">{{ currentUser.nickname }}</p>
            <p class="user-status" v-if="currentUser.is_admin">
              <el-tag type="danger">{{ currentLanguage === 'zh' ? '管理员' : 'Admin' }}</el-tag>
            </p>
            
            <div class="user-stats">
              <div class="stat-item">
                <strong>{{ newsFavoritesCount }}</strong>
                <span>{{ currentLanguage === 'zh' ? '收藏新闻' : 'Favorited News' }}</span>
              </div>
              <div class="stat-item">
                <strong>{{ policyFavoritesCount }}</strong>
                <span>{{ currentLanguage === 'zh' ? '收藏政策' : 'Favorited Policies' }}</span>
              </div>
            </div>
            
            <div class="user-info">
              <div class="info-item" v-if="currentUser.created_at">
                <label>{{ currentLanguage === 'zh' ? '注册时间' : 'Registered on' }}:</label>
                <span>{{ formatDate(currentUser.created_at) }}</span>
              </div>
              <div class="info-item" v-if="currentUser.email">
                <label>{{ currentLanguage === 'zh' ? '邮箱' : 'Email' }}:</label>
                <span>{{ currentUser.email }}</span>
              </div>
            </div>
            
            <div class="action-buttons">
              <el-button 
                type="danger" 
                plain 
                @click="handleLogout"
                block
              >
                {{ currentLanguage === 'zh' ? '退出登录' : 'Logout' }}
              </el-button>
              
              <el-button 
                v-if="currentUser.is_admin"
                type="primary"
                plain
                @click="router.push('/admin')"
                block
                style="margin-top: 10px"
              >
                {{ currentLanguage === 'zh' ? '管理后台' : 'Admin Dashboard' }}
              </el-button>
            </div>
          </el-card>
        </el-col>
        
        <!-- 右侧选项卡 -->
        <el-col :span="18">
          <el-card class="animate__animated animate__fadeInRight">
            <el-tabs v-model="activeTab">

              <!-- 修改密码 -->
              <el-tab-pane name="password">
                <template #label>
                  {{ currentLanguage === 'zh' ? '修改密码' : 'Change Password' }}
                </template>
                <el-form 
                  :model="passwordForm" 
                  label-position="top"
                  :disabled="loading"
                >
                  <el-form-item :label="currentLanguage === 'zh' ? '当前密码' : 'Current Password'">
                    <el-input 
                      v-model="passwordForm.oldPassword" 
                      type="password" 
                      show-password
                      prefix-icon="Lock"
                    />
                  </el-form-item>
                  
                  <el-form-item :label="currentLanguage === 'zh' ? '新密码' : 'New Password'">
                    <el-input 
                      v-model="passwordForm.newPassword" 
                      type="password"
                      show-password
                      prefix-icon="Lock"
                    />
                  </el-form-item>
                  
                  <el-form-item :label="currentLanguage === 'zh' ? '确认新密码' : 'Confirm New Password'">
                    <el-input 
                      v-model="passwordForm.confirmPassword" 
                      type="password"
                      show-password
                      prefix-icon="Lock"
                    />
                  </el-form-item>
                  
                  <el-alert
                    type="info"
                    :title="currentLanguage === 'zh' ? '密码安全提示' : 'Password Security Tips'"
                    :description="currentLanguage === 'zh' ? '请使用至少6个字符，并包含字母、数字和特殊字符的组合，以提高账号安全性。' : 'Use at least 6 characters with a mix of letters, numbers, and symbols to create a stronger password.'"
                    :closable="false"
                    show-icon
                    style="margin-bottom: 20px"
                  />
                  
                  <el-form-item>
                    <el-button 
                      type="primary" 
                      @click="changePassword"
                      :loading="loading"
                    >
                      {{ currentLanguage === 'zh' ? '修改密码' : 'Change Password' }}
                    </el-button>
                  </el-form-item>
                </el-form>
              </el-tab-pane>
              
              <!-- 我的收藏 -->
              <el-tab-pane name="favorites">
                <template #label>
                  {{ currentLanguage === 'zh' ? '我的收藏' : 'My Favorites' }}
                </template>
                <div class="favorites-summary">
                  <div class="stat-card news-card">
                    <el-statistic 
                      :title="currentLanguage === 'zh' ? '收藏新闻' : 'Favorited News'"
                      :value="newsFavoritesCount"
                    >
                      <template #suffix>
                        <el-icon><Document /></el-icon>
                      </template>
                    </el-statistic>
                  </div>
                  
                  <div class="stat-card policy-card">
                    <el-statistic 
                      :title="currentLanguage === 'zh' ? '收藏政策' : 'Favorited Policies'"
                      :value="policyFavoritesCount"
                    >
                      <template #suffix>
                        <el-icon><DocumentChecked /></el-icon>
                      </template>
                    </el-statistic>
                  </div>
                </div>
                
                <div class="view-favorites">
                  <p class="favorites-desc">
                    {{ currentLanguage === 'zh' ? '您可以在收藏页面中查看和管理所有收藏的新闻和政策内容。' : 'You can view and manage all your favorited news and policies on the favorites page.' }}
                  </p>
                  <el-button 
                    type="primary" 
                    @click="router.push('/favorites')"
                    icon="Star"
                  >
                    {{ currentLanguage === 'zh' ? '查看全部收藏' : 'View All Favorites' }}
                  </el-button>
                </div>
              </el-tab-pane>
            </el-tabs>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<style scoped>
.profile-container {
  position: relative;
  min-height: calc(100vh - 120px);
}

.profile-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 200px;
  background: linear-gradient(135deg, #409EFF 0%, #67C23A 100%);
  z-index: -1;
}

.profile-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  color: white;
}

.profile-header h1 {
  margin: 0;
  font-size: 28px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.user-card {
  text-align: center;
  position: relative;
  height: 100%;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.user-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.avatar-container {
  margin: 20px 0;
  position: relative;
  display: inline-block;
}

.avatar-loading {
  opacity: 0.7;
}

.upload-mask {
  position: absolute;
  bottom: 0;
  right: 0;
  background-color: #409EFF;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  color: white;
  transition: all 0.2s ease;
}

.upload-mask:hover {
  transform: scale(1.1);
}

.hidden-input {
  display: none;
}

.username {
  font-size: 22px;
  margin: 10px 0 5px;
  color: #303133;
}

.nickname {
  color: #909399;
  margin: 0 0 15px;
  font-size: 16px;
}

.user-status {
  margin-bottom: 20px;
}

.user-stats {
  display: flex;
  justify-content: space-evenly;
  margin: 20px 0;
  text-align: center;
  padding: 15px 0;
  border-top: 1px dashed #EBEEF5;
  border-bottom: 1px dashed #EBEEF5;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-item strong {
  font-size: 24px;
  color: #409EFF;
  font-weight: 600;
}

.stat-item span {
  font-size: 14px;
  color: #606266;
  margin-top: 5px;
}

.user-info {
  margin: 20px 0;
  text-align: left;
  padding: 0 20px;
}

.info-item {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
}

.info-item label {
  font-weight: bold;
  color: #606266;
  margin-bottom: 5px;
  font-size: 14px;
}

.info-item span {
  color: #303133;
}

.action-buttons {
  margin: 20px 0;
  padding: 0 20px;
}

.favorites-summary {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  flex: 1;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  background-color: #fff;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.news-card {
  border-left: 5px solid #409EFF;
}

.policy-card {
  border-left: 5px solid #67C23A;
}

.view-favorites {
  text-align: center;
  margin-top: 30px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.favorites-desc {
  margin-bottom: 20px;
  color: #606266;
}

/* 添加动画 */
@import 'https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css';
</style> 