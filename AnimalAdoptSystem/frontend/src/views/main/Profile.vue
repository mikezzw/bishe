<template>
  <div class="profile">
    <div class="container">
      <h2>个人信息</h2>
      
      <div class="profile-content" v-if="user">
        <div class="profile-header">
          <div class="avatar-upload-container">
            <img :src="user.avatar || 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=user%20avatar%20portrait&image_size=square'" :alt="user.username" class="avatar">
            <button type="button" class="upload-avatar-btn" @click="$refs.avatarInput.click()" v-if="editMode">
              📷 更换头像
            </button>
            <input 
              ref="avatarInput" 
              type="file" 
              accept="image/*" 
              @change="handleAvatarUpload"
              style="display: none"
            >
          </div>
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
          <template v-if="user && user.user_type === 'normal'">
            <router-link to="/volunteer/apply" class="btn btn-volunteer">
              申请成为志愿者
            </router-link>
          </template>
          <template v-else-if="user && user.user_type === 'volunteer'">
            <span class="volunteer-badge">
              ✅ 志愿者身份
            </span>
          </template>
          <button @click="showFeedbackModal = true" class="btn btn-feedback">
            📝 意见反馈
          </button>
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
            <label for="avatar">头像</label>
            <div class="avatar-input-group">
              <input type="url" id="avatar" v-model="form.avatar" placeholder="或点击上方的相机按钮上传图片">
              <button type="button" class="btn btn-secondary" @click="$refs.avatarInput.click()">
                📷 选择图片
              </button>
            </div>
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
      
      <!-- 反馈模态框 -->
      <div class="modal-overlay" v-if="showFeedbackModal" @click.self="showFeedbackModal = false">
        <div class="modal-content feedback-modal">
          <div class="modal-header">
            <h2>📝 意见反馈</h2>
            <button class="close-btn" @click="showFeedbackModal = false">×</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitFeedback">
              <div class="form-group">
                <label for="feedback_type">反馈类型</label>
                <select id="feedback_type" v-model="feedbackForm.feedback_type" required>
                  <option value="suggestion">💡 建议</option>
                  <option value="complaint">⚠️ 投诉</option>
                  <option value="bug">🐛 Bug 反馈</option>
                  <option value="other">📋 其他</option>
                </select>
              </div>
              <div class="form-group">
                <label for="priority">优先级</label>
                <select id="priority" v-model="feedbackForm.priority" required>
                  <option value="low">低</option>
                  <option value="medium">中</option>
                  <option value="high">高</option>
                </select>
              </div>
              <div class="form-group">
                <label for="title">标题</label>
                <input type="text" id="title" v-model="feedbackForm.title" placeholder="请简要描述您的问题或建议" required>
              </div>
              <div class="form-group">
                <label for="content">详细内容</label>
                <textarea id="content" v-model="feedbackForm.content" rows="6" placeholder="请详细描述您的问题、建议或需求..." required></textarea>
              </div>
              <div class="form-group">
                <label for="contact_info">联系方式（选填）</label>
                <input type="text" id="contact_info" v-model="feedbackForm.contact_info" placeholder="手机号、邮箱或其他联系方式，方便我们回复您">
              </div>
              <div class="form-actions">
                <button type="submit" class="btn btn-primary" :disabled="submittingFeedback">
                  {{ submittingFeedback ? '提交中...' : '提交反馈' }}
                </button>
                <button type="button" class="btn btn-secondary" @click="showFeedbackModal = false">取消</button>
              </div>
            </form>
            
            <!-- 我的反馈记录 -->
            <div class="my-feedbacks" v-if="myFeedbacks.length > 0">
              <h3>我的反馈记录</h3>
              <div class="feedback-list">
                <div v-for="feedback in myFeedbacks" :key="feedback.id" class="feedback-item">
                  <div class="feedback-header">
                    <span class="feedback-type">{{ getFeedbackTypeText(feedback.feedback_type) }}</span>
                    <span class="feedback-status" :class="getStatusClass(feedback.status)">
                      {{ getFeedbackStatusText(feedback.status) }}
                    </span>
                    <span class="feedback-date">{{ new Date(feedback.created_at).toLocaleDateString() }}</span>
                  </div>
                  <h4 class="feedback-title">{{ feedback.title }}</h4>
                  <p class="feedback-content">{{ feedback.content }}</p>
                  <div v-if="feedback.admin_notes" class="admin-notes">
                    <strong>管理员回复：</strong>
                    <p>{{ feedback.admin_notes }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
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
      uploadingAvatar: false,
      loading: true,
      error: '',
      success: '',
      showFeedbackModal: false,
      feedbackForm: {
        feedback_type: 'suggestion',
        priority: 'medium',
        title: '',
        content: '',
        contact_info: ''
      },
      submittingFeedback: false,
      myFeedbacks: []
    }
  },
  mounted() {
    this.getUserProfile()
    // 打开模态框时加载反馈记录
    this.$watch('showFeedbackModal', (newVal) => {
      if (newVal) {
        this.loadMyFeedbacks()
      }
    })
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
          // 直接使用 data 字段
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
    },
    
    async handleAvatarUpload(event) {
      const file = event.target.files[0]
      if (!file) return
      
      // 验证文件类型
      if (!file.type.startsWith('image/')) {
        alert('请选择图片文件')
        return
      }
      
      // 验证文件大小 (2MB)
      if (file.size > 2 * 1024 * 1024) {
        alert('图片大小不能超过 2MB')
        return
      }
      
      this.uploadingAvatar = true
      
      try {
        // 转换为 base64
        const reader = new FileReader()
        reader.onload = async (e) => {
          try {
            const base64Avatar = e.target.result
            
            // 直接更新表单和显示
            this.form.avatar = base64Avatar
            this.user.avatar = base64Avatar
            
            // 保存到后端
            await this.updateProfile()
            
            this.success = '头像更新成功'
            setTimeout(() => {
              this.success = ''
            }, 3000)
          } catch (error) {
            console.error('头像上传失败:', error)
            alert('头像上传失败，请稍后重试')
          } finally {
            this.uploadingAvatar = false
          }
        }
        reader.readAsDataURL(file)
      } catch (error) {
        console.error('头像上传失败:', error)
        this.uploadingAvatar = false
        alert('头像上传失败，请稍后重试')
      }
      
      // 清空 input，允许重复选择同一文件
      event.target.value = ''
    },
    
    async submitFeedback() {
      if (!this.feedbackForm.title || !this.feedbackForm.content) {
        alert('请填写标题和内容')
        return
      }
      
      this.submittingFeedback = true
      try {
        const response = await this.$axios.post('/community/feedbacks/', this.feedbackForm)
        console.log('提交反馈响应:', response)
        
        if (response.code === 200) {
          alert('反馈提交成功，我们会尽快处理！')
          this.showFeedbackModal = false
          // 重置表单
          this.feedbackForm = {
            feedback_type: 'suggestion',
            priority: 'medium',
            title: '',
            content: '',
            contact_info: ''
          }
          // 加载我的反馈列表
          this.loadMyFeedbacks()
        } else {
          alert('反馈提交失败：' + (response.message || '请稍后重试'))
        }
      } catch (error) {
        console.error('提交反馈失败:', error)
        alert('反馈提交失败，请稍后重试')
      } finally {
        this.submittingFeedback = false
      }
    },
    
    async loadMyFeedbacks() {
      try {
        const response = await this.$axios.get('/community/feedbacks/my-feedbacks/')
        console.log('获取我的反馈响应:', response)
        
        if (response.code === 200) {
          this.myFeedbacks = response.data || []
        }
      } catch (error) {
        console.error('获取反馈记录失败:', error)
      }
    },
    
    getFeedbackTypeText(type) {
      const typeMap = {
        'complaint': '投诉',
        'suggestion': '建议',
        'bug': 'Bug 反馈',
        'other': '其他'
      }
      return typeMap[type] || type
    },
    
    getFeedbackStatusText(status) {
      const statusMap = {
        'pending': '待处理',
        'reviewing': '处理中',
        'resolved': '已解决',
        'dismissed': '已驳回'
      }
      return statusMap[status] || status
    },
    
    getStatusClass(status) {
      const classMap = {
        'pending': 'status-pending',
        'reviewing': 'status-reviewing',
        'resolved': 'status-resolved',
        'dismissed': 'status-dismissed'
      }
      return classMap[status] || ''
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

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 20px;
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
  justify-content: center;
  align-items: center;
}

.avatar {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #ff9a3d;
  box-shadow: 0 0 0 4px rgba(255, 154, 61, 0.2);
}

.avatar-upload-container {
  position: relative;
  display: inline-block;
}

.upload-avatar-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  background: linear-gradient(135deg, #ff9a3d 0%, #ff6b6b 100%);
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(255, 154, 61, 0.3);
}

.upload-avatar-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(255, 154, 61, 0.5);
}

.avatar-input-group {
  display: flex;
  gap: 10px;
  align-items: center;
}

.avatar-input-group input {
  flex: 1;
}

.avatar-upload-container {
  position: relative;
  display: inline-block;
}

.upload-avatar-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  background: linear-gradient(135deg, #ff9a3d 0%, #ff6b6b 100%);
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(255, 154, 61, 0.3);
}

.upload-avatar-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(255, 154, 61, 0.5);
}

.avatar-input-group {
  display: flex;
  gap: 10px;
  align-items: center;
}

.avatar-input-group input {
  flex: 1;
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
  justify-content: center;
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

.btn-feedback {
  background: linear-gradient(135deg, #9C27B0 0%, #BA68C8 100%);
  color: white;
  border: none;
  box-shadow: 0 2px 8px rgba(156, 39, 176, 0.3);
}

.btn-feedback:hover {
  background: linear-gradient(135deg, #7B1FA2 0%, #AB47BC 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(156, 39, 176, 0.4);
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

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content.feedback-modal {
  background: white;
  border-radius: 15px;
  width: 90%;
  max-width: 700px;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { 
    opacity: 0;
    transform: translateY(30px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  color: #ff6b6b;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 5px;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #f5f5f5;
  color: #333;
}

.modal-body {
  padding: 20px;
}

.my-feedbacks {
  margin-top: 30px;
  padding-top: 30px;
  border-top: 2px solid #eee;
}

.my-feedbacks h3 {
  color: #ff6b6b;
  margin-bottom: 20px;
}

.feedback-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.feedback-item {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 10px;
  border-left: 4px solid #ff9a3d;
}

.feedback-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 10px;
}

.feedback-type {
  padding: 5px 12px;
  border-radius: 20px;
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
  color: #ef6c00;
  font-weight: bold;
  font-size: 0.85rem;
}

.feedback-status {
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: bold;
}

.feedback-status.status-pending {
  background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
  color: #c62828;
}

.feedback-status.status-reviewing {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  color: #1565c0;
}

.feedback-status.status-resolved {
  background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
  color: #2e7d32;
}

.feedback-status.status-dismissed {
  background: linear-gradient(135deg, #f5f5f5 0%, #eeeeee 100%);
  color: #616161;
}

.feedback-date {
  font-size: 0.85rem;
  color: #999;
}

.feedback-title {
  margin: 10px 0;
  color: #333;
  font-size: 1.1rem;
}

.feedback-content {
  color: #666;
  line-height: 1.6;
  margin: 10px 0;
}

.admin-notes {
  margin-top: 15px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  border-left: 3px solid #4CAF50;
}

.admin-notes strong {
  color: #4CAF50;
  display: block;
  margin-bottom: 5px;
}

.admin-notes p {
  color: #555;
  margin: 0;
  line-height: 1.5;
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
