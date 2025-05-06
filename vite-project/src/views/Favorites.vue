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
const activeTab = ref('news')

// 收藏的新闻和政策
const newsFavorites = computed(() => userStore.getFavoritesByType('news'))
const policyFavorites = computed(() => userStore.getFavoritesByType('policy'))

// 清空所有收藏
async function clearAllFavorites() {
  try {
    await ElMessageBox.confirm(
      currentLanguage.value === 'zh' 
        ? '确定要清空所有收藏吗？此操作不可恢复。' 
        : 'Are you sure to clear all favorites? This cannot be undone.',
      currentLanguage.value === 'zh' ? '警告' : 'Warning',
      {
        confirmButtonText: currentLanguage.value === 'zh' ? '确定' : 'Confirm',
        cancelButtonText: currentLanguage.value === 'zh' ? '取消' : 'Cancel',
        type: 'warning'
      }
    )
    
    userStore.clearFavorites()
    ElMessage.success(
      currentLanguage.value === 'zh' 
        ? '已清空所有收藏' 
        : 'All favorites have been cleared'
    )
  } catch (error) {
    // 用户取消操作，不做处理
  }
}

// 移除单个收藏
function removeFavorite(type, id) {
  userStore.removeFavorite(type, id)
  ElMessage.success(
    currentLanguage.value === 'zh' 
      ? '已从收藏中移除' 
      : 'Removed from favorites'
  )
}

// 查看详情
function viewDetail(type, id) {
  if (type === 'news') {
    router.push(`/news/${id}`)
  } else {
    router.push(`/policy/${id}`)
  }
}

// 获取标题（根据当前语言）
function getTitle(item) {
  if (currentLanguage.value === 'en' && item.title_en) {
    return item.title_en
  }
  return item.title
}

// 格式化日期
function formatDate(dateStr) {
  if (!dateStr) return ''
  
  const date = new Date(dateStr)
  return date.toLocaleDateString(
    currentLanguage.value === 'zh' ? 'zh-CN' : 'en-US',
    { year: 'numeric', month: 'long', day: 'numeric' }
  )
}

onMounted(() => {
  // 页面加载时确保已获取新闻和政策数据
  if (contentStore.news.length === 0) {
    contentStore.fetchNews()
  }
  
  if (contentStore.policies.length === 0) {
    contentStore.fetchPolicies()
  }
})
</script>

<template>
  <div class="favorites-container">
    <div class="page-header">
      <h1>{{ currentLanguage === 'zh' ? '我的收藏' : 'My Favorites' }}</h1>
      
      <div class="header-actions">
        <el-button @click="router.push('/')" plain>
          {{ currentLanguage === 'zh' ? '返回首页' : 'Back to Home' }}
        </el-button>
        
        <el-button 
          type="danger" 
          @click="clearAllFavorites"
          :disabled="newsFavorites.length === 0 && policyFavorites.length === 0"
        >
          {{ currentLanguage === 'zh' ? '清空所有收藏' : 'Clear All Favorites' }}
        </el-button>
      </div>
    </div>
    
    <el-tabs v-model="activeTab">
      <el-tab-pane :label="currentLanguage === 'zh' ? `新闻 (${newsFavorites.length})` : `News (${newsFavorites.length})`" name="news">
        <el-empty 
          v-if="newsFavorites.length === 0" 
          :description="currentLanguage === 'zh' ? '暂无收藏的新闻' : 'No favorited news yet'" 
        />
        
        <div v-else class="favorites-list">
          <el-card 
            v-for="favorite in newsFavorites" 
            :key="`news-${favorite.id}`" 
            class="favorite-card"
          >
            <div class="card-content">
              <div v-if="favorite.item && favorite.item.image_url" class="card-image">
                <el-image :src="favorite.item.image_url" fit="cover" />
              </div>
              
              <div class="card-info">
                <h3 class="title" @click="viewDetail('news', favorite.id)">
                  {{ favorite.item ? getTitle(favorite.item) : 'Unknown Title' }}
                </h3>
                
                <div class="meta">
                  <span class="date">
                    {{ currentLanguage === 'zh' ? '收藏于: ' : 'Favorited on: ' }}
                    {{ formatDate(favorite.addedAt) }}
                  </span>
                </div>
                
                <div class="actions">
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="viewDetail('news', favorite.id)"
                  >
                    {{ currentLanguage === 'zh' ? '查看详情' : 'View Details' }}
                  </el-button>
                  
                  <el-button 
                    type="danger" 
                    size="small" 
                    @click="removeFavorite('news', favorite.id)"
                  >
                    {{ currentLanguage === 'zh' ? '取消收藏' : 'Remove' }}
                  </el-button>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </el-tab-pane>
      
      <el-tab-pane :label="currentLanguage === 'zh' ? `政策 (${policyFavorites.length})` : `Policies (${policyFavorites.length})`" name="policy">
        <el-empty 
          v-if="policyFavorites.length === 0" 
          :description="currentLanguage === 'zh' ? '暂无收藏的政策' : 'No favorited policies yet'" 
        />
        
        <div v-else class="favorites-list">
          <el-card 
            v-for="favorite in policyFavorites" 
            :key="`policy-${favorite.id}`" 
            class="favorite-card"
          >
            <div class="card-content">
              <div v-if="favorite.item && favorite.item.image_url" class="card-image">
                <el-image :src="favorite.item.image_url" fit="cover" />
              </div>
              
              <div class="card-info">
                <h3 class="title" @click="viewDetail('policy', favorite.id)">
                  {{ favorite.item ? getTitle(favorite.item) : 'Unknown Title' }}
                </h3>
                
                <div class="meta">
                  <span class="date">
                    {{ currentLanguage === 'zh' ? '收藏于: ' : 'Favorited on: ' }}
                    {{ formatDate(favorite.addedAt) }}
                  </span>
                </div>
                
                <div class="actions">
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="viewDetail('policy', favorite.id)"
                  >
                    {{ currentLanguage === 'zh' ? '查看详情' : 'View Details' }}
                  </el-button>
                  
                  <el-button 
                    type="danger" 
                    size="small" 
                    @click="removeFavorite('policy', favorite.id)"
                  >
                    {{ currentLanguage === 'zh' ? '取消收藏' : 'Remove' }}
                  </el-button>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<style scoped>
.favorites-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0;
  color: #303133;
  font-size: 28px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.favorites-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 20px;
}

.favorite-card {
  transition: transform 0.3s;
}

.favorite-card:hover {
  transform: translateY(-5px);
}

.card-content {
  display: flex;
  gap: 20px;
}

.card-image {
  width: 120px;
  height: 120px;
  flex-shrink: 0;
  border-radius: 6px;
  overflow: hidden;
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
  font-size: 18px;
  margin: 0 0 10px 0;
  cursor: pointer;
  color: #409EFF;
}

.title:hover {
  text-decoration: underline;
}

.meta {
  color: #909399;
  font-size: 14px;
  margin-bottom: 15px;
}

.actions {
  margin-top: auto;
  display: flex;
  gap: 10px;
}
</style> 