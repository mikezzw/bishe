<template>
  <div class="shelter-info">
    <!-- 侧边栏 -->
    <div class="sidebar">
      <div class="sidebar-header">
        <h2>基地管理</h2>
        <div class="user-info">
          <div class="user-avatar">
            {{ user?.username?.charAt(0) || 'S' }}
          </div>
          <div class="user-details">
            <p class="user-name">{{ user?.username }}</p>
            <p class="user-role">{{ user?.user_type === 'shelter' ? '基地管理员' : '普通用户' }}</p>
          </div>
        </div>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/shelter/dashboard" class="nav-item">
          <i class="nav-icon">📊</i>
          <span>概览</span>
        </router-link>
        <router-link to="/shelter/info" class="nav-item active">
          <i class="nav-icon">🏠</i>
          <span>基地信息</span>
        </router-link>
        <router-link to="/shelter/animals" class="nav-item">
          <i class="nav-icon">🐾</i>
          <span>基地宠物</span>
        </router-link>
        <router-link to="/shelter/activities" class="nav-item">
          <i class="nav-icon">📅</i>
          <span>活动管理</span>
        </router-link>
        <router-link to="/shelter/volunteers" class="nav-item">
          <i class="nav-icon">🤝</i>
          <span>志愿者管理</span>
        </router-link>
        <router-link to="/shelter/donations" class="nav-item">
          <i class="nav-icon">💰</i>
          <span>捐赠管理</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <button class="btn btn-secondary" @click="logout">退出登录</button>
      </div>
    </div>
    
    <!-- 主内容区域 -->
    <div class="main-content">
      <div class="content-header">
        <h1>基地信息</h1>
        <div class="header-actions">
          <button class="btn btn-primary" @click="toggleEdit" :disabled="loading">
            {{ isEditing ? '取消' : '编辑' }}
          </button>
          <button class="btn btn-success" @click="saveInfo" v-if="isEditing" :disabled="loading">
            {{ loading ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
      
      <div class="info-card">
        <div class="info-section">
          <h2>基本信息</h2>
          <form class="info-form" v-if="isEditing">
            <div class="form-group">
              <label for="name">基地名称</label>
              <input type="text" id="name" v-model="form.name" required>
            </div>
            <div class="form-group">
              <label for="address">基地地址</label>
              <input type="text" id="address" v-model="form.address" required>
            </div>
            <div class="form-group">
              <label for="contact_name">联系人姓名</label>
              <input type="text" id="contact_name" v-model="form.contact_name" required>
            </div>
            <div class="form-group">
              <label for="contact_phone">联系电话</label>
              <input type="tel" id="contact_phone" v-model="form.contact_phone" required>
            </div>
            <div class="form-group">
              <label for="email">电子邮箱</label>
              <input type="email" id="email" v-model="form.email" required>
            </div>
            <div class="form-group">
              <label for="capacity">容纳能力</label>
              <input type="number" id="capacity" v-model="form.capacity" min="1" required>
            </div>
          </form>
          <div class="info-display" v-else>
            <div class="info-item">
              <span class="info-label">基地名称:</span>
              <span class="info-value">{{ shelterInfo.name }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">基地地址:</span>
              <span class="info-value">{{ shelterInfo.address }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">联系人姓名:</span>
              <span class="info-value">{{ shelterInfo.contact_name }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">联系电话:</span>
              <span class="info-value">{{ shelterInfo.contact_phone }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">电子邮箱:</span>
              <span class="info-value">{{ shelterInfo.email }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">容纳能力:</span>
              <span class="info-value">{{ shelterInfo.capacity }} 只宠物</span>
            </div>
          </div>
        </div>
        
        <div class="info-section">
          <h2>基地描述</h2>
          <div v-if="isEditing">
            <textarea v-model="form.description" rows="5" placeholder="请输入基地描述"></textarea>
          </div>
          <div class="info-display" v-else>
            <p>{{ shelterInfo.description || '暂无描述' }}</p>
          </div>
        </div>
        
        <div class="info-section">
          <h2>基地状态</h2>
          <div class="info-display">
            <div class="info-item">
              <span class="info-label">创建时间:</span>
              <span class="info-value">{{ shelterInfo.created_at || '未知' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">更新时间:</span>
              <span class="info-value">{{ shelterInfo.updated_at || '未知' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">当前宠物数:</span>
              <span class="info-value">{{ shelterInfo.current_animals || 0 }} 只</span>
            </div>
            <div class="info-item">
              <span class="info-label">可领养宠物数:</span>
              <span class="info-value">{{ shelterInfo.available_animals || 0 }} 只</span>
            </div>
          </div>
        </div>
        
        <div class="info-section">
          <h2>基地活动</h2>
          <div v-if="loadingActivities" class="loading">
            <p>加载活动中...</p>
          </div>
          <div v-else-if="shelterActivities.length > 0" class="activities-list">
            <div class="activity-item" v-for="activity in shelterActivities" :key="activity.id">
              <div class="activity-header">
                <h3>{{ activity.name }}</h3>
                <span class="activity-status" :class="activity.status">
                  {{ getStatusText(activity.status) }}
                </span>
              </div>
              <div class="activity-details">
                <div class="detail-item">
                  <i class="icon">📍</i>
                  <span>{{ activity.location }}</span>
                </div>
                <div class="detail-item">
                  <i class="icon">⏰</i>
                  <span>{{ formatDate(activity.start_time) }}</span>
                </div>
                <div class="detail-item">
                  <i class="icon">👥</i>
                  <span>{{ (activity.participants || []).length }}/{{ activity.capacity }} 人</span>
                </div>
              </div>
              <div class="activity-actions">
                <router-link :to="`/volunteer/activities`" class="btn btn-outline">
                  查看详情
                </router-link>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <p>暂无活动</p>
          </div>
        </div>
      </div>
      
      <div class="error-message" v-if="error">
        {{ error }}
      </div>
      <div class="success-message" v-if="success">
        {{ success }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ShelterInfo',
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user')) || {},
      shelterInfo: {},
      shelterActivities: [],
      form: {
        name: '',
        description: '',
        address: '',
        contact_name: '',
        contact_phone: '',
        email: '',
        capacity: ''
      },
      isEditing: false,
      loading: false,
      loadingActivities: false,
      error: '',
      success: ''
    }
  },
  mounted() {
    // 检查用户是否已登录且为基地管理员或系统管理员
    if (!this.user || (this.user.user_type !== 'shelter' && this.user.user_type !== 'admin')) {
      this.$router.push('/login')
      return
    }
    
    // 加载基地信息和活动
    this.loadAllData()
  },
  methods: {
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.$router.push('/login')
    },
    async loadAllData() {
      try {
        // 先加载基地信息
        await this.loadShelterInfo()
        // 然后加载基地活动
        await this.loadShelterActivities()
      } catch (error) {
        console.error('加载数据失败:', error)
      }
    },
    async loadShelterInfo() {
      try {
        console.log('开始加载基地信息...')
        console.log('用户信息:', this.user)
        
        // 检查用户ID是否存在
        if (!this.user.id) {
          console.error('用户ID不存在')
          return
        }
        
        // 获取用户所属基地信息
        console.log('获取用户所属基地信息...')
        const userShelterResponse = await this.$axios.get(`/shelters/staff/user/${this.user.id}/shelter/`)
        console.log('用户基地信息响应:', userShelterResponse)
        
        if (userShelterResponse.code === 200 && userShelterResponse.data) {
          // 检查返回的是数组还是单个对象
          if (Array.isArray(userShelterResponse.data)) {
            // 如果是数组，优先选择用户在User模型中关联的基地
            if (this.user.shelter && this.user.shelter.id) {
              const userAssignedShelter = userShelterResponse.data.find(item => item.shelter.id === this.user.shelter.id)
              if (userAssignedShelter) {
                this.shelterInfo = userAssignedShelter.shelter
              } else if (userShelterResponse.data.length > 0) {
                // 如果没有找到用户关联的基地，选择第一个管理员角色的基地
                const managerShelter = userShelterResponse.data.find(item => item.role === 'manager')
                if (managerShelter) {
                  this.shelterInfo = managerShelter.shelter
                } else {
                  // 如果没有管理员角色，选择第一个基地
                  this.shelterInfo = userShelterResponse.data[0].shelter
                }
              }
            } else {
              // 如果用户没有关联基地，选择第一个管理员角色的基地
              const managerShelter = userShelterResponse.data.find(item => item.role === 'manager')
              if (managerShelter) {
                this.shelterInfo = managerShelter.shelter
              } else if (userShelterResponse.data.length > 0) {
                // 如果没有管理员角色，选择第一个基地
                this.shelterInfo = userShelterResponse.data[0].shelter
              }
            }
          } else {
            // 如果是单个对象，直接使用
            this.shelterInfo = userShelterResponse.data
          }
          console.log('基地信息加载完成:', this.shelterInfo)
          // 初始化表单数据
          this.initializeForm()
        } else {
          console.error('获取基地信息失败:', userShelterResponse)
        }
      } catch (error) {
        console.error('加载基地信息失败:', error)
        console.error('错误详情:', {
          message: error.message,
          stack: error.stack,
          response: error.response
        })
      }
    },
    toggleEdit() {
      this.isEditing = !this.isEditing
      if (this.isEditing) {
        this.initializeForm()
      }
      this.error = ''
      this.success = ''
    },
    initializeForm() {
      this.form = {
        name: this.shelterInfo.name,
        description: this.shelterInfo.description,
        address: this.shelterInfo.address,
        contact_name: this.shelterInfo.contact_name,
        contact_phone: this.shelterInfo.contact_phone,
        email: this.shelterInfo.email,
        capacity: this.shelterInfo.capacity
      }
    },
    async saveInfo() {
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        // 模拟API调用
        // const response = await this.$axios.put(`/shelters/${this.shelterInfo.id}/`, this.form)
        // if (response.code === 200) {
          // 保存成功
          this.shelterInfo = {
            ...this.shelterInfo,
            ...this.form,
            updated_at: new Date().toLocaleString()
          }
          this.isEditing = false
          this.success = '基地信息保存成功'
          
          // 3秒后清除成功信息
          setTimeout(() => {
            this.success = ''
          }, 3000)
        // } else {
        //   this.error = response.message || '保存失败'
        // }
      } catch (error) {
        this.error = error.response?.data?.message || '保存失败，请检查网络连接'
      } finally {
        this.loading = false
      }
    },
    async loadShelterActivities() {
      this.loadingActivities = true
      try {
        // 确保shelterInfo存在
        if (!this.shelterInfo || !this.shelterInfo.id) {
          console.error('基地信息中缺少ID')
          this.shelterActivities = []
          return
        }
        
        // 使用正确的API路径获取基地活动
        const response = await this.$axios.get(`/shelters/${this.shelterInfo.id}/activities/`)
        console.log('基地活动响应:', response)
        if (response.code === 200 && response.data) {
          if (response.data.results && Array.isArray(response.data.results)) {
            this.shelterActivities = response.data.results
          } else if (Array.isArray(response.data)) {
            this.shelterActivities = response.data
          }
        }
      } catch (error) {
        console.error('加载基地活动失败:', error)
        this.shelterActivities = []
      } finally {
        this.loadingActivities = false
      }
    },
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', {
        month: 'short',
        day: 'numeric'
      })
    },
    getStatusText(status) {
      const statusMap = {
        'planning': '策划中',
        'upcoming': '即将开始',
        'ongoing': '进行中',
        'completed': '已完成',
        'cancelled': '已取消'
      }
      return statusMap[status] || status
    }
  }
}
</script>
<style scoped>
.shelter-info {
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
}

/* 侧边栏样式 */
.sidebar {
  width: 280px;
  background-color: #ff9a3d;
  color: white;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 10px rgba(0,0,0,0.1);
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.sidebar-header h2 {
  margin: 0 0 20px 0;
  font-size: 20px;
  text-align: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: #3498db;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
}

.user-details {
  flex: 1;
}

.user-name {
  margin: 0 0 5px 0;
  font-weight: bold;
}

.user-role {
  margin: 0;
  font-size: 12px;
  opacity: 0.8;
}

.sidebar-nav {
  flex: 1;
  padding: 20px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: white;
  text-decoration: none;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background-color: rgba(255,255,255,0.1);
  border-left-color: #3498db;
}

.nav-item.active {
  background-color: rgba(255,255,255,0.15);
  border-left-color: #3498db;
  font-weight: bold;
}

.nav-icon {
  margin-right: 15px;
  font-size: 18px;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid rgba(255,255,255,0.1);
}

/* 主内容区域样式 */
.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.content-header h1 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 10px;
}

/* 信息卡片样式 */
.info-card {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 30px;
}

.info-section {
  margin-bottom: 30px;
}

.info-section h2 {
  margin: 0 0 20px 0;
  font-size: 18px;
  color: #333;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 10px;
}

/* 表单样式 */
.info-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-group label {
  font-size: 14px;
  font-weight: bold;
  color: #555;
}

.form-group input,
.form-group textarea {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #ff9a3d;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.form-group textarea {
  resize: vertical;
}

/* 信息显示样式 */
.info-display {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.info-label {
  font-weight: bold;
  color: #555;
  min-width: 100px;
}

.info-value {
  color: #333;
  flex: 1;
}

/* 按钮样式 */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background-color: #ff9a3d;
  color: white;
}

.btn-primary:hover {
  background-color: #45a049;
}

.btn-primary:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
}

.btn-secondary:hover {
  background-color: #e0e0e0;
}

.btn-success {
  background-color: #2196F3;
  color: white;
}

.btn-success:hover {
  background-color: #0b7dda;
}

.btn-success:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

/* 错误和成功信息样式 */
.error-message {
  background-color: #ffebee;
  color: #c62828;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.success-message {
  background-color: #e8f5e8;
  color: #388e3c;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .shelter-info {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    max-height: 200px;
  }
  
  .sidebar-nav {
    display: flex;
    overflow-x: auto;
    padding: 10px 0;
  }
  
  .nav-item {
    white-space: nowrap;
    padding: 10px 15px;
    border-left: none;
    border-bottom: 3px solid transparent;
  }
  
  .nav-item.active {
    border-left: none;
    border-bottom-color: #3498db;
  }
  
}

/* 活动列表样式 */
.activities-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 20px;
}

.activity-item {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #f0f0f0;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.activity-header h3 {
  margin: 0;
  font-size: 18px;
  color: #ff6b6b;
  flex: 1;
  margin-right: 15px;
}

.activity-status {
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  white-space: nowrap;
}

.activity-status.upcoming {
  background: #e3f2fd;
  color: #1976d2;
}

.activity-status.ongoing {
  background: #fff3e0;
  color: #f57c00;
}

.activity-status.completed {
  background: #e8f5e8;
  color: #388e3c;
}

.activity-status.cancelled {
  background: #ffebee;
  color: #d32f2f;
}

.activity-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
}

.detail-item .icon {
  font-size: 16px;
}

.activity-actions {
  display: flex;
  gap: 10px;
  border-top: 1px solid #f0f0f0;
  padding-top: 15px;
}

.btn-outline {
  background: transparent;
  color: #ff6b6b;
  border: 2px solid #ffcc99;
  border-radius: 8px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  flex: 1;
}

.btn-outline:hover {
  background: #fff5e6;
  border-color: #ff9a3d;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
  background: #f9f9f9;
  border-radius: 8px;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .info-label {
    min-width: 80px;
  }
  
  .activity-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .activity-actions {
    flex-direction: column;
  }
  
  .info-label {
    min-width: unset;
  }
}
</style>
