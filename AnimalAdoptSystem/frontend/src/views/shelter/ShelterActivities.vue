<template>
  <div class="shelter-activities">
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
        <router-link to="/shelter/activities" class="nav-item active">
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
        <h1>基地活动管理</h1>
        <div class="header-actions">
          <button class="btn btn-primary" @click="openAddModal">
            <i class="btn-icon">➕</i>
            添加活动
          </button>
        </div>
      </div>
      
      <!-- 搜索和筛选 -->
      <div class="search-filter">
        <div class="search-box">
          <input type="text" placeholder="搜索活动名称..." v-model="searchQuery" @input="searchActivities">
          <button class="btn btn-secondary">搜索</button>
        </div>
        <div class="filter-box">
          <select v-model="filterStatus" @change="filterActivities">
            <option value="">所有状态</option>
            <option value="upcoming">即将开始</option>
            <option value="ongoing">进行中</option>
            <option value="completed">已结束</option>
          </select>
          <select v-model="filterType" @change="filterActivities">
            <option value="">所有类型</option>
            <option value="adoption">领养活动</option>
            <option value="volunteer">志愿活动</option>
            <option value="fundraising">筹款活动</option>
            <option value="education">教育活动</option>
          </select>
        </div>
      </div>
      
      <!-- 活动列表 -->
      <div class="activities-list">
        <div class="activity-card" v-for="activity in filteredActivities" :key="activity.id">
          <div class="activity-header">
            <h3>{{ activity.title }}</h3>
            <div class="activity-status" :class="activity.status">
              {{ getStatusText(activity.status) }}
            </div>
          </div>
          <div class="activity-info">
            <p class="activity-description">{{ activity.description }}</p>
            <div class="activity-meta">
              <span class="meta-item">📅 {{ formatDate(activity.start_time) }} 至 {{ formatDate(activity.end_time) }}</span>
              <span class="meta-item">📍 {{ activity.location }}</span>
              <span class="meta-item">👥 {{ activity.capacity }}人</span>
              <span class="meta-item">🎯 {{ getTypeText(activity.activity_type) }}</span>
            </div>
          </div>
          <div class="activity-actions">
            <button class="btn btn-sm btn-primary" @click="openEditModal(activity)">编辑</button>
            <button class="btn btn-sm btn-danger" @click="deleteActivity(activity.id)">删除</button>
          </div>
        </div>
        <div class="empty-state" v-if="filteredActivities.length === 0">
          <p>暂无活动数据</p>
        </div>
      </div>
      
      <!-- 添加活动模态框 -->
      <div class="modal" v-if="showAddModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>添加活动</h2>
            <button class="btn-close" @click="showAddModal = false">×</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="addActivity">
              <div class="form-group">
                <label for="title">活动名称</label>
                <input type="text" id="title" v-model="newActivity.title" required>
              </div>
              <div class="form-group">
                <label for="activity_type">活动类型</label>
                <select id="activity_type" v-model="newActivity.activity_type" required>
                  <option value="adoption">领养活动</option>
                  <option value="volunteer">志愿活动</option>
                  <option value="fundraising">筹款活动</option>
                  <option value="education">教育活动</option>
                </select>
              </div>
              <div class="form-group">
                <label for="description">活动描述</label>
                <textarea id="description" v-model="newActivity.description" rows="4" required></textarea>
              </div>
              <div class="form-group">
                <label for="location">活动地点</label>
                <input type="text" id="location" v-model="newActivity.location" required>
              </div>
              <div class="form-group">
                <label for="start_time">开始时间</label>
                <input type="datetime-local" id="start_time" v-model="newActivity.start_time" required>
              </div>
              <div class="form-group">
                <label for="end_time">结束时间</label>
                <input type="datetime-local" id="end_time" v-model="newActivity.end_time" required>
              </div>
              <div class="form-group">
                <label for="capacity">最大参与人数</label>
                <input type="number" id="capacity" v-model="newActivity.capacity" min="1" required>
              </div>

              <div class="form-actions">
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  {{ loading ? '添加中...' : '添加' }}
                </button>
                <button type="button" class="btn btn-secondary" @click="showAddModal = false">取消</button>
              </div>
            </form>
          </div>
        </div>
      </div>
      
      <!-- 编辑活动模态框 -->
      <div class="modal" v-if="showEditModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>编辑活动</h2>
            <button class="btn-close" @click="showEditModal = false">×</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateActivity">
              <div class="form-group">
                <label for="edit-title">活动名称</label>
                <input type="text" id="edit-title" v-model="editActivity.title" required>
              </div>
              <div class="form-group">
                <label for="edit-activity_type">活动类型</label>
                <select id="edit-activity_type" v-model="editActivity.activity_type" required>
                  <option value="adoption">领养活动</option>
                  <option value="volunteer">志愿活动</option>
                  <option value="fundraising">筹款活动</option>
                  <option value="education">教育活动</option>
                </select>
              </div>
              <div class="form-group">
                <label for="edit-description">活动描述</label>
                <textarea id="edit-description" v-model="editActivity.description" rows="4" required></textarea>
              </div>
              <div class="form-group">
                <label for="edit-location">活动地点</label>
                <input type="text" id="edit-location" v-model="editActivity.location" required>
              </div>
              <div class="form-group">
                <label for="edit-start_time">开始时间</label>
                <input type="datetime-local" id="edit-start_time" v-model="editActivity.start_time" required>
              </div>
              <div class="form-group">
                <label for="edit-end_time">结束时间</label>
                <input type="datetime-local" id="edit-end_time" v-model="editActivity.end_time" required>
              </div>
              <div class="form-group">
                <label for="edit-capacity">最大参与人数</label>
                <input type="number" id="edit-capacity" v-model="editActivity.capacity" min="1" required>
              </div>
              <div class="form-group">
                <label for="edit-status">活动状态</label>
                <select id="edit-status" v-model="editActivity.status" required>
                  <option value="upcoming">即将开始</option>
                  <option value="ongoing">进行中</option>
                  <option value="completed">已结束</option>
                </select>
              </div>
              <div class="form-actions">
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  {{ loading ? '更新中...' : '更新' }}
                </button>
                <button type="button" class="btn btn-secondary" @click="showEditModal = false">取消</button>
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
import { shelterApi } from '@/api'

export default {
  name: 'ShelterActivities',
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user')) || {},
      activities: [],
      searchQuery: '',
      filterStatus: '',
      filterType: '',
      showAddModal: false,
      showEditModal: false,
      newActivity: {
        title: '',
        description: '',
        activity_type: 'adoption',
        location: '',
        start_time: '',
        end_time: '',
        capacity: ''
      },
      editActivity: {
        id: '',
        title: '',
        description: '',
        activity_type: 'adoption',
        location: '',
        start_time: '',
        end_time: '',
        capacity: '',
        status: 'upcoming'
      },
      loading: false,
      error: '',
      success: ''
    }
  },
  computed: {
    filteredActivities() {
      // 确保 this.activities 是可迭代的，如果不是，使用空数组
      let result = Array.isArray(this.activities) ? [...this.activities] : []
      
      // 搜索
      if (this.searchQuery) {
        result = result.filter(activity => 
          activity.title.toLowerCase().includes(this.searchQuery.toLowerCase())
        )
      }
      
      // 状态筛选
      if (this.filterStatus) {
        result = result.filter(activity => activity.status === this.filterStatus)
      }
      
      // 类型筛选
      if (this.filterType) {
        result = result.filter(activity => activity.activity_type === this.filterType)
      }
      
      return result
    }
  },
  mounted() {
    // 检查用户是否已登录
    if (!this.user) {
      this.showError('请先登录', '/login')
      return
    }
    
    // 检查用户是否为基地管理员或系统管理员
    if (this.user.user_type !== 'shelter' && this.user.user_type !== 'admin') {
      this.showError('需要基地管理员或系统管理员权限才能访问此页面', '/')
      return
    }
    
    // 检查用户是否有关联的基地（系统管理员除外）
    if (this.user.user_type !== 'admin') {
      // 尝试获取基地ID，处理不同格式的shelter字段
      let shelterId = null
      if (this.user.shelter) {
        if (typeof this.user.shelter === 'object' && this.user.shelter.id) {
          shelterId = this.user.shelter.id
        } else if (typeof this.user.shelter === 'number') {
          shelterId = this.user.shelter
        }
      }
      
      if (!shelterId) {
        this.showError('您还没有关联任何基地，请联系管理员', '/shelter/info')
        return
      }
    }
    
    // 获取活动列表
    this.fetchActivities()
  },
  methods: {
    showError(message, redirectPath = null) {
      this.error = message
      // 3秒后清除错误信息
      setTimeout(() => {
        this.error = ''
        // 如果指定了跳转路径，则跳转
        if (redirectPath) {
          this.$router.push(redirectPath)
        }
      }, 3000)
    },
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.$router.push('/login')
    },
    getStatusText(status) {
      const statusMap = {
        'upcoming': '即将开始',
        'ongoing': '进行中',
        'completed': '已结束'
      }
      return statusMap[status] || status
    },
    getTypeText(type) {
      const typeMap = {
        'adoption': '领养活动',
        'volunteer': '志愿活动',
        'fundraising': '筹款活动',
        'education': '教育活动'
      }
      return typeMap[type] || type
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
    openAddModal() {
      // 重置表单
      this.newActivity = {
        title: '',
        description: '',
        activity_type: 'adoption',
        location: '',
        start_time: '',
        end_time: '',
        max_participants: '',
        status: 'upcoming'
      }
      this.showAddModal = true
      this.error = ''
      this.success = ''
    },
    openEditModal(activity) {
      this.editActivity = JSON.parse(JSON.stringify(activity))
      this.showEditModal = true
      this.error = ''
      this.success = ''
    },
    async addActivity() {
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        // 检查用户是否登录
        const token = localStorage.getItem('token')
        if (!token) {
          this.showError('请先登录', '/login')
          return
        }
        
        // 获取当前用户信息
        const user = JSON.parse(localStorage.getItem('user'))
        if (!user) {
          this.showError('用户信息缺失，请重新登录', '/login')
          return
        }
        
        if (user.user_type !== 'shelter' && user.user_type !== 'admin') {
          this.showError('需要基地管理员或系统管理员权限才能添加活动', '/')
          return
        }
        
        if (user.user_type !== 'admin') {
          // 尝试获取基地ID，处理不同格式的shelter字段
          let shelterId = null
          if (user.shelter) {
            if (typeof user.shelter === 'object' && user.shelter.id) {
              shelterId = user.shelter.id
            } else if (typeof user.shelter === 'number') {
              shelterId = user.shelter
            }
          }
          
          if (!shelterId) {
            this.showError('您还没有关联任何基地，请先完善基地信息', '/shelter/info')
            return
          }
        }
        
        // 获取基地ID，处理不同格式的shelter字段
        let shelterId = null
        if (user.shelter) {
          if (typeof user.shelter === 'object' && user.shelter.id) {
            shelterId = user.shelter.id
          } else if (typeof user.shelter === 'number') {
            shelterId = user.shelter
          }
        }
        // 为系统管理员提供默认基地 ID（如果没有关联基地）
        if (user.user_type === 'admin' && !shelterId) {
          shelterId = 1 // 默认使用基地 ID 为 1
        }
        console.log('添加活动，基地ID:', shelterId, '活动数据:', this.newActivity)
        
        const response = await shelterApi.createShelterActivity(shelterId, this.newActivity)
        if (response.code === 200) {
          // 添加成功
          // 确保 this.activities 是一个数组
          if (!Array.isArray(this.activities)) {
            this.activities = []
          }
          this.activities.push(response.data)
          this.showAddModal = false
          this.success = '活动添加成功'
          
          // 3秒后清除成功信息
          setTimeout(() => {
            this.success = ''
          }, 3000)
        } else {
          this.error = response.message || '添加失败'
        }
      } catch (error) {
        console.error('添加活动错误:', error)
        if (error.response?.status === 401) {
          this.showError('登录已过期，请重新登录', '/login')
        } else if (error.response?.status === 403) {
          this.error = '没有权限添加活动，请联系基地管理员'
        } else {
          this.error = error.response?.data?.message || '添加失败，请检查网络连接'
        }
      } finally {
        this.loading = false
      }
    },
    async updateActivity() {
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        // 检查用户是否登录
        const token = localStorage.getItem('token')
        if (!token) {
          this.showError('请先登录', '/login')
          return
        }
        
        // 获取当前用户信息
        const user = JSON.parse(localStorage.getItem('user'))
        if (!user) {
          this.showError('用户信息缺失，请重新登录', '/login')
          return
        }
        
        if (user.user_type !== 'shelter' && user.user_type !== 'admin') {
          this.showError('需要基地管理员或系统管理员权限才能更新活动', '/')
          return
        }
        
        if (user.user_type !== 'admin') {
          // 尝试获取基地ID，处理不同格式的shelter字段
          let shelterId = null
          if (user.shelter) {
            if (typeof user.shelter === 'object' && user.shelter.id) {
              shelterId = user.shelter.id
            } else if (typeof user.shelter === 'number') {
              shelterId = user.shelter
            }
          }
          
          if (!shelterId) {
            this.showError('您还没有关联任何基地，请先完善基地信息', '/shelter/info')
            return
          }
        }
        
        // 获取基地ID，处理不同格式的shelter字段
        let shelterId = null
        if (user.shelter) {
          if (typeof user.shelter === 'object' && user.shelter.id) {
            shelterId = user.shelter.id
          } else if (typeof user.shelter === 'number') {
            shelterId = user.shelter
          }
        }
        // 为系统管理员提供默认基地 ID（如果没有关联基地）
        if (user.user_type === 'admin' && !shelterId) {
          shelterId = 1 // 默认使用基地 ID 为 1
        }
        console.log('更新活动，基地ID:', shelterId, '活动ID:', this.editActivity.id, '活动数据:', this.editActivity)
        
        const response = await shelterApi.updateShelterActivity(shelterId, this.editActivity.id, this.editActivity)
        if (response.code === 200) {
          // 更新成功
          // 确保 this.activities 是一个数组
          if (!Array.isArray(this.activities)) {
            this.activities = []
          }
          const index = this.activities.findIndex(a => a.id === this.editActivity.id)
          if (index !== -1) {
            this.activities[index] = response.data
          }
          this.showEditModal = false
          this.success = '活动更新成功'
          
          // 3秒后清除成功信息
          setTimeout(() => {
            this.success = ''
          }, 3000)
        } else {
          this.error = response.message || '更新失败'
        }
      } catch (error) {
        console.error('更新活动错误:', error)
        if (error.response?.status === 401) {
          this.showError('登录已过期，请重新登录', '/login')
        } else if (error.response?.status === 403) {
          this.error = '没有权限更新活动，请联系基地管理员'
        } else {
          this.error = error.response?.data?.message || '更新失败，请检查网络连接'
        }
      } finally {
        this.loading = false
      }
    },
    async deleteActivity(id) {
      if (!confirm('确定要删除这个活动吗？')) {
        return
      }
      
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        // 检查用户是否登录
        const token = localStorage.getItem('token')
        if (!token) {
          this.showError('请先登录', '/login')
          return
        }
        
        // 获取当前用户信息
        const user = JSON.parse(localStorage.getItem('user'))
        if (!user) {
          this.showError('用户信息缺失，请重新登录', '/login')
          return
        }
        
        if (user.user_type !== 'shelter' && user.user_type !== 'admin') {
          this.showError('需要基地管理员或系统管理员权限才能删除活动', '/')
          return
        }
        
        if (user.user_type !== 'admin') {
          // 尝试获取基地ID，处理不同格式的shelter字段
          let shelterId = null
          if (user.shelter) {
            if (typeof user.shelter === 'object' && user.shelter.id) {
              shelterId = user.shelter.id
            } else if (typeof user.shelter === 'number') {
              shelterId = user.shelter
            }
          }
          
          if (!shelterId) {
            this.showError('您还没有关联任何基地，请先完善基地信息', '/shelter/info')
            return
          }
        }
        
        // 获取基地ID，处理不同格式的shelter字段
        let shelterId = null
        if (user.shelter) {
          if (typeof user.shelter === 'object' && user.shelter.id) {
            shelterId = user.shelter.id
          } else if (typeof user.shelter === 'number') {
            shelterId = user.shelter
          }
        }
        // 为系统管理员提供默认基地 ID（如果没有关联基地）
        if (user.user_type === 'admin' && !shelterId) {
          shelterId = 1 // 默认使用基地 ID 为 1
        }
        console.log('删除活动，基地ID:', shelterId, '活动ID:', id)
        
        const response = await shelterApi.deleteShelterActivity(shelterId, id)
        if (response.code === 200) {
          // 删除成功
          // 确保 this.activities 是一个数组
          if (!Array.isArray(this.activities)) {
            this.activities = []
          }
          this.activities = this.activities.filter(a => a.id !== id)
          this.success = '活动删除成功'
          
          // 3秒后清除成功信息
          setTimeout(() => {
            this.success = ''
          }, 3000)
        } else {
          this.error = response.message || '删除失败'
        }
      } catch (error) {
        console.error('删除活动错误:', error)
        if (error.response?.status === 401) {
          this.showError('登录已过期，请重新登录', '/login')
        } else if (error.response?.status === 403) {
          this.error = '没有权限删除活动，请联系基地管理员'
        } else {
          this.error = error.response?.data?.message || '删除失败，请检查网络连接'
        }
      } finally {
        this.loading = false
      }
    },
    searchActivities() {
      // 搜索逻辑已在computed中处理
    },
    filterActivities() {
      // 筛选逻辑已在computed中处理
    },
    async fetchActivities() {
      this.loading = true
      this.error = ''
      
      try {
        // 检查用户是否登录
        const token = localStorage.getItem('token')
        if (!token) {
          this.showError('请先登录', '/login')
          return
        }
        
        // 获取当前用户信息
        const user = JSON.parse(localStorage.getItem('user'))
        if (!user) {
          this.showError('用户信息缺失，请重新登录', '/login')
          return
        }
        
        if (user.user_type !== 'shelter' && user.user_type !== 'admin') {
          this.showError('需要基地管理员或系统管理员权限才能查看活动', '/')
          return
        }
        
        // 检查用户是否有管理的基地（系统管理员除外）
        if (user.user_type !== 'admin') {
          // 尝试获取基地ID，处理不同格式的shelter字段
          let shelterId = null
          if (user.shelter) {
            if (typeof user.shelter === 'object' && user.shelter.id) {
              shelterId = user.shelter.id
            } else if (typeof user.shelter === 'number') {
              shelterId = user.shelter
            }
          }
          
          if (!shelterId) {
            this.showError('您还没有关联任何基地，请先完善基地信息', '/shelter/info')
            return
          }
        }
        
        // 获取基地ID，处理不同格式的shelter字段
        let shelterId = null
        if (user.shelter) {
          if (typeof user.shelter === 'object' && user.shelter.id) {
            shelterId = user.shelter.id
          } else if (typeof user.shelter === 'number') {
            shelterId = user.shelter
          }
        }
        // 为系统管理员提供默认基地 ID（如果没有关联基地）
        if (user.user_type === 'admin' && !shelterId) {
          shelterId = 1 // 默认使用基地 ID 为 1
        }
        console.log('获取基地活动，基地ID:', shelterId)
            
        const response = await shelterApi.getShelterActivities(shelterId)
        console.log('API响应:', response)
        
        if (response.code === 200) {
          // 处理DRF分页响应格式
          if (response.data && response.data.results) {
            this.activities = response.data.results
          } else if (Array.isArray(response.data)) {
            this.activities = response.data
          } else {
            this.activities = []
          }
          console.log('活动列表获取成功，共', this.activities.length, '个活动')
        } else {
          this.error = response.message || '获取活动列表失败'
        }
      } catch (error) {
        console.error('获取活动列表错误:', error)
        if (error.response?.status === 401) {
          this.showError('登录已过期，请重新登录', '/login')
        } else if (error.response?.status === 403) {
          this.error = '没有权限查看活动，请联系基地管理员'
        } else if (error.response?.status === 404) {
          this.error = '基地不存在'
        } else {
          this.error = error.response?.data?.message || '获取活动列表失败，请检查网络连接'
        }
      } finally {
        this.loading = false
      }
    },
  }
}
</script>
<style scoped>
.shelter-activities {
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
}

/* 侧边栏样式 */
.sidebar {
  width: 280px;
  background-color: #2c3e50;
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

/* 活动列表样式 */
.activities-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.activity-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  padding: 20px;
  transition: all 0.3s ease;
}

.activity-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
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
  color: #333;
  flex: 1;
}

.activity-status {
  padding: 5px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  margin-left: 15px;
}

.activity-status.upcoming {
  background-color: #e8f5e8;
  color: #388e3c;
}

.activity-status.ongoing {
  background-color: #e3f2fd;
  color: #1976d2;
}

.activity-status.completed {
  background-color: #f5f5f5;
  color: #616161;
}

.activity-info {
  margin-bottom: 20px;
}

.activity-description {
  margin: 0 0 15px 0;
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}

.activity-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 14px;
  color: #666;
}

.meta-item {
  display: inline-block;
}

.activity-actions {
  display: flex;
  gap: 10px;
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

/* 表单样式 */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-bottom: 15px;
}

.form-group label {
  font-size: 14px;
  font-weight: bold;
  color: #555;
}

.form-group input,
.form-group select,
.form-group textarea {
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

.form-group textarea {
  resize: vertical;
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

.btn-danger {
  background-color: #f44336;
  color: white;
}

.btn-danger:hover {
  background-color: #da190b;
}

.btn-success {
  background-color: #2196F3;
  color: white;
}

.btn-success:hover {
  background-color: #0b7dda;
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
  .shelter-activities {
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
  
  .activities-list {
    grid-template-columns: 1fr;
  }
  
  .activity-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .activity-status {
    margin-left: 0;
  }
  
  .modal-content {
    width: 95%;
    max-height: 95vh;
  }
}
</style>
