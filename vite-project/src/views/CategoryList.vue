<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useContentStore } from '../stores/content'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const contentStore = useContentStore()

const currentLanguage = computed(() => contentStore.currentLanguage)

// 从路由参数中获取类型和类别
const contentType = computed(() => route.query.type || 'news')
const categoryId = computed(() => Number(route.query.category || 0))

// 数据状态
const loading = ref(false)
const contentList = ref([])
const searchKeyword = ref('')
const searchResults = ref([])
const showSearchResults = ref(false)

// 分类名称映射
const categoryNames = {
  0: { zh: '教育咨询', en: 'Education Consultation' },
  1: { zh: '国际合作', en: 'International Cooperation' },
  2: { zh: '全球化与来华留学', en: 'Globalization & Study in China' },
  3: { zh: '教育政策解读', en: 'Education Policy Interpretation' },
  4: { zh: '在华发展机遇', en: 'Development Opportunities in China' },
  5: { zh: '学生服务与支持', en: 'Student Services & Support' },
  6: { zh: '教育与学习', en: 'Education & Learning' },
  7: { zh: '政策与建设', en: 'Policy & Construction' },
  8: { zh: '国际关系与交流', en: 'International Relations & Exchange' },
  9: { zh: '就业与工作', en: 'Employment & Work' }
}

// 是否是新闻类型
const isNews = computed(() => contentType.value === 'news')

// 获取当前分类名称
const currentCategoryName = computed(() => {
  const category = categoryNames[categoryId.value]
  return category ? (currentLanguage.value === 'zh' ? category.zh : category.en) : categoryId.value
})

// 获取页面标题
const pageTitle = computed(() => {
  if (isNews.value) {
    return currentLanguage.value === 'zh' ? '新闻中心' : 'News Center'
  } else {
    return currentLanguage.value === 'zh' ? '政策中心' : 'Policy Center'
  }
})

// 获取数据
async function fetchData() {
  loading.value = true
  
  try {
    if (isNews.value) {
      // 获取新闻数据
      if (!contentStore.news || contentStore.news.length === 0) {
        await contentStore.fetchNews()
      }
      
      // 过滤出当前类别的新闻
      contentList.value = contentStore.news.filter(item => item.category === categoryId.value)
    } else {
      // 获取政策数据
      if (!contentStore.policies || contentStore.policies.length === 0) {
        await contentStore.fetchPolicies()
      }
      
      // 过滤出当前类别的政策
      contentList.value = contentStore.policies.filter(item => item.category === categoryId.value)
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
    router.push(`/news/${item.id}`)
  } else {
    router.push(`/policy/${item.id}`)
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
    const titleEnMatch = item.title_en && item.title_en.toLowerCase().includes(keyword)
    const contentEnMatch = item.content_en && item.content_en.toLowerCase().includes(keyword)
    
    return titleMatch || contentMatch || titleEnMatch || contentEnMatch
  })
  
  showSearchResults.value = true
}

// 清除搜索
function clearSearch() {
  searchKeyword.value = ''
  showSearchResults.value = false
}

// 切换分类
function switchCategory(category) {
  router.push({
    path: '/visualization',
    query: {
      type: contentType.value,
      category: category
    }
  })
}

// 获取标题（根据当前语言）
function getTitle(item) {
  if (currentLanguage.value === 'en' && item.title_en) {
    return item.title_en
  }
  return item.title
}

// 获取内容（根据当前语言）
function getContent(item) {
  if (currentLanguage.value === 'en' && item.content_en) {
    return item.content_en
  }
  return item.content
}

// 监听路由变化，更新数据
watch([contentType, categoryId], () => {
  fetchData()
  clearSearch()
}, { immediate: true })

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="category-list-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <el-button @click="router.push('/')" class="back-button">
        <el-icon><HomeFilled /></el-icon>
        {{ currentLanguage === 'zh' ? '返回首页' : 'Back to Home' }}
      </el-button>
      <h1>{{ pageTitle }}</h1>
    </div>
    
    <!-- 当前分类标题 -->
    <div class="current-category">
      <h2>{{ currentCategoryName }}</h2>
    </div>
    
    <!-- 分类标签导航栏 -->
    <div class="category-tabs">
      <div v-if="isNews" class="tab-group">
        <div class="tabs">
          <div 
            v-for="category in [0, 1, 2, 3, 4]" 
            :key="`news-${category}`"
            class="tab-item"
            :class="{ active: categoryId === category }"
            @click="switchCategory(category)"
          >
            {{ currentLanguage === 'zh' ? categoryNames[category].zh : categoryNames[category].en }}
          </div>
        </div>
      </div>
      
      <div v-else class="tab-group">
        <div class="tabs">
          <div 
            v-for="category in [5, 6, 7, 8, 9]" 
            :key="`policy-${category}`"
            class="tab-item"
            :class="{ active: categoryId === category }"
            @click="switchCategory(category)"
          >
            {{ currentLanguage === 'zh' ? categoryNames[category].zh : categoryNames[category].en }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="searchKeyword"
        :placeholder="currentLanguage === 'zh' ? '在当前分类中搜索...' : 'Search in current category...'"
        prefix-icon="Search"
        @keyup.enter="searchContent"
        clearable
      >
        <template #append>
          <el-button @click="searchContent">
            {{ currentLanguage === 'zh' ? '搜索' : 'Search' }}
          </el-button>
        </template>
      </el-input>
    </div>
    
    <!-- 搜索结果信息 -->
    <div v-if="showSearchResults" class="search-result-info">
      <span>{{ currentLanguage === 'zh' ? `搜索结果: ${searchResults.length} 条` : `Search Results: ${searchResults.length} items` }}</span>
      <el-button size="small" text @click="clearSearch">
        {{ currentLanguage === 'zh' ? '清除搜索' : 'Clear Search' }}
      </el-button>
    </div>
    
    <!-- 内容加载中 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>
    
    <!-- 空数据状态 -->
    <div v-else-if="(showSearchResults ? searchResults : contentList).length === 0" class="empty-state">
      <el-empty 
        :description="showSearchResults 
          ? (currentLanguage === 'zh' ? '没有找到匹配的结果' : 'No matching results found') 
          : (currentLanguage === 'zh' ? '暂无数据' : 'No Data Available')" 
      />
      <el-button v-if="showSearchResults" @click="clearSearch">
        {{ currentLanguage === 'zh' ? '返回全部内容' : 'Back to All Content' }}
      </el-button>
    </div>
    
    <!-- 内容列表 -->
    <div v-else class="content-list">
      <el-card 
        v-for="item in (showSearchResults ? searchResults : contentList)" 
        :key="item.id" 
        class="content-card"
        @click="goToDetail(item)"
      >
        <div class="card-content">
          <div v-if="item.image_url" class="card-image">
            <el-image :src="item.image_url" fit="cover" />
          </div>
          <div class="card-info">
            <h3 class="title">{{ getTitle(item) }}</h3>
            <p class="summary" v-if="item.content">
              {{ getContent(item).slice(0, 100) }}{{ getContent(item).length > 100 ? '...' : '' }}
            </p>
            <div class="meta">
              <span class="date">{{ item.created_at }}</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.category-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  gap: 20px;
}

.back-button {
  flex-shrink: 0;
}

h1 {
  margin: 0;
  color: #303133;
  font-size: 24px;
}

.current-category {
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f2f5;
}

.current-category h2 {
  font-size: 28px;
  margin: 0;
  color: #303133;
}

.category-tabs {
  margin-bottom: 20px;
  overflow-x: auto;
}

.tab-group {
  margin-bottom: 10px;
}

.tabs {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.tab-item {
  cursor: pointer;
  padding: 8px 16px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  transition: all 0.3s;
  white-space: nowrap;
}

.tab-item:hover {
  color: #409eff;
  border-color: #c6e2ff;
  background-color: #ecf5ff;
}

.tab-item.active {
  background-color: #409eff;
  color: #fff;
  border-color: #409eff;
}

.search-bar {
  margin-bottom: 20px;
}

.search-result-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 10px 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  color: #606266;
}

.loading-container, .empty-state {
  padding: 40px 0;
  text-align: center;
}

.content-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.content-card {
  cursor: pointer;
  transition: all 0.3s;
}

.content-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.card-content {
  display: flex;
  gap: 20px;
}

.card-image {
  width: 180px;
  height: 120px;
  flex-shrink: 0;
  overflow: hidden;
  border-radius: 4px;
}

.card-image .el-image {
  width: 100%;
  height: 100%;
}

.card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.title {
  margin-top: 0;
  margin-bottom: 10px;
  color: #303133;
  font-size: 18px;
}

.summary {
  color: #606266;
  margin-bottom: 10px;
  line-height: 1.5;
  flex: 1;
}

.meta {
  color: #909399;
  font-size: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

@media (max-width: 768px) {
  .tabs {
    flex-wrap: nowrap;
    overflow-x: auto;
    padding-bottom: 5px;
  }
  
  .category-tabs {
    margin-left: -20px;
    margin-right: -20px;
    padding: 0 20px;
  }
  
  .tab-item {
    padding: 6px 12px;
    font-size: 14px;
  }
  
  .current-category h2 {
    font-size: 24px;
  }
  
  .card-content {
    flex-direction: column;
  }
  
  .card-image {
    width: 100%;
    height: 180px;
    margin-bottom: 15px;
  }
  
  .title {
    font-size: 16px;
  }
  
  .summary {
    font-size: 14px;
  }
}
</style> 