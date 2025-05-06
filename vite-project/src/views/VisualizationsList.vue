<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useContentStore } from '../stores/content'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const contentStore = useContentStore()
const currentLanguage = computed(() => contentStore.currentLanguage)

// 数据
const visualizations = ref([])
const loading = ref(false)
const error = ref(null)
const categoryMap = {
  'News': { zh: '新闻分析', en: 'News Analysis' },
  'Official_Policy': { zh: '政策分析', en: 'Policy Analysis' },
  'Employment_Entrepreneurship': { zh: '就业创业分析', en: 'Employment & Entrepreneurship Analysis' }
}

// 可视化类型
const vizTypeMap = {
  1: { zh: '趋势图', en: 'Trend Chart' },
  2: { zh: '时间线图', en: 'Timeline' },
  3: { zh: '态度表现图', en: 'Attitude Chart' },
  4: { zh: '关键词云', en: 'Keyword Cloud' }
}

// 获取所有可视化数据
async function fetchAllVisualizations() {
  loading.value = true
  error.value = null
  
  try {
    const result = await contentStore.fetchVisualizations()
    if (result.success && Array.isArray(result.visualizations)) {
      visualizations.value = result.visualizations || []
    } else {
      error.value = result.error || (currentLanguage.value === 'zh' ? '未获取到可视化数据' : 'Failed to get visualization data')
      ElMessage.error(currentLanguage.value === 'zh' 
        ? '获取可视化数据失败' 
        : 'Failed to fetch visualization data')
    }
  } catch (err) {
    console.error('获取可视化数据错误:', err)
    error.value = err.message || '未知错误'
    ElMessage.error(currentLanguage.value === 'zh' 
      ? '获取可视化数据发生错误' 
      : 'Error occurred while fetching visualization data')
  } finally {
    loading.value = false
  }
}

// 根据类别获取可视化数据
async function fetchVisualizationsByCategory(category) {
  loading.value = true
  error.value = null
  
  try {
    const result = await contentStore.fetchVisualizationsByCategory(category)
    if (result.success && Array.isArray(result.visualizations)) {
      visualizations.value = result.visualizations || []
    } else {
      error.value = result.error || (currentLanguage.value === 'zh' ? '未获取到可视化数据' : 'Failed to get visualization data')
      ElMessage.error(currentLanguage.value === 'zh' 
        ? '获取可视化数据失败' 
        : 'Failed to fetch visualization data')
    }
  } catch (err) {
    console.error('获取可视化数据错误:', err)
    error.value = err.message || '未知错误'
    ElMessage.error(currentLanguage.value === 'zh' 
      ? '获取可视化数据发生错误' 
      : 'Error occurred while fetching visualization data')
  } finally {
    loading.value = false
  }
}

// 获取可视化详情
function goToVisualizationDetail(vizId) {
  if (vizId) {
    router.push(`/visualization-detail/${vizId}`)
  } else {
    ElMessage.warning(currentLanguage.value === 'zh' ? '可视化ID无效' : 'Invalid visualization ID')
  }
}

// 获取类别名称
function getCategoryName(category) {
  if (!category) return ''
  return currentLanguage.value === 'zh' 
    ? (categoryMap[category] ? categoryMap[category].zh : category) 
    : (categoryMap[category] ? categoryMap[category].en : category)
}

// 获取类型名称
function getTypeName(typeId) {
  if (!typeId) return ''
  return currentLanguage.value === 'zh' 
    ? (vizTypeMap[typeId] ? vizTypeMap[typeId].zh : `类型${typeId}`) 
    : (vizTypeMap[typeId] ? vizTypeMap[typeId].en : `Type ${typeId}`)
}

// 组件挂载时获取数据
onMounted(async () => {
  const category = route.query.category
  if (category) {
    await fetchVisualizationsByCategory(category)
  } else {
    await fetchAllVisualizations()
  }
})
</script>

<template>
  <div class="visualizations-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <el-button @click="router.push('/')" class="back-button">
        <el-icon><HomeFilled /></el-icon>
        {{ currentLanguage === 'zh' ? '返回首页' : 'Back to Home' }}
      </el-button>
      <h1>{{ currentLanguage === 'zh' ? '可视化数据分析中心' : 'Visualization Analysis Center' }}</h1>
    </div>
    
    <!-- 过滤器部分 -->
    <div class="filters">
      <div class="filter-label">{{ currentLanguage === 'zh' ? '数据分类:' : 'Categories:' }}</div>
      <div class="filter-buttons">
        <el-button 
          @click="fetchAllVisualizations()" 
          :type="!route.query.category ? 'primary' : 'default'"
        >
          {{ currentLanguage === 'zh' ? '全部' : 'All' }}
        </el-button>
        <el-button 
          @click="fetchVisualizationsByCategory('News')" 
          :type="route.query.category === 'News' ? 'primary' : 'default'"
        >
          {{ currentLanguage === 'zh' ? '新闻分析' : 'News Analysis' }}
        </el-button>
        <el-button 
          @click="fetchVisualizationsByCategory('Official_Policy')" 
          :type="route.query.category === 'Official_Policy' ? 'primary' : 'default'"
        >
          {{ currentLanguage === 'zh' ? '政策分析' : 'Policy Analysis' }}
        </el-button>
        <el-button 
          @click="fetchVisualizationsByCategory('Employment_Entrepreneurship')" 
          :type="route.query.category === 'Employment_Entrepreneurship' ? 'primary' : 'default'"
        >
          {{ currentLanguage === 'zh' ? '就业创业分析' : 'Employment & Entrepreneurship Analysis' }}
        </el-button>
      </div>
    </div>
    
    <!-- 内容区域 -->
    <div class="content-area" v-loading="loading">
      <!-- 错误提示 -->
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      
      <!-- 空数据提示 -->
      <div v-else-if="visualizations.length === 0" class="empty-state">
        <el-empty 
          :description="currentLanguage === 'zh' ? '暂无可视化数据' : 'No visualization data available'" 
        />
      </div>
      
      <!-- 可视化卡片列表 -->
      <div v-else class="visualization-cards">
        <el-card 
          v-for="item in visualizations" 
          :key="item.viz_id" 
          class="visualization-card"
          @click="goToVisualizationDetail(item.viz_id)"
          shadow="hover"
        >
          <!-- 图片预览区 -->
          <div class="card-image" v-if="item.image_url">
            <el-image 
              :src="item.image_url" 
              fit="cover"
              class="viz-image"
            />
          </div>
          <div class="card-image placeholder" v-else>
            <el-icon><PieChart /></el-icon>
          </div>
          
          <!-- 文本信息区 -->
          <div class="card-content">
            <h3 class="viz-title">{{ item.viz_name }}</h3>
            
            <div class="viz-meta">
              <el-tag size="small" type="info" class="category-tag">
                {{ getCategoryName(item.category) }}
              </el-tag>
              <el-tag size="small" class="type-tag">
                {{ getTypeName(item.viz_type_id) }}
              </el-tag>
            </div>
            
            <p class="viz-description" v-if="item.viz_analysis">
              {{ item.viz_analysis.slice(0, 100) }}{{ item.viz_analysis.length > 100 ? '...' : '' }}
            </p>
            
            <div class="viz-date">
              {{ currentLanguage === 'zh' ? '最后更新: ' : 'Last updated: ' }} 
              {{ item.last_updated }}
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<style scoped>
.visualizations-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
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
}

.filters {
  background-color: #f5f7fa;
  padding: 15px 20px;
  border-radius: 8px;
  margin-bottom: 30px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.filter-label {
  font-weight: 600;
  color: #606266;
  white-space: nowrap;
}

.filter-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.content-area {
  min-height: 400px;
}

.error-message {
  color: #f56c6c;
  text-align: center;
  padding: 40px 0;
  font-size: 16px;
}

.empty-state {
  padding: 60px 0;
}

.visualization-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;
}

.visualization-card {
  cursor: pointer;
  transition: all 0.3s;
  overflow: hidden;
  height: 100%;
}

.visualization-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.card-image {
  height: 200px;
  overflow: hidden;
  position: relative;
  border-radius: 8px;
  margin-bottom: 15px;
  background-color: #f5f7fa;
}

.card-image.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 64px;
  color: #dcdfe6;
}

.viz-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-content {
  padding: 5px 0;
}

.viz-title {
  margin: 0 0 12px 0;
  font-size: 18px;
  color: #303133;
  line-height: 1.4;
}

.viz-meta {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}

.viz-description {
  color: #606266;
  margin-bottom: 12px;
  line-height: 1.6;
  font-size: 14px;
}

.viz-date {
  font-size: 13px;
  color: #909399;
  margin-top: 15px;
}

@media (max-width: 768px) {
  .visualization-cards {
    grid-template-columns: 1fr;
  }
  
  .filters {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style> 