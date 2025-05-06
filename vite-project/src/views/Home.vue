<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useContentStore } from '../stores/content'
import { ElMessage } from 'element-plus'

const router = useRouter()
const contentStore = useContentStore()

const currentLanguage = computed(() => contentStore.currentLanguage)
const searchKeyword = ref('')
const searchType = ref('all')
const searchResults = ref([])
const showSearchResults = ref(false)

// 分类名称和图标
const categoryInfo = {
  0: { 
    zh: '教育咨询', 
    en: 'Education Consultation',
    icon: 'School',
    color: '#409EFF',
    bgColor: '#ECF5FF',
    vizTypeId: 1,  // 对应可视化类型ID
    category: 'News' // 对应可视化分类
  },
  1: { 
    zh: '国际合作', 
    en: 'International Cooperation',
    icon: 'Connection',
    color: '#67C23A',
    bgColor: '#F0F9EB',
    vizTypeId: 2,
    category: 'News'
  },
  2: { 
    zh: '全球化与来华留学', 
    en: 'Globalization & Study in China',
    icon: 'Place',
    color: '#E6A23C',
    bgColor: '#FDF6EC',
    vizTypeId: 3,
    category: 'News'
  },
  3: { 
    zh: '教育政策解读', 
    en: 'Education Policy Interpretation',
    icon: 'Document',
    color: '#F56C6C',
    bgColor: '#FEF0F0',
    vizTypeId: 4,
    category: 'News'
  },
  4: { 
    zh: '在华发展机遇', 
    en: 'Development Opportunities in China',
    icon: 'Opportunity',
    color: '#909399',
    bgColor: '#F4F4F5',
    vizTypeId: 1,
    category: 'Official_Policy'
  },
  5: { 
    zh: '学生服务与支持', 
    en: 'Student Services & Support',
    icon: 'Service',
    color: '#8E44AD',
    bgColor: '#F5EEF8',
    vizTypeId: 2,
    category: 'Official_Policy'
  },
  6: { 
    zh: '教育与学习', 
    en: 'Education & Learning',
    icon: 'Reading',
    color: '#3498DB',
    bgColor: '#EBF5FB',
    vizTypeId: 3,
    category: 'Official_Policy'
  },
  7: { 
    zh: '政策与建设', 
    en: 'Policy & Construction',
    icon: 'SetUp',
    color: '#27AE60',
    bgColor: '#E9F7EF',
    vizTypeId: 4,
    category: 'Official_Policy'
  },
  8: { 
    zh: '国际关系与交流', 
    en: 'International Relations & Exchange',
    icon: 'ChatLineRound',
    color: '#E74C3C',
    bgColor: '#FDEDEC',
    vizTypeId: 1,
    category: 'Employment_Entrepreneurship'
  },
  9: { 
    zh: '就业与工作', 
    en: 'Employment & Work',
    icon: 'Suitcase',
    color: '#1ABC9C',
    bgColor: '#E8F8F5',
    vizTypeId: 2,
    category: 'Employment_Entrepreneurship'
  }
}

// 轮播图数据
const carouselItems = ref([
  {
    id: 1,
    title: { zh: '来华留学新政策', en: 'New Policies for International Students' },
    image: 'https://www.zafu.edu.cn/__local/1/9D/C2/9B6348833E5EE5BD160A934DE90_9FD017E8_197EDE.jpg'
  },
  {
    id: 2,
    title: { zh: '来华留学新闻解读', en: 'International Education in Chinese Universities' },
    image: 'https://apply.studyinchina.edu.cn/upload/school/4028868472e9601a0173e70caaf201fd/20211013143516QneY1yUV.jpg?1634107394257'
  },
  {
    id: 3,
    title: { zh: '可视化洞察与分析', en: 'Sino-foreign Cooperative Education' },
    image: 'https://apply.studyinchina.edu.cn/upload/school/4028868472e9601a0173e70caaf201fd/20211013143516QneY1yUV.jpg?1634107394257'
  }
])

// 获取新闻分类
const newsByCategory = computed(() => contentStore.newsByCategory)

// 获取政策分类
const policiesByCategory = computed(() => contentStore.policiesByCategory)

// 搜索函数
async function handleSearch() {
  if (!searchKeyword.value) {
    return
  }
  
  const results = await contentStore.searchContent(searchKeyword.value, searchType.value)
  searchResults.value = results
  showSearchResults.value = true
  
  // 滚动到搜索结果
  setTimeout(() => {
    const searchResultSection = document.querySelector('.search-results')
    if (searchResultSection) {
      searchResultSection.scrollIntoView({ behavior: 'smooth' })
    }
  }, 100)
}

// 清除搜索结果
function clearSearch() {
  showSearchResults.value = false
  searchKeyword.value = ''
}

// 跳转到详情页
function goToDetail(item) {

  if (item.category === 'News') {
    router.push(`/news/${item.policy_id}`)
  } else {
    router.push(`/policy/${item.policy_id}`)
  }
}

// 跳转到可视化详情页
function goToVisualization(category) {
  const info = getCategoryInfo(category)
  
  if (category < 5) {
    // 新闻类别 (0-4)
    // 跳转到新闻分类列表页
    router.push({
      path: '/news', 
      query: { 
        topic_id: category
      }
    })
  } else {
    // 政策类别 (5-9)
    // 跳转到政策分类列表页
    router.push({
      path: '/policy', 
      query: { 
        topic_id: category
      }
    })
  }
}

// 获取分类信息
function getCategoryInfo(category) {
  return categoryInfo[category]
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

// 当语言改变时，刷新内容
watch(() => currentLanguage.value, () => {
  // 确保内容在语言切换后更新
  contentStore.fetchNews()
  contentStore.fetchPolicies()
})

onMounted(() => {
  contentStore.fetchNews()
  contentStore.fetchPolicies()
})
</script>

<template>
  <div class="home-container">
    <!-- 搜索框 -->
    <div class="search-section">
      <div class="search-container">
        <div class="search-form">
          <el-input
            v-model="searchKeyword"
            :placeholder="currentLanguage === 'zh' ? '搜索新闻和政策...' : 'Search news and policies...'"
            class="search-input"
            size="large"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon class="search-icon"><Search /></el-icon>
            </template>
          </el-input>
          <el-select v-model="searchType" class="search-type" size="large">
            <el-option value="all" :label="currentLanguage === 'zh' ? '全部' : 'All'"></el-option>
            <el-option value="news" :label="currentLanguage === 'zh' ? '新闻' : 'News'"></el-option>
            <el-option value="policy" :label="currentLanguage === 'zh' ? '政策' : 'Policy'"></el-option>
          </el-select>
          <el-button @click="handleSearch" type="primary" size="large" class="search-button">
            {{ currentLanguage === 'zh' ? '搜索' : 'Search' }}
          </el-button>
        </div>
      </div>
    </div>
    
    <!-- 轮播图部分 -->
    <div class="carousel-card">
      <div class="carousel-section">
        <el-carousel height="400px">
          <el-carousel-item v-for="item in carouselItems" :key="item.id">
            <div class="carousel-content" :style="{ backgroundImage: `url(${item.image})` }">
              <div class="carousel-text">
                <h3>{{ currentLanguage === 'zh' ? item.title.zh : item.title.en }}</h3>
              </div>
            </div>
          </el-carousel-item>
        </el-carousel>
      </div>
    </div>
    
    <!-- 搜索结果 -->
    <div v-if="showSearchResults" class="search-results section">
      <div class="search-results-header">
        <h2>
          <el-icon><Search /></el-icon>
          {{ currentLanguage === 'zh' ? '搜索结果' : 'Search Results' }}
        </h2>
        <el-button @click="clearSearch" size="small" text>
          <el-icon><Close /></el-icon>
          {{ currentLanguage === 'zh' ? '清除搜索' : 'Clear Search' }}
        </el-button>
      </div>
      
      <div v-if="searchResults.length === 0" class="empty-results">
        <el-empty :description="currentLanguage === 'zh' ? '没有找到匹配结果' : 'No matching results found'"></el-empty>
      </div>
      
      <div v-else class="results-list">
        <el-card 
          v-for="item in searchResults" 
          :key="item.id" 
          class="result-card"
          @click="goToDetail(item)"
        >
          <div class="result-header">
            <h3>{{ getTitle(item) }}</h3>
            <el-tag size="small" type="info">
              {{ item.type === 'news' 
                ? (currentLanguage === 'zh' ? '新闻' : 'News') 
                : (currentLanguage === 'zh' ? '政策' : 'Policy') }}
            </el-tag>
          </div>
          <p class="result-summary">{{ getContent(item) ? getContent(item).slice(0, 100) + '...' : '' }}</p>
          <div class="result-meta">
            <span>{{ item.created_at }}</span>
          </div>
        </el-card>
      </div>
    </div>
    
    <!-- 新闻部分 -->
    <div class="content-card news-section">
      <h2>
        <el-icon><Promotion /></el-icon>
        {{ currentLanguage === 'zh' ? '最新新闻' : 'Latest News' }}
      </h2>
      
      <div class="category-cards">
        <div 
          v-for="category in [0, 1, 2, 3, 4]" 
          :key="`news-${category}`" 
          class="category-card"
          @click="goToVisualization(category)"
          :style="{ '--card-color': categoryInfo[category].color }"
        >
          <div class="card-icon" v-bind:style="{ backgroundColor: categoryInfo[category].bgColor }">
            <el-icon v-bind:style="{ color: categoryInfo[category].color, fontSize: '36px' }">
              <component :is="categoryInfo[category].icon"></component>
            </el-icon>
          </div>
          <div class="card-title" v-bind:style="{ color: categoryInfo[category].color }">
            {{ currentLanguage === 'zh' ? categoryInfo[category].zh : categoryInfo[category].en }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- 政策部分 -->
    <div class="content-card policy-section">
      <h2>
        <el-icon><DocumentChecked /></el-icon>
        {{ currentLanguage === 'zh' ? '政策解读' : 'Policy Interpretation' }}
      </h2>
      
      <div class="category-cards">
        <div 
          v-for="category in [5, 6, 7, 8, 9]" 
          :key="`policy-${category}`" 
          class="category-card"
          @click="goToVisualization(category)"
          :style="{ '--card-color': categoryInfo[category].color }"
        >
          <div class="card-icon" v-bind:style="{ backgroundColor: categoryInfo[category].bgColor }">
            <el-icon v-bind:style="{ color: categoryInfo[category].color, fontSize: '36px' }">
              <component :is="categoryInfo[category].icon"></component>
            </el-icon>
          </div>
          <div class="card-title" v-bind:style="{ color: categoryInfo[category].color }">
            {{ currentLanguage === 'zh' ? categoryInfo[category].zh : categoryInfo[category].en }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- 可视化分析部分 -->
    <div class="content-card visualization-section">
      <h2>
        <el-icon><PieChart /></el-icon>
        {{ currentLanguage === 'zh' ? '可视化与洞察分析' : 'Visualization & Insight Analysis' }}
        <span class="view-more" @click="router.push('/visualizations')">
          {{ currentLanguage === 'zh' ? '查看全部 >' : 'View all >' }}
        </span>
      </h2>
      
      <div class="vis-cards">
        <!-- 政策可视化 -->
        <div class="vis-card" @click="router.push('/visualizations?category=Official_Policy')">
          <div class="vis-icon">
            <el-icon><Document /></el-icon>
          </div>
          <div class="vis-content">
            <h3>{{ currentLanguage === 'zh' ? '政策可视化' : 'Policy Visualization' }}</h3>
            <p>{{ currentLanguage === 'zh' ? '留学生活、文化交流、国际视角等' : 'Student life, cultural exchange, international perspective, etc.' }}</p>
          </div>
        </div>
        
        <!-- 新闻可视化 -->
        <div class="vis-card" @click="router.push('/visualizations?category=News')">
          <div class="vis-icon">
            <el-icon><Promotion /></el-icon>
          </div>
          <div class="vis-content">
            <h3>{{ currentLanguage === 'zh' ? '新闻可视化' : 'News Visualization' }}</h3>
            <p>{{ currentLanguage === 'zh' ? '留学生活、文化交流、国际视角等' : 'Student life, cultural exchange, international perspective, etc.' }}</p>
          </div>
        </div>
        
        <!-- 就业创业可视化 -->
        <div class="vis-card" @click="router.push('/visualizations?category=Employment_Entrepreneurship')">
          <div class="vis-icon">
            <el-icon><Suitcase /></el-icon>
          </div>
          <div class="vis-content">
            <h3>{{ currentLanguage === 'zh' ? '就业创业可视化' : 'Employment & Entrepreneurship Visualization' }}</h3>
            <p>{{ currentLanguage === 'zh' ? '留学生活、文化交流、国际视角等' : 'Student life, cultural exchange, international perspective, etc.' }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 30px;
  background-color: #f5f7fa;
}

.search-section {
  margin-bottom: 10px;
}

.search-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  background-color: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

.search-form {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-input {
  flex-grow: 1;
  border-radius: 8px;
}

.search-icon {
  font-size: 18px;
  color: #409EFF;
}

.search-type {
  width: 120px;
  flex-shrink: 0;
}

.search-button {
  flex-shrink: 0;
  min-width: 80px;
}

.carousel-card, .content-card, .search-results {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
  padding: 25px;
  margin-bottom: 0;
}

.carousel-card {
  padding: 0;
  overflow: hidden;
}

.content-card h2 {
  margin-top: 0;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 2px solid #409EFF;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 24px;
  position: relative;
}

.content-card h2::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100px;
  height: 4px;
  background-color: #409EFF;
  border-radius: 2px;
}

.category-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 25px;
}

.category-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  border-radius: 12px;
  transition: all 0.3s ease;
  text-align: center;
  cursor: pointer;
  padding: 25px 15px;
  background-color: #fff;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
  border: 1px solid #ebeef5;
  position: relative;
  overflow: hidden;
}

.category-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background-color: var(--card-color, #409EFF);
  transform: scaleX(0);
  transition: transform 0.3s ease;
  transform-origin: left;
}

.category-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 20px rgba(0, 0, 0, 0.12);
}

.category-card:hover::before {
  transform: scaleX(1);
}

.card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 90px;
  height: 90px;
  border-radius: 50%;
  margin-bottom: 20px;
  transition: transform 0.3s;
}

.category-card:hover .card-icon {
  transform: scale(1.1);
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  transition: color 0.3s;
}

.category-card:hover .card-title {
  color: var(--card-color, #409EFF) !important;
}

/* 轮播图样式 */
.carousel-section {
  border-radius: 12px;
  overflow: hidden;
}

.carousel-content {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  position: relative;
}

.carousel-text {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  color: white;
}

.carousel-text h3 {
  margin: 0;
  font-size: 24px;
}

/* 搜索结果样式 */
.search-results {
  background-color: white;
}

.search-results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-results-header h2 {
  margin: 0;
  color: #303133;
  font-size: 22px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.results-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;
  margin-top: 20px;
}

.result-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 10px;
  overflow: hidden;
  border: none;
  height: 100%;
}

.result-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.result-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  flex: 1;
  margin-right: 15px;
  line-height: 1.4;
}

.result-summary {
  color: #606266;
  margin-bottom: 15px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.6;
  font-size: 14px;
}

.result-meta {
  font-size: 13px;
  color: #909399;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.empty-results {
  padding: 60px 0;
  text-align: center;
}

@media (max-width: 768px) {
  .category-cards {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  }
  
  .card-icon {
    width: 70px;
    height: 70px;
  }
  
  .content-card, .search-results {
    padding: 15px;
  }
}

/* 可视化分析卡片样式 */
.visualization-section h2 {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.view-more {
  font-size: 14px;
  color: #409EFF;
  cursor: pointer;
  font-weight: normal;
}

.vis-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
  gap: 20px;
}

.vis-card {
  display: flex;
  align-items: center;
  padding: 20px;
  border-radius: 10px;
  background-color: #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #ebeef5;
}

.vis-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
}

.vis-icon {
  width: 60px;
  height: 60px;
  background-color: #ecf5ff;
  color: #409EFF;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  margin-right: 15px;
  font-size: 24px;
}

.vis-card:nth-child(1) .vis-icon {
  background-color: #ecf5ff;
  color: #409EFF;
}

.vis-card:nth-child(2) .vis-icon {
  background-color: #f0f9eb;
  color: #67c23a;
}

.vis-card:nth-child(3) .vis-icon {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.vis-content h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #303133;
}

.vis-content p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

@media (max-width: 768px) {
  .category-cards {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  }
  
  .card-icon {
    width: 70px;
    height: 70px;
  }
  
  .content-card, .search-results {
    padding: 15px;
  }
  
  .vis-cards {
    grid-template-columns: 1fr;
  }
}
</style> 