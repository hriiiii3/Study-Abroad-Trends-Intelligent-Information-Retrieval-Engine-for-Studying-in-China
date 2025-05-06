<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { useContentStore } from '../stores/content'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const contentStore = useContentStore()

const username = ref('')
const password = ref('')
const loading = ref(false)

const currentLanguage = computed(() => contentStore.currentLanguage)

async function handleLogin() {
  if (!username.value || !password.value) {
    ElMessage.error(currentLanguage.value === 'zh' ? '用户名和密码不能为空' : 'Username and password cannot be empty')
    return
  }
  
  loading.value = true
  const result = await userStore.login(username.value, password.value)
  loading.value = false
  
  if (result.success) {
    ElMessage.success(currentLanguage.value === 'zh' ? '登录成功' : 'Login successful')
    router.push('/')
  } else {
    ElMessage.error(result.error || (currentLanguage.value === 'zh' ? '登录失败' : 'Login failed'))
  }
}
</script>

<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2 class="login-title">
        {{ currentLanguage === 'zh' ? '用户登录' : 'User Login' }}
      </h2>
      
      <el-form>
        <el-form-item>
          <el-input
            v-model="username"
            :placeholder="currentLanguage === 'zh' ? '用户名' : 'Username'"
            prefix-icon="el-icon-user"
          />
        </el-form-item>
        
        <el-form-item>
          <el-input
            v-model="password"
            type="password"
            :placeholder="currentLanguage === 'zh' ? '密码' : 'Password'"
            prefix-icon="el-icon-lock"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            :loading="loading" 
            @click="handleLogin"
            style="width: 100%"
          >
            {{ currentLanguage === 'zh' ? '登录' : 'Login' }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <p>
          {{ currentLanguage === 'zh' ? '还没有账号？' : 'Don\'t have an account?' }}
          <el-button 
            type="text" 
            @click="router.push('/register')"
          >
            {{ currentLanguage === 'zh' ? '立即注册' : 'Register now' }}
          </el-button>
        </p>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 70vh;
}

.login-card {
  width: 400px;
  max-width: 100%;
}

.login-title {
  text-align: center;
  margin-bottom: 30px;
  color: #409EFF;
}

.login-footer {
  margin-top: 20px;
  text-align: center;
}
</style> 