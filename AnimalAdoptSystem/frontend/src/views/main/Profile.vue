<template>
  <div class="profile">
    <div class="container">
      <h2>个人信息</h2>
      
      <div class="profile-content" v-if="user">
        <div class="profile-header">
          <img :src="user.avatar || 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=user%20avatar%20portrait&image_size=square'" :alt="user.username" class="avatar">
          <div class="user-info">
            <h3>{{ user.username }}</h3>
            <p>{{ user.email }}</p>
            <p v-if="user.phone">电话：{{ user.phone }}</p>
            <p v-if="user.address">地址：{{ user.address }}</p>
            <p v-if="user.bio">{{ user.bio }}</p>
          </div>
        </div>
        
        <div class="profile-actions">
          <button class="btn btn-primary" @click="editMode = !editMode">
            {{ editMode ? '取消编辑' : '编辑资料' }}
          </button>
          <router-link to="/password-change" class="btn btn-secondary">
            修改密码
          </router-link>
          <router-link v-if="user && user.user_type === 'normal'" to="/volunteer/apply" class="btn btn-volunteer">
            申请成为志愿者
          </router-link>
          <span v-else-if="user && user.user_type === 'volunteer'" class="volunteer-badge">
            ✅ 志愿者身份
          </span>
        </div>
        
        <form v-if="editMode" @submit.prevent="updateProfile" class="edit-form">
          <div class="form-group">
            <label for="email">邮箱</label>
            <input type="email" id="email" v-model="form.email">
          </div>
          <div class="form-group">
            <label for="phone">电话</label>
            <input type="tel" id="phone" v-model="form.phone">
          </div>
          <div class="form-group">
            <label for="avatar">头像URL</label>
            <input type="url" id="avatar" v-model="form.avatar">
          </div>
          <div class="form-group">
            <label for="address">地址</label>
            <input type="text" id="address" v-model="form.address">
          </div>
          <div class="form-group">
            <label for="bio">个人简介</label>
            <textarea id="bio" v-model="form.bio" rows="4"></textarea>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? '保存中...' : '保存修改' }}
            </button>
            <button type="button" class="btn btn-secondary" @click="editMode = false">取消</button>
          </div>
          <div class="error-message" v-if="error">
            {{ error }}
          </div>
          <div class="success-message" v-if="success">
            {{ success }}
          </div>
        </form>
      </div>
      
      <div class="loading" v-else-if="loading">
        <p>加载中...</p>
      </div>
      
      <div class="error-container" v-else-if="error">
        <div class="error-card">
          <h3>❌ 出错了</h3>
          <p>{{ error }}</p>
          <button class="btn btn-primary" @click="getUserProfile">重试</button>
          <router-link to="/login" class="btn btn-secondary" v-if="error.includes('登录')">去登录</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Profile',
  data() {
    return {
      user: null,
      editMode: false,
      form: {
        email: '',
        phone: '',
        avatar: '',
        address: '',
        bio: ''
      },
      loading: true,
      error: '',
      success: ''
    }
  },
  mounted() {
    this.getUserProfile()
  },
  methods: {
    async getUserProfile() {
      this.loading = true
      this.error = ''
      
      // 检查是否有有效的token
      const token = localStorage.getItem('token')
      console.log('当前token状态:', token ? '存在' : '不存在')
      if (!token) {
        this.error = '请先登录'
        this.loading = false
        return
      }
      
      try {
        console.log('开始获取用户个人信息...')
        const response = await this.$axios.get('/users/profile/')
        console.log('API响应数据:', response)
        console.log('响应类型:', typeof response)
        
        // 处理多种可能的响应格式
        let userData = null
        
        console.log('开始处理响应数据:', response)
        
        // 获取实际的响应数据（注意：axios拦截器已经提取了response.data）
        const actualData = response
        
        // 首先检查是否为错误响应
        if (actualData && actualData.detail) {
          console.log('检测到错误响应:', actualData.detail)
          throw new Error(actualData.detail)
        }
        
        // 格式1: 标准API格式 {code: 200, message: '...', data: {...用户信息...}}
        if (actualData && typeof actualData === 'object' && actualData.code === 200 && actualData.data) {
          console.log('匹配到标准API格式')
          console.log('data字段内容:', actualData.data)
          // 检查data是否包含用户信息的关键字段
          if (actualData.data.id && actualData.data.username) {
            userData = actualData.data
            console.log('✅ 使用标准格式的用户数据')
          }
        }
        // 格式2: 直接返回用户数据 {id: ..., username: ..., ...}
        else if (actualData && typeof actualData === 'object' && actualData.id && actualData.username) {
          userData = actualData
          console.log('✅ 使用直接格式的用户数据')
        }
        // 格式3: 包装在data字段中 {data: {id: ..., username: ...}}
        else if (actualData && typeof actualData === 'object' && actualData.data && 
                 typeof actualData.data === 'object' && actualData.data.id && actualData.data.username) {
          userData = actualData.data
          console.log('✅ 使用包装格式的用户数据')
        }
        // 格式4: 更灵活的data字段处理，只要data是对象就尝试使用
        else if (actualData && typeof actualData === 'object') {
          console.log('匹配到灵活格式，尝试使用实际数据')
          console.log('实际数据内容:', actualData)
          userData = actualData
          console.log('✅ 使用灵活格式的用户数据')
        }
        
        console.log('最终userData:', userData)
        
        if (userData) {
          this.user = userData
          console.log('✅ 用户信息获取成功:', this.user)
          // 初始化表单数据
          this.form = {
            email: this.user.email,
            phone: this.user.phone || '',
            avatar: this.user.avatar || '',
            address: this.user.address || '',
            bio: this.user.bio || ''
          }
        } else {
          console.error('❌ 无法识别的响应格式:', response)
          throw new Error('响应格式不符合预期')
        }
      } catch (error) {
        console.error('获取个人信息失败:', error)
        console.error('错误详情:', {
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data,
          message: error.message
        })
        
        // 显示用户友好的错误信息
        if (error.response?.status === 401) {
          this.error = '认证失败，请重新登录'
          // 清除无效的认证信息
          localStorage.removeItem('token')
          localStorage.removeItem('user')
        } else if (error.response?.status === 403) {
          this.error = '没有权限访问个人信息'
        } else if (error.message === 'Network Error') {
          this.error = '网络连接失败，请检查网络设置'
        } else {
          this.error = '获取个人信息失败：' + (error.message || '请稍后重试')
        }
      } finally {
        this.loading = false
        console.log('加载状态已设置为false')
      }
    },
    async updateProfile() {
      this.loading = true
      this.error = ''
      this.success = ''
      try {
        const response = await this.$axios.put('/users/profile/', this.form)
        console.log('更新个人信息响应:', response)
        const actualData = response
        // 处理多种可能的响应格式
        if (actualData && actualData.code === 200) {
          this.success = '资料更新成功'
          // 更新用户信息
          this.user = actualData.data
          // 退出编辑模式
          setTimeout(() => {
            this.editMode = false
            this.success = ''
          }, 2000)
        } else if (actualData) {
          // 直接使用data字段
          this.success = '资料更新成功'
          this.user = actualData
          setTimeout(() => {
            this.editMode = false
            this.success = ''
          }, 2000)
        } else {
          this.error = actualData?.message || '更新失败'
        }
      } catch (error) {
        console.error('更新个人信息失败:', error)
        this.error = error.response?.data?.message || '更新失败，请检查网络连接'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.profile {
  padding: 40px 0;
  background: linear-gradient(135deg, #fff8f0 0%, #ffeaa7 100%);
  min-height: 100vh;
}

.profile h2 {
  margin-bottom: 30px;
  font-size: 28px;
  color: #ff6b6b;
  background: linear-gradient(135deg, #ff6b6b 0%, #ff9a3d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-align: center;
}

.profile-content {
  background: linear-gradient(135deg, #ffffff 0%, #fff5e6 100%);
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 15px 40px rgba(255, 154, 61, 0.3);
  padding: 40px;
  border: 1px solid rgba(255, 154, 61, 0.1);
}

.profile-header {
  display: flex;
  gap: 30px;
  margin-bottom: 30px;
  padding-bottom: 30px;
  border-bottom: 1px solid #eee;
}

.avatar {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #ff9a3d;
  box-shadow: 0 0 0 4px rgba(255, 154, 61, 0.2);
}

.user-info h3 {
  font-size: 24px;
  margin: 0 0 10px;
  color: #ff6b6b;
  background: linear-gradient(135deg, #ff6b6b 0%, #ff9a3d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.user-info p {
  margin: 5px 0;
  color: #666;
  line-height: 1.5;
}

.profile-actions {
  margin-bottom: 30px;
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 30px;
  padding-top: 30px;
  border-top: 1px solid #eee;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: bold;
  color: #555;
}

.form-group input,
.form-group textarea {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  font-family: inherit;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #ff9a3d;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 10px;
}

.btn {
  padding: 10px 20px;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
  border: none;
}

.btn-primary {
  background-color: #ff9a3d;
  color: white;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff9a3d 100%);
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
}

.btn-primary:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.btn-secondary {
  background: linear-gradient(135deg, #ffffff 0%, #fff5e6 100%);
  color: #ff6b6b;
  border: 2px solid #ffcc99;
  box-shadow: 0 2px 8px rgba(255, 154, 61, 0.2);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #fff5e6 0%, #ffffff 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 154, 61, 0.3);
  border-color: #ff9a3d;
}

.btn-volunteer {
  background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
  color: white;
  border: none;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

.btn-volunteer:hover {
  background: linear-gradient(135deg, #388E3C 0%, #689F38 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
}

.volunteer-badge {
  padding: 10px 20px;
  background: linear-gradient(135deg, #E8F5E8 0%, #C8E6C9 100%);
  color: #2E7D32;
  border-radius: 20px;
  font-weight: bold;
  border: 2px solid #4CAF50;
}

.error-message {
  padding: 10px;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 4px;
  margin-top: 10px;
}

.success-message {
  padding: 10px;
  background-color: #e8f5e8;
  color: #2e7d32;
  border-radius: 4px;
  margin-top: 10px;
}

.loading {
  text-align: center;
  padding: 40px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.error-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.error-card {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  text-align: center;
  max-width: 400px;
  width: 100%;
}

.error-card h3 {
  color: #ff6b6b;
  margin-bottom: 15px;
}

.error-card p {
  color: #666;
  margin-bottom: 20px;
  line-height: 1.5;
}

.error-card .btn {
  margin: 5px;
}

@media (max-width: 768px) {
  .profile-content {
    padding: 20px;
  }
  
  .profile-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .profile-actions {
    flex-direction: column;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    text-align: center;
  }
}
</style>
