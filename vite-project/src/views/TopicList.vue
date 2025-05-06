<script setup lang="js">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useContentStore } from '../stores/content'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 接收props - type(news/policy)和topicId
const props = defineProps({
  type: {
    type: String,
    default: 'news' // 默认显示新闻
  },
  topicId: {
    type: Number,
    default: 0
  }
})

const router = useRouter()
const contentStore = useContentStore()

const currentLanguage = computed(() => contentStore.currentLanguage)

// 数据状态
const loading = ref(false)
const contentList = ref([])
const topicName = ref('')
const searchKeyword = ref('')
const searchResults = ref([])
const showSearchResults = ref(false)
const sortOrder = ref('desc') // 默认降序排列（最新的在前面）

// 是否是新闻类型
const isNews = computed(() => props.type === 'news')

// 排序后的内容列表
const sortedContentList = computed(() => {
  const list = showSearchResults.value ? [...searchResults.value] : [...contentList.value]
  
  return list.sort((a, b) => {
    const dateA = a.date_published ? new Date(a.date_published) : new Date(0)
    const dateB = b.date_published ? new Date(b.date_published) : new Date(0)
    return sortOrder.value === 'asc' ? dateA - dateB : dateB - dateA
  })
})

// 获取页面标题
const pageTitle = computed(() => {
  if (isNews.value) {
    return currentLanguage.value === 'zh' ? '新闻中心' : 'News Center'
  } else {
    return currentLanguage.value === 'zh' ? '政策中心' : 'Policy Center'
  }
})

// 获取主题信息
async function fetchTopicInfo() {
  try {
    const response = await axios.get('/api/policy-topics')
    if (response.data && response.data.topics) {
      const topics = response.data.topics
      const currentTopic = topics.find(t => t.topic_id === props.topicId)
      if (currentTopic) {
        topicName.value = currentTopic.topic_name
      }
    }
  } catch (error) {
    console.error('获取主题信息失败:', error)
  }
}

// 获取数据
async function fetchData() {
  loading.value = true
  
  try {
    if (isNews.value) {
      // 获取新闻数据
      if (!contentStore.news || contentStore.news.length === 0) {
        await contentStore.fetchNews()
      }
      
      // 根据主题ID过滤
      contentList.value = contentStore.newsByTopicId(props.topicId)
    } else {
      // 获取政策数据
      if (!contentStore.policies || contentStore.policies.length === 0) {
        await contentStore.fetchPolicies()
      }
      
      // 根据主题ID过滤
      contentList.value = contentStore.policiesByTopicId(props.topicId)
    }
  } catch (error) {
    console.error('获取数据失败:', error)
    ElMessage.error(currentLanguage.value === 'zh' 
      ? '获取数据失败' 
      : 'Failed to fetch data')
  } finally {
    loading.value = false
  }
}

// 跳转到详情页
function goToDetail(item) {
  if (isNews.value) {
    router.push(`/news/${item.policy_id}`)
  } else {
    router.push(`/policy/${item.policy_id}`)
  }
}

// 搜索内容
function searchContent() {
  if (!searchKeyword.value.trim()) {
    showSearchResults.value = false
    return
  }
  
  const keyword = searchKeyword.value.toLowerCase()
  
  // 在标题和内容中搜索
  searchResults.value = contentList.value.filter(item => {
    const titleMatch = item.title && item.title.toLowerCase().includes(keyword)
    const contentMatch = item.content && item.content.toLowerCase().includes(keyword)
    
    return titleMatch || contentMatch
  })
  
  showSearchResults.value = true
}

// 清除搜索
function clearSearch() {
  searchKeyword.value = ''
  showSearchResults.value = false
}

// 切换排序顺序
function toggleSortOrder() {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
}

// 监听props变化，更新数据
watch([() => props.type, () => props.topicId], () => {
  fetchData()
  fetchTopicInfo()
  clearSearch()
}, { immediate: true })

onMounted(() => {
  fetchData()
  fetchTopicInfo()
})
</script>

<template>
  <div class="topic-list-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <el-button @click="router.push('/')" class="back-button" type="primary" plain>
        <el-icon><HomeFilled /></el-icon>
        {{ currentLanguage === 'zh' ? '返回首页' : 'Back to Home' }}
      </el-button>
      <h1>{{ pageTitle }}</h1>
    </div>
    
    <!-- 当前主题标题 -->
    <div class="current-topic">
      <h2>{{ topicName }}</h2>
      <div class="topic-meta">
        <el-tag type="info" effect="plain" size="large">
          {{ isNews ? 
            (currentLanguage === 'zh' ? '新闻主题' : 'News Topic') : 
            (currentLanguage === 'zh' ? '政策主题' : 'Policy Topic') 
          }}
        </el-tag>
        <span class="item-count">
          {{ sortedContentList.length }} {{ currentLanguage === 'zh' ? '项内容' : 'items' }}
        </span>
      </div>
    </div>
    
    <!-- 搜索和排序栏 -->
    <div class="filters-container">
      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          :placeholder="currentLanguage === 'zh' ? '在当前主题中搜索...' : 'Search in current topic...'"
          prefix-icon="Search"
          @keyup.enter="searchContent"
          clearable
        >
          <template #append>
            <el-button @click="searchContent" type="primary">
              {{ currentLanguage === 'zh' ? '搜索' : 'Search' }}
            </el-button>
          </template>
        </el-input>
      </div>
      
      <!-- 排序选项 -->
      <div class="sort-options">
        <span class="sort-label">{{ currentLanguage === 'zh' ? '日期排序:' : 'Date:' }}</span>
        <el-button @click="toggleSortOrder" size="default" type="info" plain class="sort-order-btn">
          <el-icon>
            <component :is="sortOrder === 'asc' ? 'SortUp' : 'SortDown'" />
          </el-icon>
          {{ sortOrder === 'asc' 
            ? (currentLanguage === 'zh' ? '从旧到新' : 'Oldest first') 
            : (currentLanguage === 'zh' ? '从新到旧' : 'Newest first') }}
        </el-button>
      </div>
    </div>
    
    <!-- 搜索结果信息 -->
    <div v-if="showSearchResults" class="search-result-info">
      <span>{{ currentLanguage === 'zh' ? `搜索结果: ${searchResults.length} 条` : `Search Results: ${searchResults.length} items` }}</span>
      <el-button size="small" text type="primary" @click="clearSearch">
        <el-icon><Close /></el-icon>
        {{ currentLanguage === 'zh' ? '清除搜索' : 'Clear Search' }}
      </el-button>
    </div>
    
    <!-- 内容加载中 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>
    
    <!-- 空数据状态 -->
    <div v-else-if="sortedContentList.length === 0" class="empty-state">
      <el-empty 
        :description="showSearchResults 
          ? (currentLanguage === 'zh' ? '没有找到匹配的结果' : 'No matching results found') 
          : (currentLanguage === 'zh' ? '暂无数据' : 'No Data Available')" 
      />
      <el-button v-if="showSearchResults" @click="clearSearch" type="primary">
        {{ currentLanguage === 'zh' ? '返回全部内容' : 'Back to All Content' }}
      </el-button>
    </div>
    
    <!-- 内容列表 -->
    <div v-else class="content-list">
      <el-card 
        v-for="item in sortedContentList" 
        :key="item.policy_id" 
        class="content-card"
        @click="goToDetail(item)"
        shadow="hover"
      >
        <div class="card-content">
          <div v-if="item.image_url" class="card-image">
            <el-image :src="item.image_url" fit="cover" />
          </div>
          <div class="card-info">
            <h3 class="title">{{ item.title }}</h3>
            <p class="summary" v-if="item.content">
              {{ item.content.slice(0, 100) }}{{ item.content.length > 100 ? '...' : '' }}
            </p>
            <div class="meta">
              <div class="meta-left">
                <el-tag size="small" type="info" effect="plain" v-if="item.date_published">
                  <el-icon><Calendar /></el-icon>
                  {{ item.date_published }}
                </el-tag>
                <el-tag size="small" type="success" effect="plain" v-if="item.unit_published">
                  <el-icon><Office /></el-icon>
                  {{ item.unit_published }}
                </el-tag>
              </div>
              <el-button size="small" text type="primary" class="read-more">
                {{ currentLanguage === 'zh' ? '阅读更多' : 'Read more' }}
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.topic-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f9fafc;
  min-height: 100vh;
}

.page-header {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  gap: 20px;
}

.back-button {
  flex-shrink: 0;
}

h1 {
  margin: 0;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
}

.current-topic {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #ebeef5;
}

.current-topic h2 {
  font-size: 32px;
  margin: 0 0 15px 0;
  color: #303133;
}

.topic-meta {
  display: flex;
  align-items: center;
  gap: 15px;
}

.item-count {
  color: #909399;
  font-size: 16px;
}

.filters-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 25px;
  background-color: #fff;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.search-bar {
  flex-grow: 1;
  min-width: 300px;
}

.sort-options {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.sort-label {
  color: #606266;
  white-space: nowrap;
  font-weight: 500;
}

.sort-order-btn {
  min-width: 140px;
}

.search-result-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #ecf5ff;
  border-radius: 8px;
  border-left: 4px solid #409eff;
}

.loading-container {
  padding: 30px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.empty-state {
  text-align: center;
  padding: 60px 0;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.content-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 25px;
}

.content-card {
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 8px;
  border: none;
  overflow: hidden;
  height: 100%;
}

.content-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
}

.card-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.card-image {
  height: 200px;
  overflow: hidden;
  margin-bottom: 15px;
  border-radius: 4px;
}

.card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.title {
  font-size: 18px;
  margin: 0 0 15px 0;
  color: #303133;
  line-height: 1.5;
  font-weight: 600;
}

.summary {
  color: #606266;
  margin-bottom: 20px;
  flex: 1;
  font-size: 14px;
  line-height: 1.8;
}

.meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.meta-left {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.read-more {
  display: flex;
  align-items: center;
  gap: 5px;
}

@media (max-width: 768px) {
  .filters-container {
    flex-direction: column;
  }
  
  .search-bar, .sort-options {
    width: 100%;
  }
  
  .content-list {
    grid-template-columns: 1fr;
  }
  
  .current-topic h2 {
    font-size: 24px;
  }
  
  h1 {
    font-size: 22px;
  }
  
  .topic-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style> 