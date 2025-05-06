<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import { useContentStore } from '../stores/content'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const userStore = useUserStore()
const contentStore = useContentStore()

const activeTab = ref('dashboard') // 默认显示仪表盘页面
const loading = ref(false) // 添加loading变量
const topicNames = ref({}) // 主题名称映射

// 统计数据
const statsData = ref({
  totalNews: 0,
  totalPolicies: 0,
  totalUsers: 0,
  totalAdmins: 0,
  topicStats: {
    news: {},
    policies: {}
  },
  recentNews: [],
  recentPolicies: []
})

// 获取政策主题
async function fetchPolicyTopics() {
  try {
    const response = await axios.get('/api/policy-topics')
    if (response.data && response.data.topics) {
      response.data.topics.forEach(topic => {
        topicNames.value[topic.topic_id] = topic.topic_name
      })
      console.log('获取主题成功:', topicNames.value)
    }
  } catch (error) {
    console.error('获取政策主题失败:', error)
  }
}

// 获取统计数据
async function fetchStats() {
  console.log('开始获取统计数据...')
  loading.value = true
  
  try {
    // 请求新闻数据
    console.log('检查新闻数据是否已加载')
    if (!contentStore.news || contentStore.news.length === 0) {
      console.log('新闻数据尚未加载，正在请求...')
      try {
        await contentStore.fetchNews()
        console.log('新闻数据已加载，条数:', contentStore.news.length)
      } catch (newsError) {
        console.error('获取新闻失败:', newsError)
      }
    }
    
    // 请求政策数据
    console.log('检查政策数据是否已加载')
    if (!contentStore.policies || contentStore.policies.length === 0) {
      console.log('政策数据尚未加载，正在请求...')
      try {
        await contentStore.fetchPolicies()
        console.log('政策数据已加载，条数:', contentStore.policies.length)
      } catch (policyError) {
        console.error('获取政策失败:', policyError)
      }
    }
    
    // 计算新闻总数
    console.log('计算新闻总数')
    statsData.value.totalNews = contentStore.news && Array.isArray(contentStore.news) ? contentStore.news.length : 0
    
    // 计算政策总数
    console.log('计算政策总数')
    statsData.value.totalPolicies = contentStore.policies && Array.isArray(contentStore.policies) ? contentStore.policies.length : 0
    
    // 获取用户相关统计
    console.log('正在获取用户统计数据')
    try {
      await fetchUsers()
      console.log('用户数据已加载')
    } catch (userError) {
      console.error('获取用户列表时出错:', userError)
      // 继续执行，不要因用户数据获取失败而中断整个函数
    }
    
    statsData.value.totalUsers = userStore.users && Array.isArray(userStore.users) ? userStore.users.length : 0
    statsData.value.totalAdmins = userStore.users && Array.isArray(userStore.users) 
      ? userStore.users.filter(u => u && typeof u === 'object' && u.is_admin).length 
      : 0
    
    // 重置主题统计
    statsData.value.topicStats.news = {}
    statsData.value.topicStats.policies = {}
    
    // 计算新闻主题统计
    console.log('计算新闻主题统计')
    if (contentStore.news && Array.isArray(contentStore.news)) {
      contentStore.news.forEach(news => {
        if (news && typeof news === 'object' && news.topic_id !== undefined) {
          const topicId = news.topic_id
          statsData.value.topicStats.news[topicId] = (statsData.value.topicStats.news[topicId] || 0) + 1
        }
      })
    }
    
    // 计算政策主题统计
    console.log('计算政策主题统计')
    if (contentStore.policies && Array.isArray(contentStore.policies)) {
      contentStore.policies.forEach(policy => {
        if (policy && typeof policy === 'object' && policy.topic_id !== undefined) {
          const topicId = policy.topic_id
          statsData.value.topicStats.policies[topicId] = (statsData.value.topicStats.policies[topicId] || 0) + 1
        }
      })
    }
    
    // 获取最近添加的内容
    console.log('获取最近新闻')
    if (contentStore.news && Array.isArray(contentStore.news) && contentStore.news.length > 0) {
      // 创建一个新数组再排序，以避免修改原数组
      statsData.value.recentNews = [...contentStore.news]
        .filter(item => item && typeof item === 'object')
        .sort((a, b) => {
          const dateA = a.last_updated ? new Date(a.last_updated) : new Date(0)
          const dateB = b.last_updated ? new Date(b.last_updated) : new Date(0)
          return dateB - dateA
        })
        .slice(0, 5)
    } else {
      statsData.value.recentNews = []
    }
    
    console.log('获取最近政策')
    if (contentStore.policies && Array.isArray(contentStore.policies) && contentStore.policies.length > 0) {
      // 创建一个新数组再排序，以避免修改原数组
      statsData.value.recentPolicies = [...contentStore.policies]
        .filter(item => item && typeof item === 'object')
        .sort((a, b) => {
          const dateA = a.last_updated ? new Date(a.last_updated) : new Date(0)
          const dateB = b.last_updated ? new Date(b.last_updated) : new Date(0)
          return dateB - dateA
        })
        .slice(0, 5)
    } else {
      statsData.value.recentPolicies = []
    }
    
    console.log('统计数据获取完成', statsData.value)
  } catch (error) {
    console.error('获取统计数据出错:', error)
    ElMessage.error('获取统计数据失败，可能是网络问题或CORS限制')
  } finally {
    loading.value = false
  }
}

// 分类名称配置
const categoryNames = {
  news: [
    { zh: '教育咨询', en: 'Education Consultation' },
    { zh: '国际合作', en: 'International Cooperation' },
    { zh: '全球化与来华留学', en: 'Globalization & Study in China' },
    { zh: '教育政策解读', en: 'Education Policy Interpretation' },
    { zh: '在华发展机遇', en: 'Development Opportunities in China' }
  ],
  policies: [
    { zh: '学生服务与支持', en: 'Student Services & Support' },
    { zh: '教育与学习', en: 'Education & Learning' },
    { zh: '政策与建设', en: 'Policy & Construction' },
    { zh: '国际关系与交流', en: 'International Relations & Exchange' },
    { zh: '就业与工作', en: 'Employment & Work' }
  ]
}

// 格式化日期
function formatDate(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'short', day: 'numeric' })
}

// 用户管理相关
const userDialogVisible = ref(false)
const currentUser = ref(null)
const userForm = ref({
  username: '',
  is_admin: false
})

// 新闻/政策表单
const formType = ref('news') // news或policy
const formMode = ref('add') // add或edit
const contentForm = ref({
  title: '',
  content: '',
  source_name: '',
  source_url: '',
  topic_id: 0,
  image_url: '',
  unit_published: '',
  date_published: ''
})

// 计算属性，根据当前formType确定可选的主题列表
const availableTopics = computed(() => {
  const topics = []
  for (const id in topicNames.value) {
    topics.push({
      id: parseInt(id),
      name: topicNames.value[id]
    })
  }
  return topics
})

// 获取主题标签的方法
function getTopicLabel(topicId) {
  return topicNames.value[topicId] || `主题 ${topicId}`
}

const formVisible = ref(false)
const formLoading = ref(false)
const currentContentId = ref(null)

// 图片上传相关
const uploadLoading = ref(false)
const imageFile = ref(null)
const predictLoading = ref(false) // 添加预测加载状态

// 获取用户列表
async function fetchUsers() {
  try {
    console.log('正在获取用户列表...');
    await userStore.fetchUsers();
    console.log('获取用户列表完成，用户数量:', userStore.users ? userStore.users.length : 0);
    
    // 检查是否成功获取到用户数据
    if (userStore.users && userStore.users.length === 0 && !userStore.loading) {
      ElMessage.warning('未找到用户数据')
    }
  } catch (error) {
    console.error('获取用户列表出错:', error);
    ElMessage.error('获取用户列表时发生错误')
  }
}

// 打开用户编辑对话框
function openUserDialog(user) {
  currentUser.value = user
  userForm.value = {
    username: user.username,
    is_admin: user.is_admin
  }
  userDialogVisible.value = true
}

// 更新用户信息
async function updateUser() {
  if (!currentUser.value) return
  
  try {
    const result = await userStore.updateUser(currentUser.value.id, userForm.value)
    
    if (result.success) {
      let message = '用户更新成功'
      
      // 如果是本地更新模式，添加提示信息
      if (result.message) {
        message += `（${result.message}）`
      }
      
      ElMessage.success(message)
      userDialogVisible.value = false
      
      // 刷新统计数据
      fetchStats()
    } else {
      ElMessage.error(result.error || '更新失败')
    }
  } catch (error) {
    ElMessage.error('提交失败')
    console.error(error)
  }
}

// 删除用户
async function deleteUser(user) {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const result = await userStore.deleteUser(user.id)
    
    if (result.success) {
      ElMessage.success('用户删除成功')
    } else {
      ElMessage.error(result.error || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error('操作失败')
      console.error(error)
    }
  }
}

// 添加新闻/政策
function showAddForm(type) {
  formType.value = type
  formMode.value = 'add'
  formVisible.value = true
  currentContentId.value = null
  contentForm.value = {
    title: '',
    content: '',
    source_name: '',
    source_url: '',
    topic_id: 0,
    image_url: '',
    unit_published: '',
    date_published: ''
  }
}

// 编辑新闻/政策
function showEditForm(type, item) {
  console.log('showEditForm开始执行，item类型:', typeof item)
  formType.value = type
  formMode.value = 'edit'
  formVisible.value = true
  currentContentId.value = item.policy_id
  
  console.log('编辑项目原始数据:', JSON.stringify(item, null, 2)) // 使用JSON.stringify确保完整输出
  
  // 创建新对象确保没有引用问题
  const clonedItem = JSON.parse(JSON.stringify(item))
  console.log('克隆后的对象:', clonedItem)
  console.log('克隆后的content:', clonedItem.content)
  
  // 直接赋值每个字段
  contentForm.value.title = clonedItem.title || ''
  contentForm.value.content = clonedItem.content || ''
  contentForm.value.source_name = clonedItem.source_name || ''
  contentForm.value.source_url = clonedItem.source_url || ''
  contentForm.value.topic_id = parseInt(clonedItem.topic_id) || 0
  contentForm.value.image_url = clonedItem.image_url || ''
  contentForm.value.unit_published = clonedItem.unit_published || ''
  
  // 处理日期格式，确保日期选择器能正确识别
  if (clonedItem.date_published) {
    try {
      if (typeof clonedItem.date_published === 'string') {
        contentForm.value.date_published = clonedItem.date_published
      } else {
        contentForm.value.date_published = clonedItem.date_published
      }
    } catch (e) {
      console.error('日期处理出错:', e)
      contentForm.value.date_published = ''
    }
  } else {
    contentForm.value.date_published = ''
  }
  
  console.log('赋值完成后的contentForm:', JSON.stringify(contentForm.value, null, 2))
  console.log('contentForm.content:', contentForm.value.content)
  
  // 延迟检查
  setTimeout(() => {
    console.log('500ms后检查content字段:', contentForm.value.content)
  }, 500)
}

// 调试方法
function debugContent() {
  console.log('当前content值:', contentForm.value.content)
  contentForm.value.content = '测试内容 - ' + new Date().toLocaleString()
  console.log('设置后的content值:', contentForm.value.content)
  
  // 延迟检查content值
  setTimeout(() => {
    console.log('延迟后content值:', contentForm.value.content)
  }, 1000)
}

// 提交表单
async function submitForm() {
  // 表单验证
  if (!contentForm.value.title || !contentForm.value.content) {
    ElMessage.warning('标题和内容不能为空')
    return
  }
  
  formLoading.value = true
  
  try {
    // 预测主题ID
    if (!contentForm.value.topic_id || contentForm.value.topic_id === 0) {
      try {
        // 注释掉实际预测代码，改为默认选择第一个主题
        const defaultTopicId = availableTopics.value.length > 0 ? availableTopics.value[0].id : 0
        contentForm.value.topic_id = defaultTopicId
        console.log('自动选择默认主题:', contentForm.value.topic_id)
        ElMessage.success(`已自动选择主题: ${getTopicLabel(contentForm.value.topic_id)}`)
      } catch (error) {
        console.error('主题选择失败:', error)
        // 继续提交，不阻止表单提交
      }
    }
    
    // 处理提交数据
    const submitData = { ...contentForm.value }
    
    // 处理日期
    if (submitData.date_published instanceof Date) {
      submitData.date_published = submitData.date_published.toISOString().split('T')[0] // 格式化为YYYY-MM-DD
    }
    
    let result
    
    if (formMode.value === 'add') {
      // 添加新内容
      if (formType.value === 'news') {
        result = await contentStore.addNews(submitData)
      } else {
        result = await contentStore.addPolicy(submitData)
      }
      
      if (result.success) {
        ElMessage.success(
          `${formType.value === 'news' ? '新闻' : '政策'}添加成功`
        )
        formVisible.value = false
        
        // 重新加载数据
        if (formType.value === 'news') {
          await contentStore.fetchNews()
        } else {
          await contentStore.fetchPolicies()
        }
      } else {
        ElMessage.error(result.error || '添加失败')
      }
    } else {
      // 编辑现有内容
      if (formType.value === 'news') {
        result = await contentStore.updateNews(currentContentId.value, submitData)
      } else {
        result = await contentStore.updatePolicy(currentContentId.value, submitData)
      }
      
      if (result.success) {
        ElMessage.success(
          `${formType.value === 'news' ? '新闻' : '政策'}更新成功`
        )
        formVisible.value = false
        
        // 重新加载数据
        if (formType.value === 'news') {
          await contentStore.fetchNews()
        } else {
          await contentStore.fetchPolicies()
        }
      } else {
        ElMessage.error(result.error || '更新失败')
      }
    }
  } catch (error) {
    ElMessage.error('提交失败')
    console.error(error)
  } finally {
    formLoading.value = false
  }
}

// 删除新闻
async function deleteNews(news) {
  try {
    await ElMessageBox.confirm(
      `确定要删除新闻 "${news.title}" 吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const result = await contentStore.deleteNews(news.policy_id)
    
    if (result.success) {
      ElMessage.success('新闻删除成功')
    } else {
      ElMessage.error(result.error || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error('操作失败')
      console.error(error)
    }
  }
}

// 删除政策
async function deletePolicy(policy) {
  try {
    await ElMessageBox.confirm(
      `确定要删除政策 "${policy.title}" 吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const result = await contentStore.deletePolicy(policy.policy_id)
    
    if (result.success) {
      ElMessage.success('政策删除成功')
    } else {
      ElMessage.error(result.error || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error('操作失败')
      console.error(error)
    }
  }
}

// 处理图片上传
async function handleImageUpload(event) {
  const file = event.target.files?.[0]
  if (!file) return
  
  // 验证文件类型
  if (!file.type.includes('image/')) {
    ElMessage.error('请上传图片文件')
    return
  }
  
  uploadLoading.value = true
  
  try {
    // 创建FormData对象
    const formData = new FormData()
    formData.append('file', file)
    
    let imageUrl = '';
    
    try {
      // 尝试发送请求到后端
      const response = await axios.post('/api/upload-image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      // 设置图片URL - 确保使用完整URL
      const baseUrl = import.meta.env.DEV ? 'http://localhost:5000' : '';
      imageUrl = `${baseUrl}${response.data.url}`
    } catch (apiError) {
      console.warn('API调用失败，使用本地模式:', apiError);
      
      // 在API不可用时，使用本地文件URL作为替代
      // 创建一个本地数据URL (base64)
      await new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          imageUrl = e.target?.result || ''; // 添加可选链操作符，避免null引用
          contentForm.value.image_url = imageUrl;
          ElMessage.success('图片已本地处理（开发模式）')
          uploadLoading.value = false;
          resolve();
        };
        reader.readAsDataURL(file);
      });
    }
    
    // 如果走到这里，说明API调用成功
    contentForm.value.image_url = imageUrl;
    ElMessage.success('图片上传成功')
  } catch (error) {
    ElMessage.error('上传失败')
    console.error(error)
  } finally {
    uploadLoading.value = false
    // 清空文件输入，允许再次选择同一文件
    if (imageFile.value) {
      imageFile.value = null
    }
  }
}

// 获取图表颜色
function getChartColor(index) {
  const colors = [
    '#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399',
    '#8E44AD', '#3498DB', '#27AE60', '#E74C3C', '#1ABC9C'
  ]
  return colors[index % colors.length]
}

// 获取分类标签类型
function getCategoryTagType(category) {
  if (category === undefined || category === null || typeof category !== 'number') {
    return ''; // 返回默认类型
  }
  const types = ['', 'success', 'warning', 'danger', 'info'];
  return types[Math.abs(category) % types.length];
}

// 预测主题ID
async function predictTopicId() {
  try {
    // 拼接数据格式为 "[新闻/政策] 标题 [SEP] 内容"
    const typePrefix = formType.value === 'news' ? '[新闻]' : '[政策]'
    const predictText = `${typePrefix} ${contentForm.value.title} [SEP] ${contentForm.value.content}`
    
    // 调用后端预测API
    const response = await axios.post('/api/predict-topic', {
      text: predictText
    })
    
    if (response.data && response.data.topic_id !== undefined) {
      return { topic_id: response.data.topic_id }
    } else {
      console.warn('预测结果格式错误:', response.data)
      return null
    }
  } catch (error) {
    console.error('调用预测API失败:', error)
    throw error
  }
}

// 添加自动预测按钮
async function manualPredictTopic() {
  // 验证表单
  if (!contentForm.value.title || !contentForm.value.content) {
    ElMessage.warning('请先填写标题和内容')
    return
  }
  
  predictLoading.value = true
  
  try {
    const result = await predictTopicId()
    if (result && result.topic_id !== undefined) {
      contentForm.value.topic_id = result.topic_id
      ElMessage.success(`已预测主题: ${getTopicLabel(contentForm.value.topic_id)}`)
    } else {
      ElMessage.warning('预测失败，请手动选择主题')
    }
  } catch (error) {
    console.error('预测失败:', error)
    ElMessage.error('主题预测失败，请手动选择')
  } finally {
    predictLoading.value = false
  }
}

// 获取主题列表
async function fetchTopics() {
  loading.value = true
  try {
    const result = await contentStore.fetchPolicyTopics()
    if (result.success) {
      // 更新主题缓存
      result.topics.forEach(topic => {
        topicNames.value[topic.topic_id] = topic.topic_name
      })
      return result.topics
    } else {
      ElMessage.error('获取主题列表失败')
      return []
    }
  } catch (error) {
    console.error('获取主题列表失败:', error)
    ElMessage.error('获取主题列表失败')
    return []
  } finally {
    loading.value = false
  }
}

// 可视化管理相关
const visualizationsList = ref([])
const visualizationTypesList = ref([])
const visualizationForm = ref({
  viz_id: null,
  viz_name: '',
  viz_analysis: '',
  image_url: '',
  category: 'News',
  viz_type_id: 1
})
const visualizationDialogVisible = ref(false)
const visualizationDialogTitle = ref('添加可视化')
const visualizationDialogMode = ref('add') // add或edit

// 获取可视化列表
async function fetchVisualizations() {
  loading.value = true
  try {
    const result = await contentStore.fetchVisualizations()
    if (result.success) {
      return result.visualizations
    } else {
      ElMessage.error('获取可视化列表失败')
      return []
    }
  } catch (error) {
    console.error('获取可视化列表失败:', error)
    ElMessage.error('获取可视化列表失败')
    return []
  } finally {
    loading.value = false
  }
}

// 获取可视化类型列表
async function fetchVisualizationTypes() {
  loading.value = true
  try {
    const result = await contentStore.fetchVisualizationTypes()
    if (result.success) {
      visualizationTypesList.value = result.types
      return result.types
    } else {
      ElMessage.error('获取可视化类型列表失败')
      return []
    }
  } catch (error) {
    console.error('获取可视化类型列表失败:', error)
    ElMessage.error('获取可视化类型列表失败')
    return []
  } finally {
    loading.value = false
  }
}

// 刷新可视化列表
async function refreshVisualizations() {
  const visualizations = await fetchVisualizations()
  visualizationsList.value = visualizations
}

// 打开添加可视化对话框
function showAddVisualizationDialog() {
  visualizationDialogMode.value = 'add'
  visualizationDialogTitle.value = '添加可视化'
  visualizationForm.value = {
    viz_id: null,
    viz_name: '',
    viz_analysis: '',
    image_url: '',
    category: 'News',
    viz_type_id: visualizationTypesList.value.length > 0 ? visualizationTypesList.value[0].viz_type_id : 1
  }
  visualizationDialogVisible.value = true
}

// 打开编辑可视化对话框
function showEditVisualizationDialog(visualization) {
  visualizationDialogMode.value = 'edit'
  visualizationDialogTitle.value = '编辑可视化'
  visualizationForm.value = { ...visualization }
  visualizationDialogVisible.value = true
}

// 提交可视化表单
async function submitVisualizationForm() {
  if (!visualizationForm.value.viz_name) {
    ElMessage.warning('请输入可视化名称')
    return
  }
  
  loading.value = true
  try {
    let result
    if (visualizationDialogMode.value === 'add') {
      // 添加可视化
      result = await contentStore.addVisualization(visualizationForm.value)
    } else {
      // 更新可视化
      result = await contentStore.updateVisualization(
        visualizationForm.value.viz_id,
        visualizationForm.value
      )
    }
    
    if (result.success) {
      ElMessage.success(visualizationDialogMode.value === 'add' ? '可视化添加成功' : '可视化更新成功')
      visualizationDialogVisible.value = false
      // 刷新可视化列表
      await refreshVisualizations()
    } else {
      ElMessage.error(result.error || '操作失败')
    }
  } catch (error) {
    console.error('提交可视化数据失败:', error)
    ElMessage.error('提交数据时发生错误')
  } finally {
    loading.value = false
  }
}

// 删除可视化
async function deleteVisualization(visualization) {
  ElMessageBox.confirm(
    `确定要删除可视化"${visualization.viz_name}"吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    loading.value = true
    try {
      const result = await contentStore.deleteVisualization(visualization.viz_id)
      if (result.success) {
        ElMessage.success('可视化删除成功')
        // 刷新可视化列表
        await refreshVisualizations()
      } else {
        ElMessage.error(result.error || '删除失败')
      }
    } catch (error) {
      console.error('删除可视化失败:', error)
      ElMessage.error('删除可视化时发生错误')
    } finally {
      loading.value = false
    }
  }).catch(() => {
    // 用户取消操作
  })
}

// 获取类别名称
const categoryMap = {
  'News': '新闻分析',
  'Official_Policy': '政策分析',
  'Employment_Entrepreneurship': '就业创业分析'
}

function getCategoryName(category) {
  return categoryMap[category] || category
}

// 获取可视化类型名称
function getVisualizationTypeName(typeId) {
  const type = visualizationTypesList.value.find(t => t.viz_type_id === typeId)
  return type ? type.type_name : `类型${typeId}`
}

// 处理可视化图片上传
async function handleVizImageUpload(event) {
  const file = event.target.files[0]
  if (!file) return
  
  const maxSize = 5 * 1024 * 1024 // 5MB
  if (file.size > maxSize) {
    ElMessage.error('图片大小不能超过5MB')
    return
  }
  
  uploadLoading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await axios.post('/api/upload-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (response.data && response.data.url) {
      visualizationForm.value.image_url = response.data.url
      ElMessage.success('图片上传成功')
    } else {
      ElMessage.error('图片上传失败')
    }
  } catch (error) {
    console.error('图片上传错误:', error)
    ElMessage.error('图片上传失败')
  } finally {
    uploadLoading.value = false
    // 清空input，允许再次选择同一文件
    if (this.$refs.vizImageFile) {
      this.$refs.vizImageFile.value = ''
    }
  }
}

onMounted(async () => {
  if (userStore.isAdmin) {
    console.log('管理员页面加载，开始初始化数据...')
    try {
      console.log('获取政策主题')
      await fetchPolicyTopics()
      // 初始化主题列表
      await refreshVisualizations()
      console.log('开始获取新闻数据')
      await contentStore.fetchNews()
      console.log('开始获取政策数据')
      await contentStore.fetchPolicies()
      console.log('开始获取用户数据')
      await fetchUsers()
      console.log('所有数据加载完成')
    } catch (error) {
      console.error('初始化数据时出错:', error)
    }
    // 最后更新统计数据
    await fetchStats()
  }
})
</script>

<template>
  <div class="admin-container">
    <h1 class="page-title">
      管理后台
    </h1>
    
    <div v-if="!userStore.isAdmin" class="access-denied">
      <el-result
        icon="error"
        title="访问被拒绝"
        sub-title="您没有权限访问此页面"
      >
        <template #extra>
          <el-button type="primary" @click="$router.push('/')">
            返回首页
          </el-button>
        </template>
      </el-result>
    </div>
    
    <div v-else class="admin-content">
      <el-tabs v-model="activeTab" @tab-click="() => {if (activeTab === 'dashboard') fetchStats()}">
        <!-- 仪表盘 -->
        <el-tab-pane name="dashboard" label="仪表盘">
          <div class="dashboard-container">
            <!-- 统计卡片 -->
            <div class="stat-cards">
              <el-card class="stat-card">
                <div class="stat-icon news-icon">
                  <el-icon><Document /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ statsData.totalNews }}</div>
                  <div class="stat-label">新闻总数</div>
                </div>
              </el-card>
              
              <el-card class="stat-card">
                <div class="stat-icon policy-icon">
                  <el-icon><DocumentChecked /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ statsData.totalPolicies }}</div>
                  <div class="stat-label">政策总数</div>
                </div>
              </el-card>
              
              <el-card class="stat-card">
                <div class="stat-icon user-icon">
                  <el-icon><User /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ statsData.totalUsers }}</div>
                  <div class="stat-label">用户总数</div>
                </div>
              </el-card>
              
              <el-card class="stat-card">
                <div class="stat-icon admin-icon">
                  <el-icon><UserFilled /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ statsData.totalAdmins }}</div>
                  <div class="stat-label">管理员数</div>
                </div>
              </el-card>
            </div>
            
            <!-- 分类统计 -->
            <div class="category-stats">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-card class="chart-card">
                    <template #header>
                      <div class="chart-header">
                        <el-icon><PieChart /></el-icon>
                        新闻主题分布
                      </div>
                    </template>
                    <div class="chart-container">
                      <div v-for="(count, topicId) in statsData.topicStats.news" :key="`news-${topicId}`" class="chart-item">
                        <div class="chart-item-label">
                          {{ topicNames[topicId] || `主题 ${topicId}` }}
                        </div>
                        <el-progress 
                          :percentage="statsData.totalNews ? Math.round(count / statsData.totalNews * 100) : 0" 
                          :color="getChartColor(topicId)"
                        />
                        <div class="chart-item-count">{{ count }}</div>
                      </div>
                    </div>
                  </el-card>
                </el-col>
                
                <el-col :span="12">
                  <el-card class="chart-card">
                    <template #header>
                      <div class="chart-header">
                        <el-icon><PieChart /></el-icon>
                        政策主题分布
                      </div>
                    </template>
                    <div class="chart-container">
                      <div v-for="(count, topicId) in statsData.topicStats.policies" :key="`policy-${topicId}`" class="chart-item">
                        <div class="chart-item-label">
                          {{ topicNames[topicId] || `主题 ${topicId}` }}
                        </div>
                        <el-progress 
                          :percentage="statsData.totalPolicies ? Math.round(count / statsData.totalPolicies * 100) : 0" 
                          :color="getChartColor(topicId)"
                        />
                        <div class="chart-item-count">{{ count }}</div>
                      </div>
                    </div>
                  </el-card>
                </el-col>
              </el-row>
            </div>
            
            <!-- 最近内容 -->
            <div class="recent-content">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-card class="recent-card">
                    <template #header>
                      <div class="recent-header">
                        <el-icon><Document /></el-icon>
                        最新新闻
                      </div>
                    </template>
                    <div class="recent-list">
                      <div v-if="statsData.recentNews.length === 0" class="empty-data">
                        暂无数据
                      </div>
                      <div v-for="item in statsData.recentNews" :key="item.policy_id" class="recent-item">
                        <div class="recent-title">{{ item.title }}</div>
                        <div class="recent-meta">
                          <span class="recent-date">{{ item.date_published }}</span>
                          <el-tag size="small" :type="getCategoryTagType(item.topic_id)">
                            {{ topicNames[item.topic_id] || `主题 ${item.topic_id}` }}
                          </el-tag>
                        </div>
                      </div>
                    </div>
                  </el-card>
                </el-col>
                
                <el-col :span="12">
                  <el-card class="recent-card">
                    <template #header>
                      <div class="recent-header">
                        <el-icon><DocumentChecked /></el-icon>
                        最新政策
                      </div>
                    </template>
                    <div class="recent-list">
                      <div v-if="statsData.recentPolicies.length === 0" class="empty-data">
                        暂无数据
                      </div>
                      <div v-for="item in statsData.recentPolicies" :key="item.policy_id" class="recent-item">
                        <div class="recent-title">{{ item.title }}</div>
                        <div class="recent-meta">
                          <span class="recent-date">{{ item.date_published }}</span>
                          <el-tag size="small" :type="getCategoryTagType(item.topic_id)">
                            {{ topicNames[item.topic_id] || `主题 ${item.topic_id}` }}
                          </el-tag>
                        </div>
                      </div>
                    </div>
                  </el-card>
                </el-col>
              </el-row>
            </div>
          </div>
        </el-tab-pane>
        
        <!-- 用户管理 -->
        <el-tab-pane name="users" label="用户管理">
          <div class="tab-header">
            <h2>用户列表</h2>
            <el-button type="primary" @click="fetchUsers">
              刷新列表
            </el-button>
          </div>
          
          <el-table 
            :data="userStore.users" 
            style="width: 100%; margin-top: 20px" 
            v-loading="userStore.loading"
          >
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="username" label="用户名" />
            <el-table-column label="管理员" width="100">
              <template #default="scope">
                <span>{{ scope.row.is_admin ? '是' : '否' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="注册时间" width="180" />
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="openUserDialog(scope.row)"
                >
                  编辑
                </el-button>
                <el-button 
                  size="small" 
                  type="danger" 
                  @click="deleteUser(scope.row)"
                  :disabled="scope.row.is_admin"
                  title="不能删除管理员账户"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <!-- 内容管理 -->
        <el-tab-pane label="内容管理" name="content">
          <div class="content-actions">
            <el-button type="primary" @click="showAddForm('news')">
              添加新闻
            </el-button>
            <el-button type="success" @click="showAddForm('policy')">
              添加政策
            </el-button>
          </div>
          
          <!-- 新闻列表 -->
          <h3>新闻列表</h3>
          <el-table :data="contentStore.news" style="width: 100%; margin-bottom: 20px" v-loading="contentStore.loading">
            <el-table-column prop="policy_id" label="ID" width="80" />
            <el-table-column prop="title" label="标题" />
            <el-table-column label="图片" width="100">
              <template #default="scope">
                <el-image 
                  v-if="scope.row.image_url" 
                  :src="scope.row.image_url" 
                  fit="cover"
                  style="width: 50px; height: 50px"
                  :preview-src-list="[scope.row.image_url]"
                />
                <span v-else>无</span>
              </template>
            </el-table-column>
            <el-table-column prop="date_published" label="发布日期" width="120" />
            <el-table-column prop="unit_published" label="发布单位" width="120" />
            <el-table-column label="主题" width="120">
              <template #default="scope">
                {{ topicNames[scope.row.topic_id] || `主题 ${scope.row.topic_id}` }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="showEditForm('news', scope.row)"
                >
                  编辑
                </el-button>
                <el-button 
                  size="small" 
                  type="danger" 
                  @click="deleteNews(scope.row)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          
          <!-- 政策列表 -->
          <h3>政策列表</h3>
          <el-table :data="contentStore.policies" style="width: 100%" v-loading="contentStore.loading">
            <el-table-column prop="policy_id" label="ID" width="80" />
            <el-table-column prop="title" label="标题" />
            <el-table-column label="图片" width="100">
              <template #default="scope">
                <el-image 
                  v-if="scope.row.image_url" 
                  :src="scope.row.image_url" 
                  fit="cover"
                  style="width: 50px; height: 50px"
                  :preview-src-list="[scope.row.image_url]"
                />
                <span v-else>无</span>
              </template>
            </el-table-column>
            <el-table-column prop="date_published" label="发布日期" width="120" />
            <el-table-column prop="unit_published" label="发布单位" width="120" />
            <el-table-column label="主题" width="120">
              <template #default="scope">
                {{ topicNames[scope.row.topic_id] || `主题 ${scope.row.topic_id}` }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="showEditForm('policy', scope.row)"
                >
                  编辑
                </el-button>
                <el-button 
                  size="small" 
                  type="danger" 
                  @click="deletePolicy(scope.row)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <!-- 可视化管理 -->
        <el-tab-pane label="可视化管理" name="visualization">
          <div class="tab-header">
            <h2>可视化管理</h2>
            <el-button type="primary" @click="showAddVisualizationDialog">
              添加可视化
            </el-button>
          </div>
          
          <!-- 可视化列表表格 -->
          <el-table 
            :data="visualizationsList" 
            style="width: 100%; margin-top: 20px"
            v-loading="loading"
          >
            <el-table-column prop="viz_id" label="ID" width="80" />
            <el-table-column prop="viz_name" label="名称" />
            <el-table-column label="预览图" width="120">
              <template #default="scope">
                <el-image 
                  v-if="scope.row.image_url" 
                  :src="scope.row.image_url" 
                  fit="cover"
                  style="width: 80px; height: 50px"
                  :preview-src-list="[scope.row.image_url]"
                />
                <span v-else>无图片</span>
              </template>
            </el-table-column>
            <el-table-column label="分类" width="120">
              <template #default="scope">
                {{ getCategoryName(scope.row.category) }}
              </template>
            </el-table-column>
            <el-table-column label="类型" width="120">
              <template #default="scope">
                {{ getVisualizationTypeName(scope.row.viz_type_id) }}
              </template>
            </el-table-column>
            <el-table-column prop="last_updated" label="更新时间" width="160" />
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="showEditVisualizationDialog(scope.row)"
                >
                  编辑
                </el-button>
                <el-button 
                  size="small" 
                  type="danger" 
                  @click="deleteVisualization(scope.row)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
      
      <!-- 用户编辑对话框 -->
      <el-dialog
        v-model="userDialogVisible"
        title="编辑用户"
        width="30%"
      >
        <el-form :model="userForm" label-width="100px">
          <el-form-item label="用户名">
            <el-input v-model="userForm.username" disabled />
          </el-form-item>
          
          <el-form-item label="管理员权限">
            <el-switch v-model="userForm.is_admin" />
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="userDialogVisible = false">
            取消
          </el-button>
          <el-button type="primary" @click="updateUser">
            保存
          </el-button>
        </template>
      </el-dialog>
      
      <!-- 添加/编辑新闻/政策对话框 -->
      <el-dialog
        v-model="formVisible"
        :title="`${formMode === 'add' ? '添加' : '编辑'}${formType === 'news' ? '新闻' : '政策'}`"
        width="60%"
      >
        <el-form :model="contentForm" label-width="120px">
          <el-form-item label="标题" required>
            <el-input v-model="contentForm.title" />
          </el-form-item>
          
          <el-form-item label="内容" v-if="formType !== 'topic'">
            <el-input
              type="textarea"
              v-model="contentForm.content"
              rows="10"
              placeholder="请输入内容"
              @input="value => console.log('内容输入:', value)"
            ></el-input>
          </el-form-item>
          
          <el-form-item label="来源名称">
            <el-input v-model="contentForm.source_name" />
          </el-form-item>
          
          <el-form-item label="来源链接">
            <el-input v-model="contentForm.source_url" />
          </el-form-item>
          
          <el-form-item label="发布单位">
            <el-input v-model="contentForm.unit_published" />
          </el-form-item>
          
          <el-form-item label="发布日期">
            <el-date-picker
              v-model="contentForm.date_published"
              type="date"
              value-format="YYYY-MM-DD"
              format="YYYY-MM-DD"
              placeholder="选择日期"
              style="width: 100%"
            />
          </el-form-item>
          
          <el-form-item label="主题分类">
            <div style="display: flex; gap: 10px; width: 100%">
              <el-select v-model="contentForm.topic_id" style="flex-grow: 1">
                <el-option 
                  v-for="topic in availableTopics"
                  :key="topic.id" 
                  :label="topic.name"
                  :value="topic.id" 
                />
              </el-select>
              <el-button 
                type="primary" 
                @click="manualPredictTopic" 
                :loading="predictLoading"
                title="基于标题和内容自动预测主题"
              >
                自动预测
              </el-button>
            </div>
          </el-form-item>
          
          <el-form-item label="图片">
            <div class="image-upload">
              <div class="image-preview" v-if="contentForm.image_url">
                <el-image 
                  :src="contentForm.image_url" 
                  fit="cover"
                  style="width: 200px; height: 120px"
                  :preview-src-list="[contentForm.image_url]"
                />
                <el-button 
                  type="danger" 
                  size="small" 
                  class="remove-image"
                  @click="contentForm.image_url = ''"
                >
                  移除
                </el-button>
              </div>
              
              <div class="upload-control">
                <input 
                  type="file" 
                  accept="image/*" 
                  ref="imageFile" 
                  @change="handleImageUpload" 
                  style="display: none"
                />
                <el-button 
                  type="primary" 
                  @click="$refs.imageFile && $refs.imageFile.click()"
                  :loading="uploadLoading"
                >
                  上传图片
                </el-button>
                <p class="upload-tip">
                  支持JPG、PNG、GIF格式，文件大小不超过5MB
                </p>
              </div>
            </div>
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="formVisible = false">
            取消
          </el-button>
          <el-button type="primary" @click="submitForm" :loading="formLoading">
            提交
          </el-button>
        </template>
      </el-dialog>
      
      <!-- 可视化编辑对话框 -->
      <el-dialog 
        v-model="visualizationDialogVisible" 
        :title="visualizationDialogTitle"
        width="650px"
      >
        <el-form :model="visualizationForm" label-width="100px">
          <el-form-item label="名称" required>
            <el-input v-model="visualizationForm.viz_name" />
          </el-form-item>
          
          <el-form-item label="分析内容">
            <el-input 
              type="textarea" 
              v-model="visualizationForm.viz_analysis" 
              rows="6" 
              placeholder="请输入可视化分析内容"
            />
          </el-form-item>
          
          <el-form-item label="分类" required>
            <el-select v-model="visualizationForm.category" style="width: 100%">
              <el-option label="新闻分析" value="News" />
              <el-option label="政策分析" value="Official_Policy" />
              <el-option label="就业创业分析" value="Employment_Entrepreneurship" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="可视化类型" required>
            <el-select v-model="visualizationForm.viz_type_id" style="width: 100%">
              <el-option 
                v-for="type in visualizationTypesList" 
                :key="type.viz_type_id" 
                :label="type.type_name" 
                :value="type.viz_type_id" 
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="图片">
            <div class="image-preview" v-if="visualizationForm.image_url">
              <el-image 
                :src="visualizationForm.image_url" 
                fit="contain"
                style="width: 300px; height: 200px;"
                :preview-src-list="[visualizationForm.image_url]"
              />
              <el-button 
                type="danger" 
                size="small" 
                class="remove-image"
                @click="visualizationForm.image_url = ''"
              >
                移除图片
              </el-button>
            </div>
            
            <div class="upload-control">
              <input 
                type="file" 
                accept="image/*" 
                ref="vizImageFile" 
                @change="handleVizImageUpload" 
                style="display: none"
              />
              <el-button 
                type="primary" 
                @click="$refs.vizImageFile && $refs.vizImageFile.click()"
                :loading="uploadLoading"
              >
                上传图片
              </el-button>
              <p class="upload-tip">支持JPG、PNG、GIF格式，建议尺寸1200×800像素</p>
            </div>
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="visualizationDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitVisualizationForm" :loading="loading">确定</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<style scoped>
.admin-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  font-size: 28px;
  margin-bottom: 20px;
  color: #303133;
}

.access-denied {
  text-align: center;
  padding: 50px 0;
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

/* 仪表盘样式 */
.dashboard-container {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.stat-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  border-radius: 8px;
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  margin-right: 15px;
  font-size: 24px;
}

.news-icon {
  background-color: #ecf5ff;
  color: #409eff;
}

.policy-icon {
  background-color: #f0f9eb;
  color: #67c23a;
}

.user-icon {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.admin-icon {
  background-color: #fef0f0;
  color: #f56c6c;
}

.stat-content {
  flex-grow: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 5px;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.chart-card {
  height: 100%;
}

.chart-header, .recent-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: bold;
  font-size: 16px;
}

.chart-container {
  padding: 10px 0;
}

.chart-item {
  margin-bottom: 15px;
}

.chart-item-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 14px;
}

.chart-item-count {
  text-align: right;
  font-size: 14px;
  color: #606266;
  margin-top: 2px;
}

.recent-list {
  max-height: 350px;
  overflow-y: auto;
}

.recent-item {
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.recent-item:last-child {
  border-bottom: none;
}

.recent-title {
  font-weight: 500;
  margin-bottom: 8px;
  color: #303133;
}

.recent-meta {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #909399;
}

.empty-data {
  text-align: center;
  color: #909399;
  padding: 30px 0;
}

/* 用户表格样式 */
.user-actions {
  display: flex;
  gap: 10px;
}

@media (max-width: 768px) {
  .stat-cards {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
  
  .stat-icon {
    width: 50px;
    height: 50px;
    font-size: 20px;
  }
  
  .stat-value {
    font-size: 24px;
  }
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.image-preview {
  margin-bottom: 15px;
  position: relative;
}

.remove-image {
  position: absolute;
  top: 5px;
  right: 5px;
}

.upload-control {
  margin-top: 10px;
}

.upload-tip {
  margin-top: 5px;
  font-size: 12px;
  color: #909399;
}
</style> 