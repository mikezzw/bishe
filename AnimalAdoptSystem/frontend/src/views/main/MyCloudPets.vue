<template>
  <div class="my-cloud-pets">
    <div class="container">
      <h2>☁️ 我的云养宠物</h2>
      
      <!-- 空状态 -->
      <div v-if="!loading && cloudPets.length === 0" class="empty-state">
        <div class="empty-icon">🐾</div>
        <h3>您还没有云养宠物</h3>
        <p>去领养一只可爱的动物，建立专属的云养关系吧！</p>
        <router-link to="/animals" class="btn btn-primary">浏览可领养动物</router-link>
      </div>
      
      <!-- 加载状态 -->
      <div v-else-if="loading" class="loading">
        <p>加载中...</p>
      </div>
      
      <!-- 云养宠物列表 -->
      <div v-else class="pets-grid">
        <div v-for="pet in cloudPets" :key="pet.id" class="pet-card" @click="showPetDetail(pet)">
          <div class="pet-image">
            <img :src="pet.images[0] || '/src/assets/default-pet.png'" :alt="pet.name">
            <div class="status-badge" :class="pet.status">{{ getStatusText(pet.status) }}</div>
          </div>
          
          <div class="pet-info">
            <h3>{{ pet.name }}</h3>
            <p class="breed">{{ pet.breed }} · {{ pet.age }}岁</p>
            
            <div class="stats">
              <div class="stat-item">
                <span class="stat-value">{{ pet.days_adopted }}</span>
                <span class="stat-label">云养天数</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ pet.interaction_count }}</span>
                <span class="stat-label">互动次数</span>
              </div>
            </div>
            
            <!-- 最近动态 -->
            <div v-if="pet.latest_activity" class="latest-activity">
              <div class="activity-header">
                <span class="activity-type">{{ pet.latest_activity.activity_type }}</span>
                <span class="activity-time">{{ formatTime(pet.latest_activity.created_at) }}</span>
              </div>
              <p class="activity-title">{{ pet.latest_activity.title }}</p>
            </div>
          </div>
          
          <div class="card-actions">
            <button class="btn-action" @click.stop="viewActivities(pet)">
              📅 查看动态
            </button>
            <button class="btn-action" @click.stop="goToAnimalDetail(pet)">
              👀 查看详情
            </button>
          </div>
        </div>
      </div>
      
      <!-- 动态详情模态框 -->
      <div class="modal-overlay" v-if="showActivityModal" @click.self="closeActivityModal">
        <div class="modal-content activity-modal">
          <div class="modal-header">
            <h2>{{ selectedPet.name }} 的成长记录</h2>
            <button class="close-btn" @click="closeActivityModal">×</button>
          </div>
          <div class="modal-body">
            <div v-if="activitiesLoading" class="loading">加载中...</div>
            <div v-else-if="activities.length === 0" class="empty-activities">
              <p>暂无动态记录</p>
            </div>
            <div v-else class="timeline">
              <div v-for="activity in activities" :key="activity.id" class="timeline-item">
                <div class="timeline-dot"></div>
                <div class="timeline-content">
                  <div class="activity-meta">
                    <span class="activity-type-badge">{{ activity.activity_type }}</span>
                    <span class="activity-date">{{ formatDate(activity.created_at) }}</span>
                    <span class="activity-author">by {{ activity.created_by }}</span>
                  </div>
                  <h4 class="activity-title">{{ activity.title }}</h4>
                  <p class="activity-desc">{{ activity.content }}</p>
                  <div v-if="activity.images && activity.images.length > 0" class="activity-images">
                    <img v-for="(img, idx) in activity.images" :key="idx" :src="img" :alt="`图片${idx+1}`">
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 分页 -->
            <div v-if="totalPages > 1" class="pagination">
              <button @click="loadActivities(currentPage - 1)" :disabled="currentPage === 1">上一页</button>
              <span>第 {{ currentPage }} / {{ totalPages }} 页</span>
              <button @click="loadActivities(currentPage + 1)" :disabled="currentPage === totalPages">下一页</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { adoptionApi } from '@/api'

export default {
  name: 'MyCloudPets',
  data() {
    return {
      cloudPets: [],
      loading: false,
      showActivityModal: false,
      selectedPet: null,
      activities: [],
      activitiesLoading: false,
      currentPage: 1,
      totalPages: 1,
      pageSize: 10
    }
  },
  created() {
    this.loadCloudPets()
  },
  methods: {
    async loadCloudPets() {
      this.loading = true
      try {
        const res = await adoptionApi.getMyCloudPets()
        if (res.code === 200) {
          this.cloudPets = res.data
        }
      } catch (error) {
        console.error('加载云养宠物失败:', error)
        this.$toast?.error('加载失败')
      } finally {
        this.loading = false
      }
    },
    
    async viewActivities(pet) {
      this.selectedPet = pet
      this.showActivityModal = true
      this.currentPage = 1
      await this.loadActivities(1)
    },
    
    async loadActivities(page) {
      if (!this.selectedPet) return
      
      this.activitiesLoading = true
      try {
        const res = await adoptionApi.getPetActivities(this.selectedPet.id, { page })
        if (res.code === 200) {
          this.activities = res.data.activities
          this.totalPages = Math.ceil(res.data.total / this.pageSize)
          this.currentPage = page
        }
      } catch (error) {
        console.error('加载动态失败:', error)
        this.$toast?.error('加载动态失败')
      } finally {
        this.activitiesLoading = false
      }
    },
    
    closeActivityModal() {
      this.showActivityModal = false
      this.selectedPet = null
      this.activities = []
    },
    
    goToAnimalDetail(pet) {
      this.$router.push(`/animal/${pet.id}`)
    },
    
    showPetDetail(pet) {
      // 点击卡片也可以查看详情
      this.goToAnimalDetail(pet)
    },
    
    getStatusText(status) {
      const map = {
        'available': '可领养',
        'adopted': '已领养',
        'medical': '医疗中',
        'pending': '审核中'
      }
      return map[status] || status
    },
    
    formatTime(dateStr) {
      const date = new Date(dateStr)
      const now = new Date()
      const diff = now - date
      
      const minutes = Math.floor(diff / 60000)
      const hours = Math.floor(diff / 3600000)
      const days = Math.floor(diff / 86400000)
      
      if (minutes < 60) return `${minutes}分钟前`
      if (hours < 24) return `${hours}小时前`
      if (days < 7) return `${days}天前`
      return date.toLocaleDateString()
    },
    
    formatDate(dateStr) {
      return new Date(dateStr).toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.my-cloud-pets {
  padding: 2rem 0;
  min-height: calc(100vh - 200px);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

h2 {
  font-size: 2rem;
  color: #333;
  margin-bottom: 2rem;
  text-align: center;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: #f9f9f9;
  border-radius: 12px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.5rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: #999;
  margin-bottom: 2rem;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.pets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 2rem;
}

.pet-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
}

.pet-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.pet-image {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.pet-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.status-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: bold;
  color: white;
}

.status-badge.available {
  background: #52c41a;
}

.status-badge.adopted {
  background: #1890ff;
}

.status-badge.medical {
  background: #faad14;
}

.pet-info {
  padding: 1.5rem;
}

.pet-info h3 {
  font-size: 1.3rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.breed {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat-item {
  flex: 1;
  text-align: center;
  padding: 0.8rem;
  background: #f5f5f5;
  border-radius: 8px;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: bold;
  color: #1890ff;
}

.stat-label {
  display: block;
  font-size: 0.8rem;
  color: #999;
  margin-top: 0.3rem;
}

.latest-activity {
  padding: 1rem;
  background: #f0f9ff;
  border-radius: 8px;
  margin-bottom: 1rem;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.activity-type {
  font-size: 0.85rem;
  color: #1890ff;
  font-weight: bold;
}

.activity-time {
  font-size: 0.8rem;
  color: #999;
}

.activity-title {
  font-size: 0.9rem;
  color: #666;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  padding: 0 1.5rem 1.5rem;
}

.btn-action {
  flex: 1;
  padding: 0.6rem;
  border: 1px solid #d9d9d9;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s;
}

.btn-action:hover {
  border-color: #1890ff;
  color: #1890ff;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 800px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e8e8e8;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #999;
  line-height: 1;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 1.5rem;
}

.timeline {
  position: relative;
  padding-left: 2rem;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #e8e8e8;
}

.timeline-item {
  position: relative;
  margin-bottom: 2rem;
}

.timeline-dot {
  position: absolute;
  left: -2rem;
  top: 0.5rem;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #1890ff;
  border: 3px solid white;
  box-shadow: 0 0 0 2px #1890ff;
}

.timeline-content {
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 8px;
}

.activity-meta {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
}

.activity-type-badge {
  padding: 2px 8px;
  background: #e6f7ff;
  color: #1890ff;
  border-radius: 4px;
  font-size: 0.8rem;
}

.activity-date {
  color: #999;
}

.activity-author {
  color: #666;
}

.activity-title {
  font-size: 1.1rem;
  color: #333;
  margin: 0.5rem 0;
}

.activity-desc {
  color: #666;
  line-height: 1.6;
  margin: 0.5rem 0;
}

.activity-images {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 0.5rem;
  margin-top: 1rem;
}

.activity-images img {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 6px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.pagination button {
  padding: 0.5rem 1rem;
  border: 1px solid #d9d9d9;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.empty-activities {
  text-align: center;
  padding: 3rem;
  color: #999;
}

.btn {
  display: inline-block;
  padding: 0.8rem 2rem;
  border-radius: 6px;
  text-decoration: none;
  font-weight: bold;
  transition: all 0.3s;
}

.btn-primary {
  background: #1890ff;
  color: white;
}

.btn-primary:hover {
  background: #40a9ff;
}

@media (max-width: 768px) {
  .pets-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
  }
}
</style>
