<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useContentStore } from '../stores/content'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const contentStore = useContentStore()
const currentLanguage = computed(() => contentStore.currentLanguage)

// 获取可视化ID
const vizId = computed(() => route.params.id)

// 数据
const visualization = ref(null)
const loading = ref(false)
const error = ref(null)

// 类别映射
const categoryMap = {
  'News': { zh: '新闻分析', en: 'News Analysis' },
  'Official_Policy': { zh: '政策分析', en: 'Policy Analysis' },
  'Employment_Entrepreneurship': { zh: '就业创业分析', en: 'Employment & Entrepreneurship Analysis' }
}

// 可视化类型映射
const vizTypeMap = {
  1: { zh: '趋势图', en: 'Trend Chart' },
  2: { zh: '时间线图', en: 'Timeline' },
  3: { zh: '态度表现图', en: 'Attitude Chart' },
  4: { zh: '关键词云', en: 'Keyword Cloud' }
}

// 获取可视化详情
async function fetchVisualizationDetail() {
  if (!vizId.value) return
  
  loading.value = true
  error.value = null
  
  try {
    const result = await contentStore.fetchVisualizationById(vizId.value)
    if (result.success && result.visualization) {
      visualization.value = result.visualization
    } else {
      error.value = result.error || (currentLanguage.value === 'zh' ? '未找到可视化数据' : 'Visualization not found')
      ElMessage.error(currentLanguage.value === 'zh' 
        ? '获取可视化详情失败' 
        : 'Failed to fetch visualization detail')
    }
  } catch (err) {
    console.error('获取可视化详情错误:', err)
    error.value = err.message || '未知错误'
    ElMessage.error(currentLanguage.value === 'zh' 
      ? '获取可视化详情发生错误' 
      : 'Error occurred while fetching visualization detail')
  } finally {
    loading.value = false
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

// 返回列表页
function goBackToList() {
  router.push('/visualizations')
}

// 组件挂载时获取数据
onMounted(() => {
  fetchVisualizationDetail()
})
</script>

<template>
  <div class="visualization-detail-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <el-button @click="goBackToList" class="back-button">
        <el-icon><Back /></el-icon>
        {{ currentLanguage === 'zh' ? '返回列表' : 'Back to List' }}
      </el-button>
      <h1>{{ currentLanguage === 'zh' ? '可视化详情' : 'Visualization Detail' }}</h1>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>
    
    <!-- 错误提示 -->
    <div v-else-if="error" class="error-message">
      <el-alert
        :title="currentLanguage === 'zh' ? '加载失败' : 'Loading Failed'"
        :description="error"
        type="error"
        :closable="false"
        show-icon
      />
      <div class="error-actions">
        <el-button @click="fetchVisualizationDetail">
          {{ currentLanguage === 'zh' ? '重试' : 'Retry' }}
        </el-button>
        <el-button @click="goBackToList">
          {{ currentLanguage === 'zh' ? '返回列表' : 'Back to List' }}
        </el-button>
      </div>
    </div>
    
    <!-- 可视化数据不存在 -->
    <div v-else-if="!visualization" class="not-found">
      <el-empty :description="currentLanguage === 'zh' ? '可视化数据不存在' : 'Visualization not found'">
        <template #extra>
          <el-button @click="goBackToList">
            {{ currentLanguage === 'zh' ? '返回列表' : 'Back to List' }}
          </el-button>
        </template>
      </el-empty>
    </div>
    
    <!-- 可视化详情内容 -->
    <div v-else class="visualization-content">
      <el-card class="detail-card">
        <template #header>
          <div class="card-header">
            <h2>{{ visualization.viz_name }}</h2>
            <div class="meta-tags">
              <el-tag size="medium" type="info" effect="plain">
                {{ getCategoryName(visualization.category) }}
              </el-tag>
              <el-tag size="medium" type="success" effect="plain">
                {{ getTypeName(visualization.viz_type_id) }}
              </el-tag>
            </div>
          </div>
        </template>
        
        <!-- 可视化图片 -->
        <div class="visualization-image" v-if="visualization.image_url">
          <el-image 
            :src="visualization.image_url" 
            fit="contain" 
            class="main-image"
            :preview-src-list="[visualization.image_url]"
          />
        </div>
        <div class="no-image-placeholder" v-else>
          <el-icon><PieChart /></el-icon>
          <p>{{ currentLanguage === 'zh' ? '暂无图片' : 'No image available' }}</p>
        </div>
        
        <!-- 可视化分析 -->
        <div v-if="visualization.viz_analysis" class="visualization-analysis">
          <h3>{{ currentLanguage === 'zh' ? '数据分析' : 'Data Analysis' }}</h3>
          <p>{{ visualization.viz_analysis }}</p>
        </div>
        
        <!-- 更新时间 -->
        <div class="update-info">
          {{ currentLanguage === 'zh' ? '最后更新: ' : 'Last updated: ' }} 
          {{ visualization.last_updated }}
        </div>
      </el-card>
      
      <!-- 相关建议部分 -->
      <div class="related-section">
        <h3>{{ currentLanguage === 'zh' ? '相关建议' : 'Related Suggestions' }}</h3>
        <div class="related-content">
          <p>{{ currentLanguage === 'zh' 
            ? '根据该数据分析，我们建议您查看相关的新闻和政策信息，以获取更全面的了解。' 
            : 'Based on this data analysis, we recommend checking related news and policies for a more comprehensive understanding.' }}
          </p>
          
          <div class="action-buttons">
            <el-button @click="router.push('/')">
              {{ currentLanguage === 'zh' ? '浏览最新新闻' : 'Browse Latest News' }}
            </el-button>
            <el-button @click="router.push('/visualizations')">
              {{ currentLanguage === 'zh' ? '查看更多可视化' : 'View More Visualizations' }}
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.visualization-detail-container {
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

.loading-container, .error-message, .not-found {
  padding: 40px 0;
  text-align: center;
}

.error-actions {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 15px;
}

.visualization-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.detail-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.card-header h2 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  line-height: 1.4;
}

.meta-tags {
  display: flex;
  gap: 10px;
}

.visualization-image {
  margin: 20px 0;
  border-radius: 8px;
  overflow: hidden;
  text-align: center;
}

.main-image {
  max-width: 100%;
  max-height: 600px;
}

.no-image-placeholder {
  height: 300px;
  background-color: #f5f7fa;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
  margin: 20px 0;
}

.no-image-placeholder .el-icon {
  font-size: 64px;
  margin-bottom: 15px;
}

.visualization-analysis {
  margin: 20px 0;
}

.visualization-analysis h3 {
  color: #303133;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
  font-size: 20px;
}

.visualization-analysis p {
  line-height: 1.8;
  color: #606266;
  white-space: pre-line;
}

.update-info {
  margin-top: 30px;
  font-size: 14px;
  color: #909399;
  text-align: right;
}

.related-section {
  background-color: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
}

.related-section h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #303133;
  font-size: 20px;
}

.related-content p {
  line-height: 1.6;
  color: #606266;
  margin-bottom: 20px;
}

.action-buttons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .meta-tags {
    flex-wrap: wrap;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style> 