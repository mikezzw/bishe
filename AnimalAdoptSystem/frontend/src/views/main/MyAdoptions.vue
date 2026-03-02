<template>
  <div class="my-adoptions">
    <div class="container">
      <h2>我的领养记录</h2>
      
      <div class="loading" v-if="loading">
        <p>加载中...</p>
      </div>
      
      <div class="error-message" v-else-if="error">
        {{ error }}
        <button class="btn btn-secondary" @click="getMyApplications">重试</button>
      </div>
      
      <div class="adoption-list" v-else-if="applications.length > 0">
        <div class="adoption-item" v-for="app in applications" :key="app.id">
          <div class="adoption-header">
            <div class="adoption-info">
              <h3>{{ app.animal.name }}</h3>
              <p class="adoption-time">申请时间：{{ formatDate(app.created_at) }}</p>
            </div>
            <div class="adoption-status" :class="app.status">
              {{ app.status === 'pending' ? '待审核' : app.status === 'approved' ? '审核通过' : app.status === 'rejected' ? '审核拒绝' : app.status === 'completed' ? '已领养' : '已取消' }}
            </div>
          </div>
          <div class="adoption-content">
            <div class="animal-info">
              <img v-if="app.animal.images && app.animal.images.length > 0" :src="app.animal.images[0]" :alt="app.animal.name" class="animal-image">
              <img v-else src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20animal%20portrait&image_size=square" :alt="app.animal.name" class="animal-image">
              <div>
                <p>{{ app.animal.species === 'cat' ? '猫' : app.animal.species === 'dog' ? '狗' : '其他' }} · {{ app.animal.breed }} · {{ app.animal.age }}个月</p>
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
        </div>
      </div>
      
      <div class="no-adoptions" v-else>
        <p>您还没有提交过领养申请</p>
        <router-link to="/animals" class="btn btn-primary">去领养</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { adoptionApi } from '@/api'

export default {
  name: 'MyAdoptions',
  data() {
    return {
      applications: [],
      loading: true,
      error: ''
    }
  },
  mounted() {
    this.getMyApplications()
  },
  methods: {
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
    async getMyApplications() {
      this.loading = true
      this.error = ''
      try {
        const response = await adoptionApi.getMyApplications()
        console.log('领养申请API响应:', response)
        // 处理不同的响应格式
        let applicationsData = []
        
        // 检查自定义响应格式（后端返回的格式）
        if (response.code === 200 && response.data) {
          if (Array.isArray(response.data)) {
            applicationsData = response.data
            console.log('使用自定义响应格式，获取到', applicationsData.length, '条记录')
          } else if (response.data.results && Array.isArray(response.data.results)) {
            applicationsData = response.data.results
            console.log('使用自定义响应格式（带results），获取到', applicationsData.length, '条记录')
          } else {
            applicationsData = [response.data]
            console.log('使用自定义响应格式（单条），获取到1条记录')
          }
        } 
        // 优先检查DRF标准分页格式
        else if (response.results && Array.isArray(response.results)) {
          applicationsData = response.results
          console.log('使用DRF标准分页格式，获取到', applicationsData.length, '条记录')
        }
        // 检查直接数组格式
        else if (Array.isArray(response)) {
          applicationsData = response
          console.log('使用直接数组格式，获取到', applicationsData.length, '条记录')
        }
        else {
          console.log('未知响应格式:', response)
          applicationsData = []
        }
        
        // 去重处理
        const uniqueApplications = this.removeDuplicates(applicationsData)
        console.log('去重后记录数:', uniqueApplications.length)
        
        this.applications = uniqueApplications
      } catch (error) {
        console.error('获取领养记录失败:', error)
        this.error = '获取领养记录失败，请稍后重试'
      } finally {
        this.loading = false
      }
    },
    removeDuplicates(applications) {
      // 基于多个字段去重，避免显示相似的申请记录
      const seen = new Set()
      return applications.filter(app => {
        // 创建一个唯一标识符，基于动物ID、申请时间和联系电话
        const uniqueKey = `${app.animal.id}-${app.created_at}-${app.contact_phone}`
        if (seen.has(uniqueKey)) {
          return false
        }
        seen.add(uniqueKey)
        return true
      })
    }
  }
}
</script>

<style scoped>
.my-adoptions {
  padding: 40px 0;
  background: linear-gradient(135deg, #fff8f0 0%, #ffeaa7 100%);
  min-height: 100vh;
}

.my-adoptions h2 {
  margin-bottom: 30px;
  font-size: 28px;
  color: #333;
}

.adoption-list {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.adoption-item {
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.adoption-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background-color: #f9f9f9;
  border-bottom: 1px solid #eee;
}

.adoption-info h3 {
  font-size: 20px;
  margin: 0;
  color: #333;
}

.adoption-time {
  margin: 5px 0 0;
  font-size: 14px;
  color: #666;
}

.adoption-status {
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: bold;
}

.adoption-status.pending {
  background-color: #fff3e0;
  color: #ff9800;
}

.adoption-status.approved {
  background: linear-gradient(135deg, #ffebee 0%, #fff5e6 100%);
  color: #ff6b6b;
  border: 1px solid rgba(255, 107, 107, 0.2);
}

.adoption-status.rejected {
  background-color: #ffebee;
  color: #f44336;
}

.adoption-status.completed {
  background-color: #e3f2fd;
  color: #2196f3;
}

.adoption-status.cancelled {
  background-color: #f5f5f5;
  color: #9e9e9e;
}

.adoption-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.animal-info {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.animal-image {
  width: 150px;
  height: 100px;
  object-fit: cover;
  border-radius: 4px;
}

.animal-info div {
  flex: 1;
}

.animal-info p {
  margin: 0 0 10px;
  line-height: 1.5;
}

.application-info h4,
.review-info h4 {
  font-size: 16px;
  margin: 0 0 10px;
  color: #ff6b6b;
  background: linear-gradient(135deg, #ff6b6b 0%, #ff9a3d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.application-info p,
.review-info p {
  margin: 0 0 8px;
  line-height: 1.5;
}

.no-adoptions {
  text-align: center;
  padding: 40px;
  background: linear-gradient(135deg, #fff8f0 0%, #ffeaa7 100%);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  box-shadow: 0 4px 15px rgba(255, 154, 61, 0.2);
  border: 2px dashed rgba(255, 154, 61, 0.3);
}

.no-adoptions p {
  font-size: 18px;
  color: #666;
}

.btn {
  padding: 10px 20px;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
  text-decoration: none;
  display: inline-block;
  width: fit-content;
  align-self: center;
}

.btn-primary {
  background: linear-gradient(135deg, #ff9a3d 0%, #ff6b6b 100%);
  color: white;
  border: none;
  box-shadow: 0 4px 15px rgba(255, 154, 61, 0.3);
  font-weight: bold;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff9a3d 100%);
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
}

@media (max-width: 768px) {
  .adoption-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .animal-info {
    flex-direction: column;
  }
  
  .animal-image {
    width: 100%;
    height: 200px;
  }
}
</style>
