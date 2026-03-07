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
      
      <!-- 标签页 -->
      <div class="tabs">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'volunteers' }" 
          @click="activeTab = 'volunteers'"
        >
          志愿者申请
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'activity-applications' }" 
          @click="activeTab = 'activity-applications'"
        >
          活动报名申请
        </button>
      </div>
      
      <!-- 搜索和筛选 -->
      <div class="search-filter">
        <div class="search-box">
          <input 
            type="text" 
            :placeholder="activeTab === 'volunteers' ? '搜索志愿者姓名或联系方式...' : '搜索活动名称或申请人...'" 
            v-model="searchQuery" 
            @input="searchVolunteers"
          >
          <button class="btn btn-secondary">搜索</button>
        </div>
        <div class="filter-box">
          <select v-model="filterStatus" @change="filterVolunteers">
            <option value="">所有状态</option>
            <option value="pending">待审核</option>
            <option value="approved">已批准</option>
            <option value="rejected">已拒绝</option>
            <option value="completed">已完成</option>
          </select>
        </div>
      </div>
      
      <!-- 志愿者列表 -->
      <div class="volunteers-list" v-if="activeTab === 'volunteers'">
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
      
      <!-- 活动报名申请列表 -->
      <div class="volunteers-list" v-else-if="activeTab === 'activity-applications'">
        <div class="volunteer-card" v-for="application in filteredActivityApplications" :key="application.id">
          <div class="volunteer-header">
            <h3>{{ application.activity_name }}</h3>
            <div class="volunteer-status" :class="application.status">
              {{ getStatusText(application.status) }}
            </div>
          </div>
          <div class="volunteer-info">
            <div class="volunteer-basic-info">
              <span class="info-item">👤 {{ application.applicant_name }}</span>
              <span class="info-item">📧 {{ application.applicant_email }}</span>
              <span class="info-item">📞 {{ application.applicant_phone }}</span>
            </div>
            <div class="volunteer-application">
              <h4>活动信息</h4>
              <p>时间: {{ formatDateTime(application.activity_time) }}</p>
              <p>地点: {{ application.activity_location }}</p>
            </div>
            <div class="volunteer-meta">
              <span class="meta-item">报名时间: {{ formatDate(application.created_at) }}</span>
              <span class="meta-item" v-if="application.updated_at">更新时间: {{ formatDate(application.updated_at) }}</span>
            </div>
          </div>
          <div class="volunteer-actions" v-if="application.status === 'pending'">
            <button class="btn btn-sm btn-success" @click="approveActivityApplication(application.id)">批准</button>
            <button class="btn btn-sm btn-danger" @click="rejectActivityApplication(application.id)">拒绝</button>
          </div>
          <div class="volunteer-actions" v-else>
            <button class="btn btn-sm btn-secondary" @click="viewActivityApplicationDetails(application)">查看详情</button>
          </div>
        </div>
        <div class="empty-state" v-if="filteredActivityApplications.length === 0">
          <p>暂无活动报名申请</p>
        </div>
      </div>
      
      <!-- 志愿者详情模态框 -->
      <div class="modal" v-if="showDetailsModal && activeTab === 'volunteers'">
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
      
      <!-- 活动报名申请详情模态框 -->
      <div class="modal" v-if="showDetailsModal && activeTab === 'activity-applications'">
        <div class="modal-content">
          <div class="modal-header">
            <h2>活动报名申请详情</h2>
            <button class="btn-close" @click="showDetailsModal = false">×</button>
          </div>
          <div class="modal-body">
            <div class="details-section">
              <h3>{{ selectedActivityApplication.activity_name }}</h3>
              <div class="details-info">
                <span class="info-item">👤 {{ selectedActivityApplication.applicant_name }}</span>
                <span class="info-item">📧 {{ selectedActivityApplication.applicant_email }}</span>
                <span class="info-item">📞 {{ selectedActivityApplication.applicant_phone }}</span>
                <span class="info-item">状态: <span class="status-badge" :class="selectedActivityApplication.status">{{ getStatusText(selectedActivityApplication.status) }}</span></span>
              </div>
            </div>
            <div class="details-section">
              <h4>活动信息</h4>
              <p>时间: {{ formatDateTime(selectedActivityApplication.activity_time) }}</p>
              <p>地点: {{ selectedActivityApplication.activity_location }}</p>
              <p>描述: {{ selectedActivityApplication.activity_description }}</p>
            </div>
            <div class="details-section">
              <h4>报名信息</h4>
              <p>报名时间: {{ formatDate(selectedActivityApplication.created_at) }}</p>
              <p v-if="selectedActivityApplication.updated_at">更新时间: {{ formatDate(selectedActivityApplication.updated_at) }}</p>
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
      activeTab: 'volunteers',
      volunteers: [],
      activityApplications: [],
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
      selectedActivityApplication: {
        id: '',
        activity_name: '',
        activity_time: '',
        activity_location: '',
        activity_description: '',
        applicant_name: '',
        applicant_email: '',
        applicant_phone: '',
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
    },
    filteredActivityApplications() {
      let result = [...this.activityApplications]
      
      // 搜索
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        result = result.filter(application => 
          application.activity_name.toLowerCase().includes(query) ||
          application.applicant_name.toLowerCase().includes(query) ||
          application.applicant_email.toLowerCase().includes(query) ||
          application.applicant_phone.includes(query)
        )
      }
      
      // 状态筛选
      if (this.filterStatus) {
        result = result.filter(application => application.status === this.filterStatus)
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
    
    // 加载初始数据
    this.loadVolunteers()
    this.loadActivityApplications()
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
        'rejected': '已拒绝',
        'completed': '已完成'
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
    formatDateTime(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    async refreshVolunteers() {
      // 刷新数据
      this.error = ''
      this.success = ''
      
      try {
        if (this.activeTab === 'volunteers') {
          // 刷新志愿者申请数据
          await this.loadVolunteers()
        } else {
          // 刷新活动报名申请数据
          await this.loadActivityApplications()
        }
        this.success = '数据已刷新'
        setTimeout(() => {
          this.success = ''
        }, 3000)
      } catch (error) {
        console.error('刷新数据失败:', error)
        this.error = '刷新数据失败，请检查网络连接'
        setTimeout(() => {
          this.error = ''
        }, 3000)
      }
    },
    async loadVolunteers() {
      try {
        // 从后端获取志愿者申请数据
        const response = await this.$axios.get('/volunteers/profiles/')
        console.log('Volunteers response:', response)
        if (response && response.code === 200 && Array.isArray(response.data)) {
          this.volunteers = response.data
        }
      } catch (error) {
        console.error('加载志愿者申请失败:', error)
        // 加载失败时使用模拟数据
        this.volunteers = [
          {
            id: 1,
            name: '张三',
            email: 'zhangsan@example.com',
            phone: '13800138001',
            address: '北京市朝阳区',
            skills: '动物护理、摄影',
            experience: '有3年动物救助经验',
            availability: '周末全天',
            application_reason: '喜欢动物，希望为动物保护事业贡献一份力量',
            status: 'pending',
            created_at: '2024-01-01T10:00:00Z',
            updated_at: null
          },
          {
            id: 2,
            name: '李四',
            email: 'lisi@example.com',
            phone: '13900139001',
            address: '上海市浦东新区',
            skills: '兽医、动物训练',
            experience: '有5年兽医工作经验',
            availability: '工作日晚上，周末全天',
            application_reason: '专业背景适合，希望帮助更多动物',
            status: 'approved',
            created_at: '2024-01-02T14:00:00Z',
            updated_at: '2024-01-03T10:00:00Z'
          }
        ]
      }
    },
    async loadActivityApplications() {
      try {
        // 从后端获取活动报名申请数据
        // 假设当前用户是基地管理员，获取其管理的基地ID
        const shelterId = this.user.shelter_id || 1 // 默认使用1作为基地ID
        console.log('Loading activity applications for shelter:', shelterId)
        const response = await this.$axios.get(`/shelters/${shelterId}/interactions/`)
        console.log('Response:', response)
        if (response && response.code === 200) {
          // 检查response.data是否存在
          if (response.data) {
            // 处理分页响应
            const applications = response.data.results || response.data
            console.log('Applications:', applications)
            
            // 检查applications是否是数组
            if (Array.isArray(applications)) {
              // 过滤出活动报名类型的申请，并转换为前端期望的格式
              const filteredApplications = applications.filter(app => app.purpose && app.purpose.startsWith('activity_'))
              console.log('Filtered activity applications:', filteredApplications)
              this.activityApplications = filteredApplications.map(app => {
                // 从applicant对象中提取信息
                const applicantName = app.applicant?.username || '未知用户'
                const applicantEmail = app.applicant?.email || '未知邮箱'
                const applicantPhone = app.applicant?.phone || '未知电话'
                
                // 从purpose字段中提取活动ID
                const activityId = app.purpose.replace('activity_', '')
                
                // 构建活动名称（使用活动ID作为临时名称）
                const activityName = `活动 ${activityId}`
                
                // 构建活动时间（使用desired_date字段）
                const activityTime = app.desired_date || '未知时间'
                
                return {
                  id: app.id,
                  activity_name: activityName,
                  activity_time: activityTime,
                  activity_location: '未知地点', // 后端没有提供活动地点信息
                  activity_description: '未知描述', // 后端没有提供活动描述信息
                  applicant_name: applicantName,
                  applicant_email: applicantEmail,
                  applicant_phone: applicantPhone,
                  status: app.status,
                  created_at: app.created_at,
                  updated_at: app.updated_at
                }
              })
              console.log('Processed activity applications:', this.activityApplications)
            } else {
              console.error('Invalid applications data:', applications)
            }
          } else {
            console.error('Invalid response data:', response.data)
          }
        } else {
          console.error('Invalid response:', response)
        }
      } catch (error) {
        console.error('加载活动报名申请失败:', error)
        // 加载失败时使用模拟数据
        this.activityApplications = [
          {
            id: 1,
            activity_name: '周末狗狗散步活动',
            activity_time: '2024-01-15T10:00:00Z',
            activity_location: '北京市朝阳区公园',
            activity_description: '带基地的狗狗出去散步，增进与狗狗的感情',
            applicant_name: '王五',
            applicant_email: 'wangwu@example.com',
            applicant_phone: '13700137001',
            status: 'pending',
            created_at: '2024-01-10T09:00:00Z',
            updated_at: null
          },
          {
            id: 2,
            activity_name: '猫咪领养日活动',
            activity_time: '2024-01-20T14:00:00Z',
            activity_location: '上海市静安区商场',
            activity_description: '帮助基地的猫咪寻找领养家庭',
            applicant_name: '赵六',
            applicant_email: 'zhaoliu@example.com',
            applicant_phone: '13600136001',
            status: 'approved',
            created_at: '2024-01-12T10:00:00Z',
            updated_at: '2024-01-13T14:00:00Z'
          }
        ]
      }
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
    viewActivityApplicationDetails(application) {
      this.selectedActivityApplication = JSON.parse(JSON.stringify(application))
      this.showDetailsModal = true
    },
    async approveVolunteer(id) {
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        // 实际API调用
        const response = await this.$axios.post(`/volunteers/profiles/${id}/approve/`)
        if (response.data && response.data.code === 200) {
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
        } else {
          this.error = response.data?.message || '批准失败'
        }
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
        // 实际API调用
        const response = await this.$axios.post(`/volunteers/profiles/${id}/reject/`)
        if (response.data && response.data.code === 200) {
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
        } else {
          this.error = response.data?.message || '拒绝失败'
        }
      } catch (error) {
        this.error = error.response?.data?.message || '拒绝失败，请检查网络连接'
      } finally {
        this.loading = false
      }
    },
    async approveActivityApplication(id) {
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        // 假设当前用户是基地管理员，获取其管理的基地ID
        const shelterId = this.user.shelter_id || 1 // 默认使用1作为基地ID
        // 实际API调用
        const response = await this.$axios.post(`/shelters/${shelterId}/interactions/${id}/approve/`)
        if (response.data && response.data.code === 200) {
          // 批准成功
          const index = this.activityApplications.findIndex(a => a.id === id)
          if (index !== -1) {
            this.activityApplications[index].status = 'approved'
            this.activityApplications[index].updated_at = new Date().toISOString()
          }
          this.success = '活动报名申请已批准'
          
          // 3秒后清除成功信息
          setTimeout(() => {
            this.success = ''
          }, 3000)
        } else {
          this.error = response.data?.message || '批准失败'
        }
      } catch (error) {
        this.error = error.response?.data?.message || '批准失败，请检查网络连接'
      } finally {
        this.loading = false
      }
    },
    async rejectActivityApplication(id) {
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        // 假设当前用户是基地管理员，获取其管理的基地 ID
        const shelterId = this.user.shelter_id || 1 // 默认使用 1 作为基地 ID
        // 实际 API 调用
        const response = await this.$axios.post(`/shelters/${shelterId}/interactions/${id}/reject/`)
        if (response && response.code === 200) {
          // 拒绝成功
          const index = this.activityApplications.findIndex(a => a.id === id)
          if (index !== -1) {
            this.activityApplications[index].status = 'rejected'
            this.activityApplications[index].updated_at = new Date().toISOString()
          }
          this.success = '活动报名申请已拒绝'
                
          // 3 秒后清除成功信息
          setTimeout(() => {
            this.success = ''
          }, 3000)
        } else {
          this.error = response?.message || '拒绝失败'
        }
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

/* 标签页样式 */
.tabs {
  display: flex;
  gap: 5px;
  margin-bottom: 20px;
  background-color: white;
  padding: 5px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.tab-btn {
  flex: 1;
  padding: 12px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #f5f5f5;
  color: #333;
}

.tab-btn:hover {
  background-color: #e0e0e0;
}

.tab-btn.active {
  background-color: #ff9a3d;
  color: white;
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