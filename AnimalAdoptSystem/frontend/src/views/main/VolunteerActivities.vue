<template>
  <div class="volunteer-activities">
    <div class="container">
      <h2>志愿者活动</h2>
      
      <div class="filters">
        <div class="search-box">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="搜索活动名称或描述..." 
            class="search-input"
            @input="searchActivities"
          >
          <button class="btn btn-search" @click="searchActivities">搜索</button>
        </div>
        
        <div class="filter-options">
          <select v-model="filterStatus" @change="filterActivities">
            <option value="">所有状态</option>
            <option value="upcoming">即将开始</option>
            <option value="ongoing">进行中</option>
            <option value="completed">已完成</option>
          </select>
          
          <select v-model="sortBy" @change="sortActivities">
            <option value="created_at">按创建时间</option>
            <option value="start_time">按开始时间</option>
            <option value="name">按名称</option>
          </select>
        </div>
      </div>

      <div class="activities-grid" v-if="filteredActivities.length > 0">
        <div class="activity-card" v-for="activity in filteredActivities" :key="activity.id">
          <div class="activity-header">
            <h3>{{ activity.name }}</h3>
            <span class="activity-status" :class="activity.status">
              {{ getStatusText(activity.status) }}
            </span>
          </div>
          
          <div class="activity-info">
            <p class="activity-description">{{ activity.description }}</p>
            
            <div class="activity-details">
              <div class="detail-item">
                <i class="icon">📍</i>
                <span>{{ activity.location }}</span>
              </div>
              
              <div class="detail-item">
                <i class="icon">👥</i>
                <span>{{ (activity.participants || []).length }}/{{ activity.capacity }} 人</span>
              </div>
              
              <div class="detail-item">
                <i class="icon">⏰</i>
                <span>{{ formatDate(activity.start_time) }}</span>
              </div>
              
              <div class="detail-item" v-if="activity.organizer">
                <i class="icon">👤</i>
                <span>{{ activity.organizer.username }}</span>
              </div>
              <div class="detail-item" v-if="activity.shelter">
                <i class="icon">🏠</i>
                <span>{{ activity.shelter.name }}</span>
              </div>
            </div>
          </div>
          
          <div class="activity-actions">
            <button 
              v-if="activity.status === 'upcoming' && !isRegistered(activity.id)" 
              class="btn btn-primary" 
              @click="registerActivity(activity.id)"
              :disabled="loading"
            >
              {{ loading ? '报名中...' : '立即报名' }}
            </button>
            
            <button 
              v-else-if="isRegistered(activity.id)" 
              class="btn btn-success" 
              disabled
            >
              已报名
            </button>
            
            <button 
              v-else-if="activity.status === 'ongoing'" 
              class="btn btn-warning" 
              disabled
            >
              进行中
            </button>
            
            <button 
              v-else 
              class="btn btn-secondary" 
              disabled
            >
              {{ getStatusText(activity.status) }}
            </button>
            
            <button class="btn btn-outline" @click="viewDetails(activity)">
              查看详情
            </button>
          </div>
        </div>
      </div>
      
      <div class="empty-state" v-else>
        <p>暂无符合条件的活动</p>
      </div>
      
      <!-- 活动详情模态框 -->
      <div class="modal" v-if="showDetailsModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>{{ selectedActivity.name }}</h2>
            <button class="btn-close" @click="showDetailsModal = false">×</button>
          </div>
          
          <div class="modal-body">
            <div class="activity-detail-section">
              <h3>活动详情</h3>
              <p>{{ selectedActivity.description }}</p>
            </div>
            
            <div class="activity-detail-section">
              <h3>基本信息</h3>
              <div class="detail-grid">
                <div class="detail-row">
                  <span class="label">地点：</span>
                  <span>{{ selectedActivity.location }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">时间：</span>
                  <span>{{ formatDateTime(selectedActivity.start_time) }} - {{ formatDateTime(selectedActivity.end_time) }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">容量：</span>
                  <span>{{ (selectedActivity.participants || []).length }}/{{ selectedActivity.capacity }} 人</span>
                </div>
                <div class="detail-row" v-if="selectedActivity.organizer">
                  <span class="label">组织者：</span>
                  <span>{{ selectedActivity.organizer.username }}</span>
                </div>
              </div>
            </div>
            
            <div class="activity-detail-section" v-if="selectedActivity.participants && selectedActivity.participants.length > 0">
              <h3>已报名参与者</h3>
              <div class="participants-list">
                <span 
                  v-for="participant in selectedActivity.participants" 
                  :key="participant.id"
                  class="participant-tag"
                >
                  {{ participant.username }}
                </span>
              </div>
            </div>
          </div>
          
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showDetailsModal = false">关闭</button>
            <button 
              v-if="selectedActivity.status === 'upcoming' && !isRegistered(selectedActivity.id)" 
              class="btn btn-primary" 
              @click="registerFromModal(selectedActivity.id)"
              :disabled="loading"
            >
              {{ loading ? '报名中...' : '立即报名' }}
            </button>
          </div>
        </div>
      </div>
      
      <div class="loading" v-if="initialLoading">
        <p>加载中...</p>
      </div>
      
      <div class="error-message" v-if="error">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'VolunteerActivities',
  data() {
    return {
      activities: [],
      searchQuery: '',
      filterStatus: '',
      sortBy: 'created_at',
      showDetailsModal: false,
      selectedActivity: {},
      loading: false,
      initialLoading: true,
      error: '',
      userRegistrations: [] // 用户已报名的活动ID列表
    }
  },
  computed: {
    filteredActivities() {
      console.log('计算filteredActivities, activities长度:', this.activities.length)
      let result = [...this.activities]
      console.log('初始result长度:', result.length)
      
      // 搜索过滤
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        result = result.filter(activity => 
          activity.name.toLowerCase().includes(query) ||
          activity.description.toLowerCase().includes(query)
        )
        console.log('搜索后result长度:', result.length)
      }
      
      // 状态过滤
      if (this.filterStatus) {
        result = result.filter(activity => activity.status === this.filterStatus)
        console.log('状态过滤后result长度:', result.length)
      }
      
      // 排序
      result.sort((a, b) => {
        switch (this.sortBy) {
          case 'name':
            return a.name.localeCompare(b.name)
          case 'start_time':
            return new Date(a.start_time) - new Date(b.start_time)
          case 'created_at':
          default:
            return new Date(b.created_at) - new Date(a.created_at)
        }
      })
      
      console.log('最终result长度:', result.length)
      return result
    }
  },
  mounted() {
    console.log('VolunteerActivities 组件已挂载')
    this.loadActivities()
    this.loadUserRegistrations()
    // 等待数据加载完成后同步状态
    setTimeout(() => {
      this.syncRegistrationStatus()
    }, 1000)
  },
  methods: {
    async loadActivities() {
      this.initialLoading = true
      this.error = ''
      
      try {
        // 直接使用fetch API，避免axios的拦截器问题
        console.log('开始加载活动列表')
        
        // 只获取基地列表
        const shelterResponse = await fetch('/api/shelters/')
        
        console.log('基地列表响应状态:', shelterResponse.status)
        
        if (!shelterResponse.ok) {
          throw new Error(`基地API错误! status: ${shelterResponse.status}`)
        }
        
        const shelterData = await shelterResponse.json()
        
        console.log('基地API响应数据:', shelterData)
        
        // 处理基地活动数据
        let shelterActivities = []
        if (shelterData.data && shelterData.data.results && Array.isArray(shelterData.data.results)) {
          // 遍历每个基地，获取其活动
          for (const shelter of shelterData.data.results) {
            try {
              const activitiesResponse = await fetch(`/api/shelters/${shelter.id}/activities/`)
              if (activitiesResponse.ok) {
                const activitiesData = await activitiesResponse.json()
                if (activitiesData.data && activitiesData.data.results && Array.isArray(activitiesData.data.results)) {
                  // 标准化基地活动数据结构
                  const normalizedActivities = activitiesData.data.results
                    // 移除过滤，显示所有基地活动
                    .map(activity => ({
                      id: activity.id,
                      shelterId: shelter.id,
                      name: activity.title, // 将title映射为name
                      description: activity.description,
                      location: activity.location,
                      start_time: activity.start_time,
                      end_time: activity.end_time,
                      capacity: activity.capacity,
                      status: activity.status,
                      organizer: { username: typeof activity.created_by === 'object' ? activity.created_by.username : activity.created_by }, // 确保只显示用户名
                      shelter: { name: shelter.name }, // 添加基地信息
                      activity_type: activity.activity_type, // 保留基地活动类型
                      created_at: activity.created_at
                    }))
                  shelterActivities = [...shelterActivities, ...normalizedActivities]
                }
              }
            } catch (error) {
              console.error(`获取基地 ${shelter.name} 的活动失败:`, error)
            }
          }
        }
        
        // 只显示基地活动
        this.activities = shelterActivities
        console.log('最终活动数据:', this.activities)
        console.log('活动总数:', this.activities.length)
        
      } catch (error) {
        console.error('加载活动失败:', error)
        this.error = '加载活动列表失败，请稍后重试'
      } finally {
        this.initialLoading = false
        console.log('加载完成，activities长度:', this.activities.length)
      }
    },
    
    async loadUserRegistrations() {
      const token = localStorage.getItem('token')
      if (!token) return
      
      try {
        const response = await this.$axios.get('/volunteers/participants/my-participations/')
        if (response.code === 200 && Array.isArray(response.data)) {
          this.userRegistrations = response.data.map(item => item.activity)
        }
      } catch (error) {
        console.error('加载用户报名信息失败:', error)
        // 不显示错误，因为这是辅助功能
        // 如果是认证错误，可能是用户未登录，这很正常
        if (error.response?.status === 401) {
          // 用户未登录，清空报名状态
          this.userRegistrations = []
        }
      }
    },
    
    isRegistered(activityId) {
      // 检查用户是否已报名该活动
      const isRegisteredLocal = this.userRegistrations.includes(activityId)
      
      // 如果本地状态显示未报名，但页面刚加载，需要重新检查
      if (!isRegisteredLocal && this.activities.length > 0) {
        const activity = this.activities.find(a => a.id === activityId)
        if (activity && activity.participants) {
          const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
          const isRegisteredInParticipants = activity.participants.some(p => p.id === currentUser.id)
          if (isRegisteredInParticipants) {
            // 更新本地状态
            if (!this.userRegistrations.includes(activityId)) {
              this.userRegistrations.push(activityId)
            }
            return true
          }
        }
      }
      
      return isRegisteredLocal
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
    },
    
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', {
        month: 'short',
        day: 'numeric'
      })
    },
    
    formatDateTime(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    searchActivities() {
      // 搜索逻辑已在computed中处理
    },
    
    filterActivities() {
      // 过滤逻辑已在computed中处理
    },
    
    sortActivities() {
      // 排序逻辑已在computed中处理
    },
    
    async registerActivity(activityId) {
      const token = localStorage.getItem('token')
      console.log('当前token:', token ? '存在' : '不存在')
      
      if (!token) {
        this.error = '请先登录后再报名活动'
        setTimeout(() => {
          this.$router.push('/login')
        }, 2000)
        return
      }
      
      // 找到活动对应的基地ID
      const activity = this.activities.find(a => a.id === activityId)
      if (!activity || !activity.shelterId) {
        this.error = '活动信息有误，无法报名'
        return
      }
      
      this.loading = true
      this.error = ''
      
      try {
        console.log(`开始报名活动 ${activityId}，基地ID：${activity.shelterId}`)
        const response = await this.$axios.post(`/shelters/${activity.shelterId}/activities/${activityId}/register/`)
        console.log('报名响应:', response)
        
        if (response.code === 200) {
          // 更新用户报名状态
          this.userRegistrations.push(activityId)
          // 重新加载活动数据以更新参与人数
          await this.loadActivities()
          this.error = '报名成功！'
          // 2秒后清除成功消息
          setTimeout(() => {
            this.error = ''
          }, 2000)
        } else {
          this.error = response.message || '报名失败'
        }
      } catch (error) {
        console.error('活动报名失败:', error)
        console.error('错误详情:', error.response || error.message)
        
        if (error.response?.status === 400) {
          const errorMessage = error.response.data.message || error.response.data.detail || '请求参数错误'
          // 特殊处理重复报名的情况
          if (errorMessage.includes('已经报名') || errorMessage.includes('already registered')) {
            this.error = '您已经报名参加此活动了'
            // 更新本地状态确保显示正确
            if (!this.userRegistrations.includes(activityId)) {
              this.userRegistrations.push(activityId)
            }
          } else if (errorMessage.includes('人数已满') || errorMessage.includes('full')) {
            this.error = '活动人数已满，无法报名'
          } else if (errorMessage.includes('无法报名') || errorMessage.includes('cannot register')) {
            this.error = '当前活动状态不允许报名'
          } else {
            this.error = '报名失败：' + errorMessage
          }
        } else if (error.response?.status === 401) {
          this.error = '认证失败，请重新登录'
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          setTimeout(() => {
            this.$router.push('/login')
          }, 2000)
        } else if (error.response?.status === 403) {
          this.error = '没有权限报名此活动'
        } else if (error.response?.status === 404) {
          this.error = '活动不存在'
        } else {
          this.error = '报名失败：' + (error.message || '请稍后重试')
        }
      } finally {
        this.loading = false
      }
    },
    
    viewDetails(activity) {
      this.selectedActivity = activity
      this.showDetailsModal = true
    },
    
    async registerFromModal(activityId) {
      await this.registerActivity(activityId)
      this.showDetailsModal = false
    },
    
    syncRegistrationStatus() {
      // 同步活动参与状态
      if (this.activities.length > 0) {
        const currentUser = JSON.parse(localStorage.getItem('user') || '{}')
        this.activities.forEach(activity => {
          if (activity.participants && Array.isArray(activity.participants)) {
            const isParticipating = activity.participants.some(p => p.id === currentUser.id)
            if (isParticipating && !this.userRegistrations.includes(activity.id)) {
              this.userRegistrations.push(activity.id)
              console.log(`同步活动 ${activity.id} 的报名状态`)
            }
          }
        })
      }
    }
  }
}
</script>

<style scoped>
.volunteer-activities {
  padding: 40px 0;
  background: linear-gradient(135deg, #fff8f0 0%, #ffeaa7 100%);
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

h2 {
  text-align: center;
  color: #ff6b6b;
  margin-bottom: 30px;
  font-size: 28px;
}

.filters {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 15px;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(255, 154, 61, 0.2);
}

.search-box {
  display: flex;
  gap: 10px;
  flex: 1;
  min-width: 300px;
}

.search-input {
  flex: 1;
  padding: 12px;
  border: 2px solid #ffcc99;
  border-radius: 8px;
  font-size: 16px;
}

.search-input:focus {
  outline: none;
  border-color: #ff9a3d;
  box-shadow: 0 0 0 3px rgba(255, 154, 61, 0.2);
}

.filter-options {
  display: flex;
  gap: 15px;
}

.filter-options select {
  padding: 12px;
  border: 2px solid #ffcc99;
  border-radius: 8px;
  font-size: 16px;
  background: white;
}

.filter-options select:focus {
  outline: none;
  border-color: #ff9a3d;
}

.activities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;
  margin-bottom: 30px;
}

.activity-card {
  background: white;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 8px 25px rgba(255, 154, 61, 0.2);
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 154, 61, 0.1);
}

.activity-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 35px rgba(255, 154, 61, 0.3);
}

.activity-header {
  padding: 20px 20px 0;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.activity-header h3 {
  margin: 0;
  font-size: 20px;
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

.activity-info {
  padding: 0 20px;
}

.activity-description {
  color: #666;
  line-height: 1.5;
  margin-bottom: 20px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
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
  padding: 20px;
  display: flex;
  gap: 10px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  flex: 1;
}

.btn-primary {
  background: linear-gradient(135deg, #ff9a3d 0%, #ff6b6b 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.4);
}

.btn-primary:disabled {
  background: #cccccc;
  cursor: not-allowed;
}

.btn-success {
  background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
  color: white;
}

.btn-warning {
  background: linear-gradient(135deg, #FF9800 0%, #FFC107 100%);
  color: white;
}

.btn-secondary {
  background: #e0e0e0;
  color: #666;
}

.btn-outline {
  background: transparent;
  color: #ff6b6b;
  border: 2px solid #ffcc99;
}

.btn-outline:hover {
  background: #fff5e6;
  border-color: #ff9a3d;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(255, 154, 61, 0.2);
}

.empty-state p {
  color: #999;
  font-size: 18px;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 15px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 25px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  color: #ff6b6b;
}

.btn-close {
  background: none;
  border: none;
  font-size: 28px;
  cursor: pointer;
  color: #999;
}

.btn-close:hover {
  color: #333;
}

.modal-body {
  padding: 25px;
}

.activity-detail-section {
  margin-bottom: 25px;
}

.activity-detail-section h3 {
  color: #ff9a3d;
  margin-bottom: 15px;
  font-size: 18px;
}

.activity-detail-section p {
  color: #666;
  line-height: 1.6;
}

.detail-grid {
  display: grid;
  gap: 12px;
}

.detail-row {
  display: flex;
  gap: 10px;
}

.detail-row .label {
  font-weight: bold;
  color: #555;
  min-width: 80px;
}

.participants-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.participant-tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
}

.modal-footer {
  padding: 20px 25px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 15px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error-message {
  background: #ffebee;
  color: #c62828;
  padding: 15px;
  border-radius: 8px;
  margin-top: 20px;
  text-align: center;
}

@media (max-width: 768px) {
  .filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    min-width: unset;
  }
  
  .filter-options {
    justify-content: space-between;
  }
  
  .activities-grid {
    grid-template-columns: 1fr;
  }
  
  .activity-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .activity-actions {
    flex-direction: column;
  }
  
  .modal-content {
    width: 95%;
    margin: 10px;
  }
  
  .detail-grid {
    gap: 15px;
  }
}
</style>