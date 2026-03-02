<template>
  <div class="shelter-adoptions">
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
        <router-link to="/shelter/adoptions" class="nav-item active">
          <i class="nav-icon">🏥</i>
          <span>领养审核</span>
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
        <h1>领养申请审核</h1>
        <div class="header-actions">
          <button class="btn btn-primary" @click="refreshApplications">
            <i class="btn-icon">🔄</i>
            刷新
          </button>
        </div>
      </div>
      
      <!-- 搜索和筛选 -->
      <div class="search-filter">
        <div class="search-box">
          <input type="text" placeholder="搜索申请人姓名或动物名称..." v-model="searchQuery" @input="searchApplications">
          <button class="btn btn-secondary">搜索</button>
        </div>
        <div class="filter-box">
          <select v-model="filterStatus" @change="filterApplications">
            <option value="">所有状态</option>
            <option value="pending">待审核</option>
            <option value="approved">审核通过</option>
            <option value="rejected">审核拒绝</option>
            <option value="completed">已领养</option>
            <option value="cancelled">已取消</option>
          </select>
        </div>
      </div>
      
      <!-- 领养申请列表 -->
      <div class="adoptions-list">
        <div class="adoption-card" v-for="app in filteredApplications" :key="app.id">
          <div class="adoption-header">
            <div class="adoption-info">
              <h3>{{ app.animal.name }}</h3>
              <p class="applicant-name">申请人: {{ app.applicant.username }}</p>
            </div>
            <div class="adoption-status" :class="app.status">
              {{ getStatusText(app.status) }}
            </div>
          </div>
          <div class="adoption-content">
            <div class="animal-info">
              <img :src="app.animal.images[0] || 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20animal%20portrait&image_size=square'" :alt="app.animal.name" class="animal-image">
              <div>
                <p>{{ getSpeciesText(app.animal.species) }} · {{ app.animal.breed }} · {{ app.animal.age }}个月</p>
                <p>{{ app.animal.description.substring(0, 100) }}...</p>
              </div>
            </div>
            <div class="application-info">
              <h4>申请信息</h4>
              <p><strong>申请原因：</strong>{{ app.application_reason }}</p>
              <p><strong>个人情况：</strong>{{ app.personal_info }}</p>
              <p><strong>联系电话：</strong>{{ app.contact_phone }}</p>
              <p><strong>联系地址：</strong>{{ app.contact_address }}</p>
            </div>
            <div class="review-info" v-if="app.reviewed_at">
              <h4>审核信息</h4>
              <p><strong>审核时间：</strong>{{ formatDate(app.reviewed_at) }}</p>
              <p><strong>审核人：</strong>{{ app.reviewer?.username }}</p>
              <p><strong>审核意见：</strong>{{ app.review_comments }}</p>
            </div>
          </div>
          <div class="adoption-actions" v-if="app.status === 'pending'">
            <button class="btn btn-sm btn-success" @click="approveApplication(app.id)">批准</button>
            <button class="btn btn-sm btn-danger" @click="rejectApplication(app.id)">拒绝</button>
            <button class="btn btn-sm btn-secondary" @click="viewApplicationDetails(app)">查看详情</button>
          </div>
          <div class="adoption-actions" v-else>
            <button class="btn btn-sm btn-secondary" @click="viewApplicationDetails(app)">查看详情</button>
          </div>
        </div>
        <div class="empty-state" v-if="filteredApplications.length === 0">
          <p>暂无领养申请</p>
        </div>
      </div>
      
      <!-- 领养申请详情模态框 -->
      <div class="modal" v-if="showDetailsModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>领养申请详情</h2>
            <button class="btn-close" @click="showDetailsModal = false">×</button>
          </div>
          <div class="modal-body">
            <div class="details-section">
              <h3>{{ selectedApplication.animal.name }}</h3>
              <div class="details-info">
                <span class="info-item">申请人: {{ selectedApplication.applicant.username }}</span>
                <span class="info-item">联系电话: {{ selectedApplication.contact_phone }}</span>
                <span class="info-item">联系地址: {{ selectedApplication.contact_address }}</span>
                <span class="info-item">状态: <span class="status-badge" :class="selectedApplication.status">{{ getStatusText(selectedApplication.status) }}</span></span>
              </div>
            </div>
            <div class="details-section">
              <h4>动物信息</h4>
              <div class="animal-details">
                <img :src="selectedApplication.animal.images[0] || 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20animal%20portrait&image_size=square'" :alt="selectedApplication.animal.name" class="animal-image">
                <div>
                  <p>{{ getSpeciesText(selectedApplication.animal.species) }} · {{ selectedApplication.animal.breed }} · {{ selectedApplication.animal.age }}个月</p>
                  <p>{{ selectedApplication.animal.description }}</p>
                </div>
              </div>
            </div>
            <div class="details-section">
              <h4>申请信息</h4>
              <p><strong>申请原因：</strong>{{ selectedApplication.application_reason }}</p>
              <p><strong>个人情况：</strong>{{ selectedApplication.personal_info }}</p>
            </div>
            <div class="details-section" v-if="selectedApplication.reviewed_at">
              <h4>审核信息</h4>
              <p><strong>审核时间：</strong>{{ formatDate(selectedApplication.reviewed_at) }}</p>
              <p><strong>审核人：</strong>{{ selectedApplication.reviewer?.username }}</p>
              <p><strong>审核意见：</strong>{{ selectedApplication.review_comments }}</p>
            </div>
            <div class="form-actions">
              <button class="btn btn-secondary" @click="showDetailsModal = false">关闭</button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 审核模态框 -->
      <div class="modal" v-if="showReviewModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>审核领养申请</h2>
            <button class="btn-close" @click="showReviewModal = false">×</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitReview">
              <div class="form-group">
                <label for="review_status">审核结果</label>
                <select id="review_status" v-model="reviewForm.status" required>
                  <option value="approved">批准</option>
                  <option value="rejected">拒绝</option>
                </select>
              </div>
              <div class="form-group">
                <label for="review_comments">审核意见</label>
                <textarea id="review_comments" v-model="reviewForm.comments" rows="4" required></textarea>
              </div>
              <div class="form-actions">
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  {{ loading ? '提交中...' : '提交审核' }}
                </button>
                <button type="button" class="btn btn-secondary" @click="showReviewModal = false">取消</button>
              </div>
            </form>
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
  name: 'ShelterAdoptions',
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user')) || {},
      applications: [],
      searchQuery: '',
      filterStatus: '',
      showDetailsModal: false,
      showReviewModal: false,
      selectedApplication: {
        id: '',
        animal: {
          id: '',
          name: '',
          species: '',
          breed: '',
          age: '',
          images: [],
          description: ''
        },
        applicant: {
          id: '',
          username: ''
        },
        application_reason: '',
        personal_info: '',
        contact_phone: '',
        contact_address: '',
        status: '',
        created_at: '',
        updated_at: '',
        reviewed_at: null,
        review_comments: null,
        reviewer: null
      },
      reviewForm: {
        status: 'approved',
        comments: ''
      },
      currentReviewId: null,
      loading: false,
      error: '',
      success: ''
    }
  },
  computed: {
    filteredApplications() {
      let result = [...this.applications]
      
      // 搜索
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        result = result.filter(app => 
          app.applicant.username.toLowerCase().includes(query) ||
          app.animal.name.toLowerCase().includes(query)
        )
      }
      
      // 状态筛选
      if (this.filterStatus) {
        result = result.filter(app => app.status === this.filterStatus)
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
    
    // 获取领养申请列表
    this.loadApplications()
  },
  methods: {
    async loadApplications() {
      try {
        const token = localStorage.getItem('token')
        const response = await this.$axios.get('/api/adoptions/applications/', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })
        
        if (response.data.code === 200) {
          this.applications = response.data.data
        } else {
          this.error = response.data.message || '获取申请列表失败'
        }
      } catch (error) {
        console.error('获取申请列表失败:', error)
        this.error = '获取申请列表失败，请稍后重试'
      }
    },
    
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.$router.push('/login')
    },
    getStatusText(status) {
      const statusMap = {
        'pending': '待审核',
        'approved': '审核通过',
        'rejected': '审核拒绝',
        'completed': '已领养',
        'cancelled': '已取消'
      }
      return statusMap[status] || status
    },
    getSpeciesText(species) {
      const speciesMap = {
        'dog': '狗',
        'cat': '猫',
        'other': '其他'
      }
      return speciesMap[species] || species
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
    refreshApplications() {
      this.loadApplications()
    },
    searchApplications() {
      // 搜索逻辑已在computed中处理
    },
    filterApplications() {
      // 筛选逻辑已在computed中处理
    },
    viewApplicationDetails(app) {
      this.selectedApplication = JSON.parse(JSON.stringify(app))
      this.showDetailsModal = true
    },
    openReviewModal(id) {
      this.currentReviewId = id
      this.reviewForm = {
        status: 'approved',
        comments: ''
      }
      this.showReviewModal = true
    },
    async approveApplication(id) {
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        const response = await this.$axios.put(`/adoptions/applications/${id}/approve/`, {
          review_comments: '审核通过'
        })
        if (response.code === 200) {
          // 批准成功
          const index = this.applications.findIndex(app => app.id === id)
          if (index !== -1) {
            this.applications[index] = response.data
          }
          this.success = '领养申请已批准'
          
          // 3秒后清除成功信息
          setTimeout(() => {
            this.success = ''
          }, 3000)
        } else {
          this.error = response.message || '批准失败'
        }
      } catch (error) {
        this.error = error.response?.data?.message || '批准失败，请检查网络连接'
      } finally {
        this.loading = false
      }
    },
    async rejectApplication(id) {
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        const response = await this.$axios.put(`/adoptions/applications/${id}/reject/`, {
          review_comments: '审核拒绝'
        })
        if (response.code === 200) {
          // 拒绝成功
          const index = this.applications.findIndex(app => app.id === id)
          if (index !== -1) {
            this.applications[index] = response.data
          }
          this.success = '领养申请已拒绝'
          
          // 3秒后清除成功信息
          setTimeout(() => {
            this.success = ''
          }, 3000)
        } else {
          this.error = response.message || '拒绝失败'
        }
      } catch (error) {
        this.error = error.response?.data?.message || '拒绝失败，请检查网络连接'
      } finally {
        this.loading = false
      }
    },
    async submitReview() {
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        const response = await this.$axios.put(`/adoptions/applications/${this.currentReviewId}/`, {
          status: this.reviewForm.status,
          review_comments: this.reviewForm.comments
        })
        if (response.code === 200) {
          // 提交成功
          const index = this.applications.findIndex(app => app.id === this.currentReviewId)
          if (index !== -1) {
            this.applications[index] = response.data
          }
          this.showReviewModal = false
          this.success = '审核已提交'
          
          // 3秒后清除成功信息
          setTimeout(() => {
            this.success = ''
          }, 3000)
        } else {
          this.error = response.message || '提交失败'
        }
      } catch (error) {
        this.error = error.response?.data?.message || '提交失败，请检查网络连接'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.shelter-adoptions {
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

/* 领养申请列表样式 */
.adoptions-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
  gap: 20px;
}

.adoption-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  padding: 20px;
  transition: all 0.3s ease;
}

.adoption-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.adoption-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.adoption-info {
  flex: 1;
}

.adoption-info h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
  color: #333;
}

.applicant-name {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.adoption-status {
  padding: 5px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  margin-left: 15px;
}

.adoption-status.pending {
  background-color: #fff3e0;
  color: #f57c00;
}

.adoption-status.approved {
  background-color: #e8f5e8;
  color: #388e3c;
}

.adoption-status.rejected {
  background-color: #ffebee;
  color: #c62828;
}

.adoption-status.completed {
  background-color: #e3f2fd;
  color: #1976d2;
}

.adoption-status.cancelled {
  background-color: #f5f5f5;
  color: #616161;
}

.adoption-content {
  margin-bottom: 20px;
}

.animal-info {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.animal-image {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
}

.animal-info div {
  flex: 1;
}

.animal-info p {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #666;
}

.application-info {
  margin-bottom: 20px;
}

.application-info h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #555;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 5px;
}

.application-info p {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}

.review-info {
  margin-bottom: 20px;
}

.review-info h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #555;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 5px;
}

.review-info p {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}

.adoption-actions {
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
  max-width: 700px;
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

.details-info {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
  font-size: 14px;
  color: #666;
}

.animal-details {
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
}

.animal-details .animal-image {
  width: 150px;
  height: 150px;
}

.animal-details div {
  flex: 1;
}

.animal-details p {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}

.details-section p {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #666;
  line-height: 1.4;
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

/* 表单样式 */
.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-size: 14px;
  font-weight: bold;
  color: #555;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #ff9a3d;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
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
  .shelter-adoptions {
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
  
  .adoptions-list {
    grid-template-columns: 1fr;
  }
  
  .adoption-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .adoption-status {
    margin-left: 0;
  }
  
  .animal-info {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .animal-details {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .details-info {
    flex-direction: column;
    gap: 10px;
  }
  
  .modal-content {
    width: 95%;
    max-height: 95vh;
  }
}
</style>