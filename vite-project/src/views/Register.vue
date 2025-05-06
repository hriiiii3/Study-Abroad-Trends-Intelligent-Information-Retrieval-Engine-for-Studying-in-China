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
const confirmPassword = ref('')
const loading = ref(false)

const currentLanguage = computed(() => contentStore.currentLanguage)

async function handleRegister() {
  if (!username.value || !password.value) {
    ElMessage.error(currentLanguage.value === 'zh' ? '用户名和密码不能为空' : 'Username and password cannot be empty')
    return
  }
  
  if (password.value !== confirmPassword.value) {
    ElMessage.error(currentLanguage.value === 'zh' ? '两次输入的密码不一致' : 'Passwords do not match')
    return
  }
  
  loading.value = true
  const result = await userStore.register(username.value, password.value)
  loading.value = false
  
  if (result.success) {
    ElMessage.success(currentLanguage.value === 'zh' ? '注册成功' : 'Registration successful')
    router.push('/')
  } else {
    ElMessage.error(result.error || (currentLanguage.value === 'zh' ? '注册失败' : 'Registration failed'))
  }
}
</script>

<template>
  <div class="register-container">
    <el-card class="register-card">
      <h2 class="register-title">
        {{ currentLanguage === 'zh' ? '用户注册' : 'User Registration' }}
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
          />
        </el-form-item>
        
        <el-form-item>
          <el-input
            v-model="confirmPassword"
            type="password"
            :placeholder="currentLanguage === 'zh' ? '确认密码' : 'Confirm Password'"
            prefix-icon="el-icon-lock"
            @keyup.enter="handleRegister"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            :loading="loading" 
            @click="handleRegister"
            style="width: 100%"
          >
            {{ currentLanguage === 'zh' ? '注册' : 'Register' }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="register-footer">
        <p>
          {{ currentLanguage === 'zh' ? '已有账号？' : 'Already have an account?' }}
          <el-button 
            type="text" 
            @click="router.push('/login')"
          >
            {{ currentLanguage === 'zh' ? '立即登录' : 'Login now' }}
          </el-button>
        </p>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 70vh;
}

.register-card {
  width: 400px;
  max-width: 100%;
}

.register-title {
  text-align: center;
  margin-bottom: 30px;
  color: #409EFF;
}

.register-footer {
  margin-top: 20px;
  text-align: center;
}
</style> 