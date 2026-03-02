<template>
  <div class="shelter-volunteers">
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
        <router-link to="/shelter/info" class="nav-item">
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
        <router-link to="/shelter/volunteers" class="nav-item active">
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
        <h1>志愿者管理</h1>
        <div class="header-actions">
          <button class="btn btn-primary" @click="refreshVolunteers">
            <i class="btn-icon">🔄</i>
            刷新
          </button>
        </div>
      </div>
      
      <!-- 搜索和筛选 -->
      <div class="search-filter">
        <div class="search-box">
          <input type="text" placeholder="搜索志愿者姓名或联系方式..." v-model="searchQuery" @input="searchVolunteers">
          <button class="btn btn-secondary">搜索</button>
        </div>
        <div class="filter-box">
          <select v-model="filterStatus" @change="filterVolunteers">
            <option value="">所有状态</option>
            <option value="pending">待审核</option>
            <option value="approved">已批准</option>
            <option value="rejected">已拒绝</option>
          </select>
        </div>
      </div>
      
      <!-- 志愿者列表 -->
      <div class="volunteers-list">
        <div class="volunteer-card" v-for="volunteer in filteredVolunteers" :key="volunteer.id">
          <div class="volunteer-header">
            <h3>{{ volunteer.name }}</h3>
            <div class="volunteer-status" :class="volunteer.status">
              {{ getStatusText(volunteer.status) }}
            </div>
          </div>
          <div class="volunteer-info">
            <div class="volunteer-basic-info">
              <span class="info-item">📧 {{ volunteer.email }}</span>
              <span class="info-item">📞 {{ volunteer.phone }}</span>
              <span class="info-item">📍 {{ volunteer.address }}</span>
            </div>
            <div class="volunteer-skills">
              <h4>技能/特长</h4>
              <p>{{ volunteer.skills || '无' }}</p>
            </div>
            <div class="volunteer-experience">
              <h4>相关经验</h4>
              <p>{{ volunteer.experience || '无' }}</p>
            </div>
            <div class="volunteer-availability">
              <h4>可用时间</h4>
              <p>{{ volunteer.availability || '无' }}</p>
            </div>
            <div class="volunteer-application">
              <h4>申请原因</h4>
              <p>{{ volunteer.application_reason || '无' }}</p>
            </div>
            <div class="volunteer-meta">
              <span class="meta-item">申请时间: {{ formatDate(volunteer.created_at) }}</span>
              <span class="meta-item" v-if="volunteer.updated_at">更新时间: {{ formatDate(volunteer.updated_at) }}</span>
            </div>
          </div>
          <div class="volunteer-actions" v-if="volunteer.status === 'pending'">
            <button class="btn btn-sm btn-success" @click="approveVolunteer(volunteer.id)">批准</button>
            <button class="btn btn-sm btn-danger" @click="rejectVolunteer(volunteer.id)">拒绝</button>
          </div>
          <div class="volunteer-actions" v-else>
            <button class="btn btn-sm btn-secondary" @click="viewVolunteerDetails(volunteer)">查看详情</button>
          </div>
        </div>
        <div class="empty-state" v-if="filteredVolunteers.length === 0">
          <p>暂无志愿者申请</p>
        </div>
      </div>
      
      <!-- 志愿者详情模态框 -->
      <div class="modal" v-if="showDetailsModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>志愿者详情</h2>
            <button class="btn-close" @click="showDetailsModal = false">×</button>
          </div>
          <div class="modal-body">
            <div class="details-section">
              <h3>{{ selectedVolunteer.name }}</h3>
              <div class="details-info">
                <span class="info-item">📧 {{ selectedVolunteer.email }}</span>
                <span class="info-item">📞 {{ selectedVolunteer.phone }}</span>
                <span class="info-item">📍 {{ selectedVolunteer.address }}</span>
                <span class="info-item">状态: <span class="status-badge" :class="selectedVolunteer.status">{{ getStatusText(selectedVolunteer.status) }}</span></span>
              </div>
            </div>
            <div class="details-section">
              <h4>技能/特长</h4>
              <p>{{ selectedVolunteer.skills || '无' }}</p>
            </div>
            <div class="details-section">
              <h4>相关经验</h4>
              <p>{{ selectedVolunteer.experience || '无' }}</p>
            </div>
            <div class="details-section">
              <h4>可用时间</h4>
              <p>{{ selectedVolunteer.availability || '无' }}</p>
            </div>
            <div class="details-section">
              <h4>申请原因</h4>
              <p>{{ selectedVolunteer.application_reason || '无' }}</p>
            </div>
            <div class="details-section">
              <h4>申请时间</h4>
              <p>{{ formatDate(selectedVolunteer.created_at) }}</p>
              <p v-if="selectedVolunteer.updated_at">更新时间: {{ formatDate(selectedVolunteer.updated_at) }}</p>
            </div>
            <div class="form-actions">
              <button class="btn btn-secondary" @click="showDetailsModal = false">关闭</button>
            </div>
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
  name: 'ShelterVolunteers',
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user')) || {},
      volunteers: [],
      searchQuery: '',
      filterStatus: '',
      showDetailsModal: false,
      selectedVolunteer: {
        id: '',
        name: '',
        email: '',
        phone: '',
        address: '',
        skills: '',
        experience: '',
        availability: '',
        application_reason: '',
        status: '',
        created_at: '',
        updated_at: ''
      },
      loading: false,
      error: '',
      success: ''
    }
  },
  computed: {
    filteredVolunteers() {
      let result = [...this.volunteers]
      
      // 搜索
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        result = result.filter(volunteer => 
          volunteer.name.toLowerCase().includes(query) ||
          volunteer.email.toLowerCase().includes(query) ||
          volunteer.phone.includes(query)
        )
      }
      
      // 状态筛选
      if (this.filterStatus) {
        result = result.filter(volunteer => volunteer.status === this.filterStatus)
      }
      
      return result
    }
  },
  mounted() {
    // 检查用户是否已登录且为基地管理员
    if (!this.user || this.user.user_type !== 'shelter') {
      this.$router.push('/login')
      return
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.$router.push('/login')
    },
    getStatusText(status) {
      const statusMap = {
        'pending': '待审核',
        'approved': '已批准',
        'rejected': '已拒绝'
      }
      return statusMap[status] || status
    },
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    refreshVolunteers() {
      // 模拟刷新数据
      this.error = ''
      this.success = ''
      // 这里可以添加实际的API调用
      this.success = '数据已刷新'
      setTimeout(() => {
        this.success = ''
      }, 3000)
    },
    searchVolunteers() {
      // 搜索逻辑已在computed中处理
    },
    filterVolunteers() {
      // 筛选逻辑已在computed中处理
    },
    viewVolunteerDetails(volunteer) {
      this.selectedVolunteer = JSON.parse(JSON.stringify(volunteer))
      this.showDetailsModal = true
    },
    async approveVolunteer(id) {
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        // 模拟API调用
        // const response = await this.$axios.put(`/volunteers/${id}/approve/`)
        // if (response.code === 200) {
          // 批准成功
          const index = this.volunteers.findIndex(v => v.id === id)
          if (index !== -1) {
            this.volunteers[index].status = 'approved'
            this.volunteers[index].updated_at = new Date().toISOString()
          }
          this.success = '志愿者申请已批准'
          
          // 3秒后清除成功信息
          setTimeout(() => {
            this.success = ''
          }, 3000)
        // } else {
        //   this.error = response.message || '批准失败'
        // }
      } catch (error) {
        this.error = error.response?.data?.message || '批准失败，请检查网络连接'
      } finally {
        this.loading = false
      }
    },
    async rejectVolunteer(id) {
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        // 模拟API调用
        // const response = await this.$axios.put(`/volunteers/${id}/reject/`)
        // if (response.code === 200) {
          // 拒绝成功
          const index = this.volunteers.findIndex(v => v.id === id)
          if (index !== -1) {
            this.volunteers[index].status = 'rejected'
            this.volunteers[index].updated_at = new Date().toISOString()
          }
          this.success = '志愿者申请已拒绝'
          
          // 3秒后清除成功信息
          setTimeout(() => {
            this.success = ''
          }, 3000)
        // } else {
        //   this.error = response.message || '拒绝失败'
        // }
      } catch (error) {
        this.error = error.response?.data?.message || '拒绝失败，请检查网络连接'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.shelter-volunteers {
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

/* 搜索和筛选样式 */
.search-filter {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 15px;
}

.search-box {
  display: flex;
  gap: 10px;
  flex: 1;
  min-width: 300px;
}

.search-box input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.search-box input:focus {
  outline: none;
  border-color: #ff9a3d;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

.filter-box {
  display: flex;
  gap: 10px;
  align-items: center;
}

.filter-box select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  min-width: 150px;
}

.filter-box select:focus {
  outline: none;
  border-color: #ff9a3d;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
}

/* 志愿者列表样式 */
.volunteers-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.volunteer-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  padding: 20px;
  transition: all 0.3s ease;
}

.volunteer-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.volunteer-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.volunteer-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
  flex: 1;
}

.volunteer-status {
  padding: 5px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  margin-left: 15px;
}

.volunteer-status.pending {
  background-color: #fff3e0;
  color: #f57c00;
}

.volunteer-status.approved {
  background-color: #e8f5e8;
  color: #388e3c;
}

.volunteer-status.rejected {
  background-color: #ffebee;
  color: #c62828;
}

.volunteer-info {
  margin-bottom: 20px;
}

.volunteer-basic-info {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
  font-size: 14px;
  color: #666;
}

.info-item {
  display: inline-block;
}

.volunteer-skills,
.volunteer-experience,
.volunteer-availability,
.volunteer-application {
  margin-bottom: 15px;
}

.volunteer-skills h4,
.volunteer-experience h4,
.volunteer-availability h4,
.volunteer-application h4 {
  margin: 0 0 5px 0;
  font-size: 14px;
  font-weight: bold;
  color: #555;
}

.volunteer-skills p,
.volunteer-experience p,
.volunteer-availability p,
.volunteer-application p {
  margin: 0;
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}

.volunteer-meta {
  display: flex;
  flex-direction: column;
  gap: 5px;
  font-size: 12px;
  color: #999;
  margin-top: 10px;
}

.meta-item {
  display: inline-block;
}

.volunteer-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

/* 模态框样式 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 5px 25px rgba(0,0,0,0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.btn-close:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.details-section {
  margin-bottom: 20px;
}

.details-section h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #333;
}

.details-section h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #555;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 5px;
}

.details-section p {
  margin: 0;
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}

.details-info {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
  font-size: 14px;
  color: #666;
}

.status-badge {
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.status-badge.pending {
  background-color: #fff3e0;
  color: #f57c00;
}

.status-badge.approved {
  background-color: #e8f5e8;
  color: #388e3c;
}

.status-badge.rejected {
  background-color: #ffebee;
  color: #c62828;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
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
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-sm {
  padding: 5px 10px;
  font-size: 12px;
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

.btn-danger {
  background-color: #f44336;
  color: white;
}

.btn-danger:hover {
  background-color: #da190b;
}

.btn-icon {
  font-size: 16px;
}

/* 空状态样式 */
.empty-state {
  background-color: white;
  padding: 60px 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  text-align: center;
  color: #999;
  font-size: 16px;
}

/* 错误和成功信息样式 */
.error-message {
  background-color: #ffebee;
  color: #c62828;
  padding: 10px;
  border-radius: 4px;
  margin-top: 20px;
}

.success-message {
  background-color: #e8f5e8;
  color: #388e3c;
  padding: 10px;
  border-radius: 4px;
  margin-top: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .shelter-volunteers {
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
  
  .search-filter {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    min-width: unset;
  }
  
  .filter-box {
    justify-content: space-between;
  }
  
  .volunteers-list {
    grid-template-columns: 1fr;
  }
  
  .volunteer-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .volunteer-status {
    margin-left: 0;
  }
  
  .volunteer-basic-info {
    flex-direction: column;
    gap: 10px;
  }
  
  .modal-content {
    width: 95%;
    max-height: 95vh;
  }
  
  .details-info {
    flex-direction: column;
    gap: 10px;
  }
}
</style>