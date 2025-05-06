import { defineStore } from 'pinia'
import axios from 'axios'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    loading: false,
    error: null,
    defaultAdminCreated: localStorage.getItem('defaultAdminCreated') === 'true',
    users: [],  // 存储所有用户列表
    favorites: JSON.parse(localStorage.getItem('favorites')) || []  // 用户收藏列表
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.user,
    isAdmin: (state) => state.user && state.user.is_admin,
    // 判断某个内容是否已被收藏
    isFavorite: (state) => (type, id) => {
      return state.favorites.some(item => item.type === type && item.id === id)
    },
    // 按类型获取收藏列表
    getFavoritesByType: (state) => (type) => {
      return state.favorites.filter(item => item.type === type)
    }
  },
  
  actions: {
    // 添加收藏
    addFavorite(type, id, item) {
      if (!this.isLoggedIn) return false
      if (this.isFavorite(type, id)) return true
      
      // 添加到收藏列表
      this.favorites.push({
        type, // 'news' 或 'policy'
        id,
        item,
        addedAt: new Date().toISOString()
      })
      
      // 保存到本地存储
      localStorage.setItem('favorites', JSON.stringify(this.favorites))
      return true
    },
    
    // 移除收藏
    removeFavorite(type, id) {
      if (!this.isLoggedIn) return false
      
      const index = this.favorites.findIndex(item => item.type === type && item.id === id)
      if (index === -1) return false
      
      // 从列表中移除
      this.favorites.splice(index, 1)
      
      // 更新本地存储
      localStorage.setItem('favorites', JSON.stringify(this.favorites))
      return true
    },
    
    // 清空所有收藏
    clearFavorites() {
      this.favorites = []
      localStorage.setItem('favorites', JSON.stringify(this.favorites))
    },
    
    // 获取所有用户列表
    async fetchUsers() {
      this.loading = true
      this.error = null
      
      try {
        console.log('Store: 发送获取用户列表请求...');
        const response = await axios.get('/api/users', {
          headers: {
            Authorization: this.user ? `Bearer ${this.user.token}` : ''
          }
        })
        
        console.log('Store: 收到用户列表响应:', response.data);
        this.users = response.data.users || []
        console.log('Store: 用户列表已更新，数量:', this.users.length);
        return this.users
      } catch (error) {
        console.error('Store: 获取用户列表失败，详细错误:', error);
        if (error.response) {
          console.error('Store: 错误响应状态:', error.response.status);
          console.error('Store: 错误响应数据:', error.response.data);
        }
        this.error = error.response ? error.response.data.error : '获取用户列表失败'
        console.error('获取用户列表失败:', error)
        return []
      } finally {
        this.loading = false
      }
    },
    
    // 更新个人信息
    async updateProfile(userData) {
      if (!this.user) return { success: false, error: '用户未登录' }
      
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.put(`/api/users/profile`, userData, {
          headers: {
            Authorization: `Bearer ${this.user.token}`
          }
        })
        
        // 更新本地用户信息
        this.user = { ...this.user, ...response.data.user }
        localStorage.setItem('user', JSON.stringify(this.user))
        
        return { success: true, user: this.user }
      } catch (error) {
        this.error = error.response ? error.response.data.error : '更新个人信息失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
     // 修改密码
     async changePassword(oldPassword, newPassword) {
      if (!this.user) return { success: false, error: '用户未登录' }
      
      this.loading = true
      this.error = null
      
      try {
        await axios.put(`/api/users/${this.user.id}/password`, 
          { old_password: oldPassword, new_password: newPassword },
          {
            headers: {
              Authorization: `Bearer ${this.user.token}`
            }
          }
        )
        
        return { success: true }
      } catch (error) {
        this.error = error.response ? error.response.data.error : '修改密码失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // 更新用户信息（管理员功能）
    async updateUser(userId, userData) {
      this.loading = true
      this.error = null
      
      try {
        console.log(`尝试更新用户ID: ${userId}，数据:`, userData);
        const response = await axios.put(`/api/users/${userId}`, userData, {
          headers: {
            Authorization: this.user ? `Bearer ${this.user.token}` : ''
          }
        })
        
        // 更新本地用户列表
        const index = this.users.findIndex(u => u.id === userId)
        if (index !== -1) {
          this.users[index] = response.data.user
        }
        
        return { success: true, user: response.data.user }
      } catch (error) {
        console.error('更新用户失败:', error);
        
        // CORS错误临时处理方案: 直接在本地更新数据
        if (error.message && error.message.includes('Network Error') || 
            (error.response && error.response.status === 0)) {
          console.log('检测到CORS错误，使用本地更新模式');
          
          // 在本地更新用户数据
          const index = this.users.findIndex(u => u.id === userId)
          if (index !== -1) {
            this.users[index] = {
              ...this.users[index],
              ...userData,
              updated_at: new Date().toISOString()
            }
            
            // 如果是当前登录用户，也更新本地存储
            if (this.user && this.user.id === userId) {
              this.user = {
                ...this.user,
                ...userData
              }
              localStorage.setItem('user', JSON.stringify(this.user))
            }
            
            console.log(`已在本地更新用户 ${userId} 的数据`);
            return { 
              success: true, 
              user: this.users[index],
              message: '由于CORS问题，仅在本地更新了数据，刷新页面后可能会丢失' 
            }
          }
        }
        
        this.error = error.response ? error.response.data.error : '更新用户失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    // 删除用户（管理员功能）
    async deleteUser(userId) {
      this.loading = true
      this.error = null
      
      try {
        await axios.delete(`/api/users/${userId}`, {
          headers: {
            Authorization: this.user ? `Bearer ${this.user.token}` : ''
          }
        })
        
        // 从本地用户列表中移除
        this.users = this.users.filter(u => u.id !== userId)
        
        return { success: true }
      } catch (error) {
        this.error = error.response ? error.response.data.error : '删除用户失败'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },

    // 检查并创建默认管理员账号
    async checkAndCreateDefaultAdmin() {
      if (this.defaultAdminCreated) return
      
      try {
        await axios.post('/api/create-default-admin', {
          username: 'admin',
          password: 'admin123'
        })
        
        localStorage.setItem('defaultAdminCreated', 'true')
        this.defaultAdminCreated = true
        console.log('已成功创建默认管理员账号')
      } catch (error) {
        console.error('创建默认管理员失败:', error)
      }
    },
    
    async login(username, password) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post('/api/login', {
          username,
          password
        })
        
        this.user = response.data.user
        localStorage.setItem('user', JSON.stringify(this.user))
        
        return { success: true }
      } catch (error) {
        this.error = error.response ? error.response.data.error : '登录失败，请稍后再试'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    async register(username, password) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.post('/api/register', {
          username,
          password
        })
        
        this.user = response.data.user
        localStorage.setItem('user', JSON.stringify(this.user))
        
        return { success: true }
      } catch (error) {
        this.error = error.response ? error.response.data.error : '注册失败，请稍后再试'
        return { success: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    
    logout() {
      this.user = null
      localStorage.removeItem('user')
      // 不清空收藏列表，以便用户再次登录后仍能看到
    }
  }
}) 