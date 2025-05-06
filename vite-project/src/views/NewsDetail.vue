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

const newsId = computed(() => route.params.id)
const currentLanguage = computed(() => contentStore.currentLanguage)
const news = ref(null)
const loading = ref(false)
const isLoggedIn = computed(() => userStore.isLoggedIn)
const isFavorite = computed(() => userStore.isFavorite('news', parseInt(newsId.value)))

// 分类名称
const categoryNames = {
  0: { zh: '教育咨询', en: 'Education Consultation' },
  1: { zh: '国际合作', en: 'International Cooperation' },
  2: { zh: '全球化与来华留学', en: 'Globalization & Study in China' },
  3: { zh: '教育政策解读', en: 'Education Policy Interpretation' },
  4: { zh: '在华发展机遇', en: 'Development Opportunities in China' }
}

// 获取新闻详情
async function fetchNewsDetail() {
  loading.value = true
  
  try {
    // 先从store中检查是否已有数据
    const cachedNews = contentStore.getNewsById(newsId.value)
    
    if (cachedNews) {
      news.value = cachedNews
    } else {
      // 如果store中没有，则从API获取
      const response = await axios.get(`http://localhost:5000/api/news/${newsId.value}`)
      news.value = response.data.news
    }
  } catch (error) {
    ElMessage.error(currentLanguage.value === 'zh' ? '获取新闻详情失败' : 'Failed to fetch news details')
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
    userStore.removeFavorite('news', parseInt(newsId.value))
    ElMessage.success(currentLanguage.value === 'zh' 
      ? '已从收藏中移除' 
      : 'Removed from favorites')
  } else {
    // 添加收藏
    userStore.addFavorite('news', parseInt(newsId.value), news.value)
    ElMessage.success(currentLanguage.value === 'zh' 
      ? '已添加到收藏' 
      : 'Added to favorites')
  }
}

// 获取标题（根据当前语言）
function getTitle() {
  if (!news.value) return ''
  
  if (currentLanguage.value === 'en' && news.value.title_en) {
    return news.value.title_en
  }
  return news.value.title
}

// 获取内容（根据当前语言）
function getContent() {
  if (!news.value) return ''
  
  if (currentLanguage.value === 'en' && news.value.content_en) {
    return news.value.content_en
  }
  return news.value.content
}

// 获取分类名称
function getCategoryName() {
  if (!news.value) return ''
  
  const category = news.value.category
  if (categoryNames[category]) {
    return categoryNames[category][currentLanguage.value]
  }
  return ''
}

onMounted(() => {
  fetchNewsDetail()
})
</script>

<template>
  <div class="news-detail-container">
    <el-card v-loading="loading">
      <template v-if="news">
        <div class="news-header">
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
          
          <h1 class="news-title">{{ getTitle() }}</h1>
          
          <div class="news-meta">
            <el-tag type="success">{{ getCategoryName() }}</el-tag>
            <span class="news-date">{{ news.created_at }}</span>
          </div>
        </div>
        
        <div class="news-content">
          <el-image 
            v-if="news.image_url" 
            :src="news.image_url" 
            fit="cover"
            class="news-image"
          />
          
          <div class="news-text">
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
.news-detail-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.news-header {
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

.news-title {
  font-size: 28px;
  margin-bottom: 15px;
  color: #303133;
  border-bottom: 1px solid #EBEEF5;
  padding-bottom: 15px;
}

.news-meta {
  display: flex;
  gap: 15px;
  align-items: center;
  margin-bottom: 20px;
}

.news-date {
  color: #909399;
  font-size: 14px;
}

.news-content {
  line-height: 1.8;
}

.news-image {
  max-width: 100%;
  margin-bottom: 20px;
  border-radius: 8px;
}

.news-text p {
  margin-bottom: 15px;
}
</style> 