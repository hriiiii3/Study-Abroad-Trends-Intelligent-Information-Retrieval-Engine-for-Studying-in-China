import { defineStore } from 'pinia'
import axios from 'axios'

export const useContentStore = defineStore('content', {
  state: () => ({
    news: [],
    policies: [],
    searchResults: [],
    loading: false,
    error: null,
    currentLanguage: localStorage.getItem('language') || 'zh' // zh表示中文，en表示英文
  }),
  
  getters: {
    newsByCategory: (state) => {
      const result = {}
      for (let i = 0; i < 5; i++) {
        result[i] = state.news.filter(news => news.category === i)
      }
      return result
    },
    
    policiesByCategory: (state) => {
      const result = {}
      for (let i = 5; i < 10; i++) {
        result[i] = state.policies.filter(policy => policy.category === i)
      }
      return result
    },
    
    newsByTopicId: (state) => (topicId) => {
      return state.news.filter(news => news.topic_id === Number(topicId))
    },
    
    policiesByTopicId: (state) => (topicId) => {
      return state.policies.filter(policy => policy.topic_id === Number(topicId))
    },
    
    getNewsById: (state) => (id) => {
      return state.news.find(n => n.policy_id === parseInt(id))
    },
    
    getPolicyById: (state) => (id) => {
      return state.policies.find(p => p.policy_id === parseInt(id))
    }
  },
  
  actions: {
    setLanguage(lang) {
      this.currentLanguage = lang
      localStorage.setItem('language', lang)
    },
    
    async fetchNews() {
      this.loading = true
      this.error = null
      
      try {
        console.log('正在获取新闻数据...')
        const response = await axios.get('/api/news')
        console.log('获取新闻数据成功:', response.data)
        this.news = response.data.news
        return this.news
      } catch (error) {
        console.error('获取新闻数据失败:', error)
        this.error = '获取新闻失败'
        // 不再生成模拟数据
        return []
      } finally {
        this.loading = false
      }
    },
    
    async fetchPolicies() {
      this.loading = true
      this.error = null
      
      try {
        console.log('正在获取政策数据...')
        const response = await axios.get('/api/policies')
        console.log('获取政策数据成功:', response.data)
        this.policies = response.data.policies
        return this.policies
      } catch (error) {
        console.error('获取政策数据失败:', error)
        this.error = '获取政策失败'
        // 不再生成模拟数据
        return []
      } finally {
        this.loading = false
      }
    },
    
    async searchContent(keyword, type = 'all') {
      this.loading = true
      this.error = null
      this.searchResults = []
      
      try {
        const response = await axios.get(`/api/search?keyword=${keyword}&type=${type}`)
        this.searchResults = response.data.results
        return response.data.results
      } catch (error) {
        this.error = '搜索失败'
        console.error(error)
        return []
      } finally {
        this.loading = false
      }
    },
    
    async addNews(newsData) {
      this.loading = true
      this.error = null
      
      try {
        // 确保数据格式正确
        const data = {
          title: newsData.title,
          content: newsData.content,
          source_name: newsData.source_name || '',
          source_url: newsData.source_url || '',
          image_url: newsData.image_url || '',
          topic_id: newsData.topic_id || 0,
          unit_published: newsData.unit_published || '',
          date_published: newsData.date_published || ''
        }
        
        const response = await axios.post('/api/news', data)
        this.news.unshift(response.data.news)
        return { success: true, news: response.data.news }
      } catch (error) {
        this.error = error.response ? error.response.data.error : '添加新闻失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    async addPolicy(policyData) {
      this.loading = true
      this.error = null
      
      try {
        // 确保数据格式正确
        const data = {
          title: policyData.title,
          content: policyData.content,
          source_name: policyData.source_name || '',
          source_url: policyData.source_url || '',
          image_url: policyData.image_url || '',
          topic_id: policyData.topic_id || 7,
          unit_published: policyData.unit_published || '',
          date_published: policyData.date_published || ''
        }
        
        const response = await axios.post('/api/policies', data)
        this.policies.unshift(response.data.policy)
        return { success: true, policy: response.data.policy }
      } catch (error) {
        this.error = error.response ? error.response.data.error : '添加政策失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // 编辑新闻
    async updateNews(newsId, newsData) {
      this.loading = true
      this.error = null
      
      try {
        // 确保数据格式正确
        const data = {
          title: newsData.title,
          content: newsData.content,
          source_name: newsData.source_name || '',
          source_url: newsData.source_url || '',
          image_url: newsData.image_url || '',
          topic_id: newsData.topic_id || 0,
          unit_published: newsData.unit_published || '',
          date_published: newsData.date_published || ''
        }
        
        const response = await axios.put(`/api/news/${newsId}`, data)
        
        // 更新本地新闻列表
        const index = this.news.findIndex(n => n.policy_id === newsId)
        if (index !== -1) {
          this.news[index] = response.data.news
        }
        
        return { success: true, news: response.data.news }
      } catch (error) {
        this.error = error.response ? error.response.data.error : '更新新闻失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // 编辑政策
    async updatePolicy(policyId, policyData) {
      this.loading = true
      this.error = null
      
      try {
        // 确保数据格式正确
        const data = {
          title: policyData.title,
          content: policyData.content,
          source_name: policyData.source_name || '',
          source_url: policyData.source_url || '',
          image_url: policyData.image_url || '',
          topic_id: policyData.topic_id || 7,
          unit_published: policyData.unit_published || '',
          date_published: policyData.date_published || ''
        }
        
        const response = await axios.put(`/api/policies/${policyId}`, data)
        
        // 更新本地政策列表
        const index = this.policies.findIndex(p => p.policy_id === policyId)
        if (index !== -1) {
          this.policies[index] = response.data.policy
        }
        
        return { success: true, policy: response.data.policy }
      } catch (error) {
        this.error = error.response ? error.response.data.error : '更新政策失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // 删除新闻
    async deleteNews(newsId) {
      this.loading = true
      this.error = null
      
      try {
        await axios.delete(`/api/news/${newsId}`)
        
        // 从本地新闻列表中移除
        this.news = this.news.filter(n => n.policy_id !== newsId)
        
        return { success: true }
      } catch (error) {
        this.error = error.response ? error.response.data.error : '删除新闻失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // 删除政策
    async deletePolicy(policyId) {
      this.loading = true
      this.error = null
      
      try {
        await axios.delete(`/api/policies/${policyId}`)
        
        // 从本地政策列表中移除
        this.policies = this.policies.filter(p => p.policy_id !== policyId)
        
        return { success: true }
      } catch (error) {
        this.error = error.response ? error.response.data.error : '删除政策失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // 上传图片
    async uploadImage(file) {
      this.loading = true
      this.error = null
      
      try {
        const formData = new FormData()
        formData.append('image', file)
        
        const response = await axios.post('/api/upload-image', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        return { success: true, imageUrl: response.data.imageUrl }
      } catch (error) {
        this.error = error.response ? error.response.data.error : '图片上传失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // 获取所有可视化类型
    async fetchVisualizationTypes() {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get('/api/visualization-types')
        return { success: true, types: response.data.types }
      } catch (error) {
        this.error = error.response ? error.response.data.error : '获取可视化类型失败'
        console.error('获取可视化类型失败:', error)
        return { success: false, error: this.error, types: [] }
      } finally {
        this.loading = false
      }
    },
    
    // 获取所有可视化数据
    async fetchVisualizations() {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get('/api/visualizations')
        return { success: true, visualizations: response.data.visualizations }
      } catch (error) {
        this.error = error.response ? error.response.data.error : '获取可视化数据失败'
        console.error('获取可视化数据失败:', error)
        return { success: false, error: this.error, visualizations: [] }
      } finally {
        this.loading = false
      }
    },
    
    // 根据类别获取可视化数据
    async fetchVisualizationsByCategory(category) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get(`/api/visualizations?category=${category}`)
        return { success: true, visualizations: response.data.visualizations }
      } catch (error) {
        this.error = error.response ? error.response.data.error : '获取可视化数据失败'
        console.error(`获取类别${category}的可视化数据失败:`, error)
        return { success: false, error: this.error, visualizations: [] }
      } finally {
        this.loading = false
      }
    },
    
    // 获取单个可视化详情
    async fetchVisualizationById(id) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get(`/api/visualizations/${id}`)
        return { success: true, visualization: response.data.visualization }
      } catch (error) {
        this.error = error.response ? error.response.data.error : '获取可视化详情失败'
        console.error(`获取可视化${id}详情失败:`, error)
        return { success: false, error: this.error, visualization: null }
      } finally {
        this.loading = false
      }
    },
    
    // 获取政策主题
    async fetchPolicyTopics() {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get('/api/policy-topics')
        return { success: true, topics: response.data.topics }
      } catch (error) {
        this.error = error.response ? error.response.data.error : '获取主题失败'
        console.error('获取主题失败:', error)
        return { success: false, error: this.error, topics: [] }
      } finally {
        this.loading = false
      }
    },
    
    // 添加主题
    async addTopic(topicData) {
      this.loading = true
      this.error = null
      
      try {
        const data = {
          topic_name: topicData.topic_name,
          user_id: topicData.user_id
        }
        
        const response = await axios.post('/api/policy-topics', data)
        return { success: true, topic: response.data.topic }
      } catch (error) {
        this.error = error.response ? error.response.data.error : '添加主题失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // 更新主题
    async updateTopic(topicId, topicData) {
      this.loading = true
      this.error = null
      
      try {
        const data = {
          topic_name: topicData.topic_name,
          user_id: topicData.user_id
        }
        
        const response = await axios.put(`/api/policy-topics/${topicId}`, data)
        return { success: true, topic: response.data.topic }
      } catch (error) {
        this.error = error.response ? error.response.data.error : '更新主题失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // 删除主题
    async deleteTopic(topicId, userId) {
      this.loading = true
      this.error = null
      
      try {
        await axios.delete(`/api/policy-topics/${topicId}?user_id=${userId}`)
        return { success: true }
      } catch (error) {
        this.error = error.response ? error.response.data.error : '删除主题失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // 添加可视化
    async addVisualization(vizData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post('/api/visualizations', vizData)
        return { success: true, visualization: response.data.visualization }
      } catch (error) {
        this.error = error.response ? error.response.data.error : '添加可视化失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // 更新可视化
    async updateVisualization(vizId, vizData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.put(`/api/visualizations/${vizId}`, vizData)
        return { success: true, visualization: response.data.visualization }
      } catch (error) {
        this.error = error.response ? error.response.data.error : '更新可视化失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // 删除可视化
    async deleteVisualization(vizId) {
      this.loading = true
      this.error = null
      
      try {
        await axios.delete(`/api/visualizations/${vizId}`)
        return { success: true }
      } catch (error) {
        this.error = error.response ? error.response.data.error : '删除可视化失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    }
  }
}) 