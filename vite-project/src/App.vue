<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from './stores/user'
import { useContentStore } from './stores/content'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const contentStore = useContentStore()

const isLoggedIn = computed(() => userStore.isLoggedIn)
const isAdmin = computed(() => userStore.isAdmin)
const currentLanguage = computed(() => contentStore.currentLanguage)
const showUserMenu = ref(false)
const showLangMenu = ref(false)

// 切换语言
function toggleLanguage(lang) {
  contentStore.setLanguage(lang)
  showLangMenu.value = false
}

// 切换下拉菜单的显示状态
function toggleMenu(menu) {
  if (menu === 'lang') {
    showLangMenu.value = !showLangMenu.value
    showUserMenu.value = false // 关闭其他菜单
  } else if (menu === 'user') {
    showUserMenu.value = !showUserMenu.value
    showLangMenu.value = false // 关闭其他菜单
  }
}

// 点击页面其他区域时关闭菜单
function closeMenus(event) {
  // 检查点击的元素是否在菜单内
  const isClickInUserMenu = event.target.closest('.user-dropdown')
  const isClickInLangMenu = event.target.closest('.lang-dropdown')
  
  if (!isClickInUserMenu) {
    showUserMenu.value = false
  }
  
  if (!isClickInLangMenu) {
    showLangMenu.value = false
  }
}

// 退出登录
function logout() {
  userStore.logout()
  ElMessage.success(currentLanguage.value === 'zh' ? '退出成功' : 'Logged out successfully')
  router.push('/')
}

onMounted(() => {
  // 初始加载新闻和政策
  contentStore.fetchNews()
  contentStore.fetchPolicies()
  
  // 检查并创建默认管理员账号
  userStore.checkAndCreateDefaultAdmin()
  
  // 添加全局点击事件监听器
  document.addEventListener('click', closeMenus)
})

// 在组件卸载时移除事件监听器
onUnmounted(() => {
  document.removeEventListener('click', closeMenus)
})
</script>

<template>
    <div class="app-container">
        <el-container>
            <el-header>
                <div class="header-container">
                    <div class="logo" @click="router.push('/')">
                        <span v-if="currentLanguage === 'zh'">留途风向</span>
                        <span v-else>Study in China News & Policy System</span>
                    </div>
                    <div class="nav-links">
                        <el-button text @click="router.push('/')">
                            {{ currentLanguage === 'zh' ? '首页' : 'Home' }}
                        </el-button>
                        <el-button text @click="router.push('/ai-chat')" v-if="isLoggedIn">
                            {{ currentLanguage === 'zh' ? 'AI智能助手' : 'AI Assistant' }}
                        </el-button>
                        <el-button text @click="router.push('/admin')" v-if="isAdmin">
                            {{ currentLanguage === 'zh' ? '管理页面' : 'Admin' }}
                        </el-button>
                    </div>
                    <div class="user-actions">
                        <!-- 语言切换下拉菜单 -->
                        <div class="dropdown-container lang-dropdown" @click.stop="toggleMenu('lang')">
                            <el-button type="primary">
                                {{ currentLanguage === 'zh' ? '中文' : 'English' }}
                                <el-icon class="dropdown-icon" :class="{ 'rotate': showLangMenu }"><ArrowDown /></el-icon>
                            </el-button>

                            <div class="dropdown-menu" v-show="showLangMenu">
                                <div class="dropdown-item" @click="toggleLanguage('zh')">
                                    <el-icon v-if="currentLanguage === 'zh'"><Check /></el-icon>
                                    <span>中文</span>
                                </div>
                                <div class="dropdown-item" @click="toggleLanguage('en')">
                                    <el-icon v-if="currentLanguage === 'en'"><Check /></el-icon>
                                    <span>English</span>
                                </div>
                            </div>
                        </div>

                        <template v-if="isLoggedIn">
                            <div class="dropdown-container user-dropdown" @click.stop="toggleMenu('user')">
                                <el-button type="info">
                                    {{ currentLanguage === 'zh' ? '用户' : 'User' }}
                                    <el-icon class="dropdown-icon" :class="{ 'rotate': showUserMenu }"><ArrowDown /></el-icon>
                                </el-button>

                                <div class="dropdown-menu" v-show="showUserMenu">
                                    <div class="dropdown-item" @click="router.push('/profile')">
                                        <el-icon><User /></el-icon>
                                        {{ currentLanguage === 'zh' ? '个人中心' : 'Profile' }}
                                    </div>
                                    <div class="dropdown-item" @click="router.push('/favorites')">
                                        <el-icon><Star /></el-icon>
                                        {{ currentLanguage === 'zh' ? '我的收藏' : 'My Favorites' }}
                                    </div>
                                    <div class="dropdown-item" v-if="isAdmin" @click="router.push('/admin')">
                                        <el-icon><Setting /></el-icon>
                                        {{ currentLanguage === 'zh' ? '管理后台' : 'Admin' }}
                                    </div>
                                    <div class="dropdown-item" @click="logout">
                                        <el-icon><SwitchButton /></el-icon>
                                        {{ currentLanguage === 'zh' ? '退出登录' : 'Logout' }}
                                    </div>
                                </div>
                            </div>
                        </template>
                        <template v-else>
                            <el-button @click="router.push('/login')">
                                {{ currentLanguage === 'zh' ? '登录' : 'Login' }}
                            </el-button>
                            <el-button type="primary" @click="router.push('/register')">
                                {{ currentLanguage === 'zh' ? '注册' : 'Register' }}
                            </el-button>
                        </template>
                    </div>
                </div>
            </el-header>

            <el-main>
                <router-view />
            </el-main>

            <el-footer>
                <div class="footer-content">
                    <p v-if="currentLanguage === 'zh'">
                        © 2024 来华留学新闻政策系统 - 为留学生提供最新资讯
                    </p>
                    <p v-else>
                        © 2024 Study in China News & Policy System - Latest Information for International Students
                    </p>
                </div>
            </el-footer>
        </el-container>
    </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
}

.el-header {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 0 20px;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.logo {
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
  color: #409EFF;
}

.nav-links {
  display: flex;
  gap: 20px;
}

.user-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.el-main {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 120px);
}

.el-footer {
  background-color: #545c64;
  color: #fff;
  text-align: center;
  padding: 20px;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
}

/* 下拉菜单通用样式 */
.dropdown-container {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 5px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  width: 150px;
  z-index: 100;
  overflow: hidden;
}

.dropdown-item {
  padding: 10px 15px;
  cursor: pointer;
  transition: background-color 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.dropdown-item:hover {
  background-color: #f5f7fa;
}

.dropdown-item i {
  font-size: 16px;
  width: 16px;
  height: 16px;
  display: inline-flex;
  justify-content: center;
  align-items: center;
}

.dropdown-icon {
  margin-left: 5px;
  transition: transform 0.3s;
}

.dropdown-icon.rotate {
  transform: rotate(180deg);
}



</style>
