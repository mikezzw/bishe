<template>
  <div class="shelter-dashboard">
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
        <router-link to="/shelter/dashboard" class="nav-item active">
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
        <h1>基地概览</h1>

      </div>
      
      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">🐶</div>
          <div class="stat-content">
            <h3>总宠物数</h3>
            <p class="stat-value">{{ stats.totalAnimals }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🏠</div>
          <div class="stat-content">
            <h3>可领养宠物</h3>
            <p class="stat-value">{{ stats.availableAnimals }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📅</div>
          <div class="stat-content">
            <h3>活动数</h3>
            <p class="stat-value">{{ stats.totalActivities }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">💰</div>
          <div class="stat-content">
            <h3>捐赠总额</h3>
            <p class="stat-value">¥{{ stats.totalDonations }}</p>
          </div>
        </div>
      </div>
      
      <!-- 最近活动 -->
      <div class="recent-activities">
        <h2>最近活动</h2>
        <div class="activity-list">
          <div class="activity-item" v-for="activity in recentActivities" :key="activity.id">
            <div class="activity-icon">📅</div>
            <div class="activity-content">
              <h4>{{ activity.title }}</h4>
              <p>{{ activity.description }}</p>
              <p class="activity-date">{{ activity.start_time }}</p>
            </div>
            <div class="activity-status" :class="activity.status">
              {{ activity.status === 'upcoming' ? '即将开始' : activity.status === 'ongoing' ? '进行中' : '已结束' }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ShelterDashboard',
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user')) || {},
      stats: {
        totalAnimals: 0,
        availableAnimals: 0,
        totalActivities: 0,
        totalDonations: 0
      },
      recentActivities: [],
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.$router.push('/login')
    },
    async loadDashboardData() {
      try {
        console.log('开始加载基地数据...')
        console.log('用户信息:', this.user)
        
        // 检查用户ID是否存在
        if (!this.user.id) {
          console.error('用户ID不存在')
          return
        }
        
        // 检查用户是否为基地类型或系统管理员
        if (this.user.user_type !== 'shelter' && this.user.user_type !== 'admin') {
          console.error('用户不是基地类型或系统管理员')
          return
        }
        
        // 尝试获取用户所属基地信息
        console.log('获取用户所属基地信息...')
        try {
          const userShelterResponse = await this.$axios.get(`/shelters/staff/user/${this.user.id}/shelter/`)
          console.log('用户基地信息响应:', userShelterResponse)
          
          // 检查响应格式
          if (userShelterResponse.code === 200) {
            // userShelterResponse.data 是一个数组，包含用户的所有基地记录
            console.log('用户基地记录:', userShelterResponse.data)
            // 获取第一个基地的 ID
            const shelterId = userShelterResponse.data[0].shelter.id
            console.log('获取到基地ID:', shelterId)
            
            // 并行获取各项数据
            console.log('并行获取各项数据...')
            try {
              const [animalsResponse, activitiesResponse, donationsResponse] = await Promise.all([
                this.$axios.get(`/animals/?shelter=${shelterId}`),
                this.$axios.get(`/shelters/${shelterId}/activities/`),
                this.$axios.get(`/shelters/${shelterId}/donations/`)
              ])
              
              console.log('宠物数据响应:', animalsResponse)
              console.log('活动数据响应:', activitiesResponse)
              console.log('捐赠数据响应:', donationsResponse)
              
              // 处理宠物数据
              if (animalsResponse.code === 200) {
                const shelterAnimals = animalsResponse.data.results || animalsResponse.data || []
                this.stats.totalAnimals = shelterAnimals.length
                this.stats.availableAnimals = shelterAnimals.filter(animal => animal.status === 'available').length
              }
              
              // 处理活动数据
              if (activitiesResponse.code === 200) {
                const activities = activitiesResponse.data.results || activitiesResponse.data || []
                this.stats.totalActivities = activities.length
                this.recentActivities = activities.slice(0, 5)
              }
              
              // 处理捐赠数据
              if (donationsResponse.code === 200) {
                const donations = donationsResponse.data.results || donationsResponse.data || []
                this.stats.totalDonations = donations.reduce((total, donation) => total + (donation.amount || 0), 0)
              }
              
              console.log('数据加载完成:', this.stats)
            } catch (apiError) {
              console.error('获取API数据失败:', apiError)
            }
          } else {
            console.error('获取基地信息失败:', userShelterResponse)
          }
        } catch (shelterError) {
          console.error('获取基地信息失败:', shelterError)
          // 如果用户未关联基地，尝试使用用户对象中的shelter字段
          if (this.user.shelter) {
            console.log('使用用户对象中的shelter字段:', this.user.shelter)
            const shelterId = this.user.shelter.id || this.user.shelter
            
            // 并行获取各项数据
            console.log('并行获取各项数据...')
            try {
              const [animalsResponse, activitiesResponse, donationsResponse] = await Promise.all([
                this.$axios.get(`/animals/?shelter=${shelterId}`),
                this.$axios.get(`/shelters/${shelterId}/activities/`),
                this.$axios.get(`/shelters/${shelterId}/donations/`)
              ])
              
              console.log('宠物数据响应:', animalsResponse)
              console.log('活动数据响应:', activitiesResponse)
              console.log('捐赠数据响应:', donationsResponse)
              
              // 处理宠物数据
              if (animalsResponse.code === 200) {
                const shelterAnimals = animalsResponse.data.results || animalsResponse.data || []
                this.stats.totalAnimals = shelterAnimals.length
                this.stats.availableAnimals = shelterAnimals.filter(animal => animal.status === 'available').length
              }
              
              // 处理活动数据
              if (activitiesResponse.code === 200) {
                const activities = activitiesResponse.data.results || activitiesResponse.data || []
                this.stats.totalActivities = activities.length
                this.recentActivities = activities.slice(0, 5)
              }
              
              // 处理捐赠数据
              if (donationsResponse.code === 200) {
                const donations = donationsResponse.data.results || donationsResponse.data || []
                this.stats.totalDonations = donations.reduce((total, donation) => total + (donation.amount || 0), 0)
              }
              
              console.log('数据加载完成:', this.stats)
            } catch (apiError) {
              console.error('获取API数据失败:', apiError)
            }
          }
        }
      } catch (error) {
        console.error('加载数据失败:', error)
        console.error('错误详情:', {
          message: error.message,
          stack: error.stack,
          response: error.response
        })
      }
    }
  },
  mounted() {
    // 检查用户是否已登录且为基地管理员或系统管理员
    if (!this.user || (this.user.user_type !== 'shelter' && this.user.user_type !== 'admin')) {
      this.$router.push('/login')
    } else {
      // 加载数据
      this.loadDashboardData()
    }
  }
}
</script>
<style scoped>
.shelter-dashboard {
  display: flex;
  min-height: 100vh;
  background: linear-gradient(135deg, #fff8f0 0%, #ffeaa7 100%);
}

/* 侧边栏样式 */
.sidebar {
  width: 280px;
  background: linear-gradient(135deg, #ff9a3d 0%, #ff6b6b 100%);
  color: white;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 15px rgba(255, 154, 61, 0.3);
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
  background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 100%);
  border-left-color: #ffcc99;
  transform: translateX(5px);
}

.nav-item.active {
  background: linear-gradient(135deg, rgba(255,255,255,0.25) 0%, rgba(255,255,255,0.15) 100%);
  border-left-color: #ffcc99;
  font-weight: bold;
  box-shadow: inset 0 0 10px rgba(255, 255, 255, 0.2);
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

/* 统计卡片样式 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: linear-gradient(135deg, #ffffff 0%, #fff5e6 100%);
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(255, 154, 61, 0.2);
  display: flex;
  align-items: center;
  gap: 15px;
  border: 1px solid rgba(255, 154, 61, 0.1);
  transition: all 0.3s ease;
}

.stat-icon {
  font-size: 32px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f0f0;
  border-radius: 8px;
}

.stat-content {
  flex: 1;
}

.stat-content h3 {
  margin: 0 0 5px 0;
  font-size: 14px;
  color: #666;
  font-weight: normal;
}

.stat-value {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

/* 最近活动样式 */
.recent-activities {
  background: linear-gradient(135deg, #ffffff 0%, #fff5e6 100%);
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(255, 154, 61, 0.2);
  border: 1px solid rgba(255, 154, 61, 0.1);
}

.recent-activities h2 {
  margin: 0 0 20px 0;
  font-size: 18px;
  color: #333;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 15px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.activity-item:hover {
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.activity-icon {
  font-size: 20px;
  margin-top: 5px;
}

.activity-content {
  flex: 1;
}

.activity-content h4 {
  margin: 0 0 5px 0;
  font-size: 16px;
  color: #333;
}

.activity-content p {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #666;
}

.activity-date {
  font-size: 12px;
  color: #999;
  margin: 0;
}

.activity-status {
  padding: 5px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.activity-status.upcoming {
  background-color: #e3f2fd;
  color: #1976d2;
}

.activity-status.ongoing {
  background-color: #e8f5e8;
  color: #388e3c;
}

.activity-status.completed {
  background-color: #f5f5f5;
  color: #616161;
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

.btn-primary {
  background: linear-gradient(135deg, #ff9a3d 0%, #ff6b6b 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(255, 154, 61, 0.3);
  font-weight: bold;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff9a3d 100%);
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
}

.btn-secondary {
  background: linear-gradient(135deg, #ffffff 0%, #fff5e6 100%);
  color: #ff6b6b;
  border: 2px solid #ffcc99;
  box-shadow: 0 2px 8px rgba(255, 154, 61, 0.2);
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #fff5e6 0%, #ffffff 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 154, 61, 0.3);
  border-color: #ff9a3d;
}

.btn-icon {
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .shelter-dashboard {
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
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
