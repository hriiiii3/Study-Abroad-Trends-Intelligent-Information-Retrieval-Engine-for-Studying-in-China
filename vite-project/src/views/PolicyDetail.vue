<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useContentStore } from '../stores/content'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const contentStore = useContentStore()
const userStore = useUserStore()

const policyId = computed(() => route.params.id)
const currentLanguage = computed(() => contentStore.currentLanguage)
const policy = ref(null)
const loading = ref(false)
const isLoggedIn = computed(() => userStore.isLoggedIn)
const isFavorite = computed(() => userStore.isFavorite('policy', parseInt(policyId.value)))

// 分类名称
const categoryNames = {
  5: { zh: '学生服务与支持', en: 'Student Services & Support' },
  6: { zh: '教育与学习', en: 'Education & Learning' },
  7: { zh: '政策与建设', en: 'Policy & Construction' },
  8: { zh: '国际关系与交流', en: 'International Relations & Exchange' },
  9: { zh: '就业与工作', en: 'Employment & Work' }
}

// 获取政策详情
async function fetchPolicyDetail() {
  loading.value = true
  
  try {
    // 先从store中检查是否已有数据
    const cachedPolicy = contentStore.getPolicyById(policyId.value)
    
    if (cachedPolicy) {
      policy.value = cachedPolicy
    } else {
      // 如果store中没有，则从API获取
      const response = await axios.get(`http://localhost:5000/api/policies/${policyId.value}`)
      policy.value = response.data.policy
    }
  } catch (error) {
    ElMessage.error(currentLanguage.value === 'zh' ? '获取政策详情失败' : 'Failed to fetch policy details')
    console.error(error)
    router.push('/')
  } finally {
    loading.value = false
  }
}

// 切换收藏状态
function toggleFavorite() {
  if (!isLoggedIn.value) {
    ElMessage.warning(currentLanguage.value === 'zh' 
      ? '请先登录后再收藏' 
      : 'Please login to add to favorites')
    router.push('/login')
    return
  }
  
  if (isFavorite.value) {
    // 取消收藏
    userStore.removeFavorite('policy', parseInt(policyId.value))
    ElMessage.success(currentLanguage.value === 'zh' 
      ? '已从收藏中移除' 
      : 'Removed from favorites')
  } else {
    // 添加收藏
    userStore.addFavorite('policy', parseInt(policyId.value), policy.value)
    ElMessage.success(currentLanguage.value === 'zh' 
      ? '已添加到收藏' 
      : 'Added to favorites')
  }
}

// 获取标题（根据当前语言）
function getTitle() {
  if (!policy.value) return ''
  
  if (currentLanguage.value === 'en' && policy.value.title_en) {
    return policy.value.title_en
  }
  return policy.value.title
}

// 获取内容（根据当前语言）
function getContent() {
  if (!policy.value) return ''
  
  if (currentLanguage.value === 'en' && policy.value.content_en) {
    return policy.value.content_en
  }
  return policy.value.content
}

// 获取分类名称
function getCategoryName() {
  if (!policy.value) return ''
  
  const category = policy.value.category
  if (categoryNames[category]) {
    return categoryNames[category][currentLanguage.value]
  }
  return ''
}

onMounted(() => {
  fetchPolicyDetail()
})
</script>

<template>
  <div class="policy-detail-container">
    <el-card v-loading="loading">
      <template v-if="policy">
        <div class="policy-header">
          <div class="header-actions">
            <el-button @click="router.push('/')" class="back-button">
              {{ currentLanguage === 'zh' ? '返回首页' : 'Back to Home' }}
            </el-button>
            
            <el-button 
              type="danger" 
              :icon="isFavorite ? 'StarFilled' : 'Star'"
              @click="toggleFavorite"
              v-if="isLoggedIn"
              class="favorite-button"
            >
              {{ isFavorite 
                ? (currentLanguage === 'zh' ? '取消收藏' : 'Remove from Favorites')
                : (currentLanguage === 'zh' ? '收藏' : 'Add to Favorites') }}
            </el-button>
          </div>
          
          <h1 class="policy-title">{{ getTitle() }}</h1>
          
          <div class="policy-meta">
            <el-tag type="warning">{{ getCategoryName() }}</el-tag>
            <span class="policy-date">{{ policy.created_at }}</span>
          </div>
        </div>
        
        <div class="policy-content">
          <el-image 
            v-if="policy.image_url" 
            :src="policy.image_url" 
            fit="cover"
            class="policy-image"
          />
          
          <div class="policy-text">
            <p v-for="(paragraph, index) in getContent().split('\n')" :key="index">
              {{ paragraph }}
            </p>
          </div>
        </div>
      </template>
    </el-card>
  </div>
</template>

<style scoped>
.policy-detail-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.policy-header {
  margin-bottom: 30px;
  position: relative;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.back-button, .favorite-button {
  margin-bottom: 10px;
}

.policy-title {
  font-size: 28px;
  margin-bottom: 15px;
  color: #303133;
  border-bottom: 1px solid #EBEEF5;
  padding-bottom: 15px;
}

.policy-meta {
  display: flex;
  gap: 15px;
  align-items: center;
  margin-bottom: 20px;
}

.policy-date {
  color: #909399;
  font-size: 14px;
}

.policy-content {
  line-height: 1.8;
}

.policy-image {
  max-width: 100%;
  margin-bottom: 20px;
  border-radius: 8px;
}

.policy-text p {
  margin-bottom: 15px;
}
</style> 