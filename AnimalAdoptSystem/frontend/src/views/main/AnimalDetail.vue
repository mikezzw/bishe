<template>
  <div class="animal-detail">
    <div class="container">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>正在加载动物详情...</p>
      </div>
      
      <!-- 错误状态 -->
      <div v-else-if="error" class="error">
        <div class="error-icon">⚠️</div>
        <h3>加载失败</h3>
        <p>{{ error }}</p>
        <button @click="getAnimalDetail" class="btn btn-primary">重新加载</button>
      </div>
      
      <!-- 成功显示动物详情 -->
      <div v-else-if="animal" class="animal-content">
        <div class="animal-images">
          <img :src="currentImage" :alt="animal.name" class="main-image">
          <div class="thumbnail-list" v-if="animal.images && animal.images.length > 1">
            <img 
              v-for="(image, index) in animal.images" 
              :key="index" 
              :src="image" 
              :alt="animal.name" 
              class="thumbnail" 
              :class="{ active: currentIndex === index }"
              @click="currentIndex = index"
            >
          </div>
        </div>
        
        <div class="animal-info">
          <h2>{{ animal.name }}</h2>
          <div class="basic-info">
            <div class="info-item">
              <span class="label">物种：</span>
              <span class="value">{{ animal.species === 'cat' ? '猫' : animal.species === 'dog' ? '狗' : '其他' }}</span>
            </div>
            <div class="info-item">
              <span class="label">品种：</span>
              <span class="value">{{ animal.breed }}</span>
            </div>
            <div class="info-item">
              <span class="label">年龄：</span>
              <span class="value">{{ animal.age }}个月</span>
            </div>
            <div class="info-item">
              <span class="label">性别：</span>
              <span class="value">{{ animal.gender === 'male' ? '公' : animal.gender === 'female' ? '母' : '未知' }}</span>
            </div>
            <div class="info-item">
              <span class="label">体重：</span>
              <span class="value">{{ animal.weight }}kg</span>
            </div>
            <div class="info-item">
              <span class="label">状态：</span>
              <span class="value" :class="animal.status">
                {{ animal.status === 'available' ? '可领养' : animal.status === 'adopted' ? '已领养' : animal.status === 'medical' ? '医疗中' : '审核中' }}
              </span>
            </div>
            <div class="info-item">
              <span class="label">发现地点：</span>
              <span class="value">{{ animal.found_place }}</span>
            </div>
            <div class="info-item">
              <span class="label">发现日期：</span>
              <span class="value">{{ animal.found_date }}</span>
            </div>
          </div>
          
          <div class="description">
            <h3>动物描述</h3>
            <p>{{ animal.description }}</p>
          </div>
          
          <div class="personality">
            <h3>性格特点</h3>
            <p>{{ animal.personality }}</p>
          </div>
          
          <div class="health">
            <h3>健康状况</h3>
            <p>{{ animal.health_status }}</p>
          </div>
          
          <!-- 云领养提醒 -->
          <div class="cloud-adoption-alert" v-if="animal.status === 'available'">
            <div class="alert-icon">☁️</div>
            <div class="alert-content">
              <h4>云领养说明</h4>
              <p>动物将留在基地由专业人员照顾，您可远程关爱并申请线下互动</p>
              <router-link to="/shelters" class="alert-link">了解更多互动方式</router-link>
            </div>
          </div>
          
          <div class="actions">
            <router-link :to="`/adoption/apply/${animal.id}`" class="btn btn-primary" v-if="animal.status === 'available'">申请领养</router-link>
            <button class="btn btn-secondary" disabled v-else>无法领养</button>
          </div>
          <div class="personality-section">
            <PersonalityTest @match-calculated="showMatchResult" />
            <div v-if="matchResult" class="match-result">
              <h4>匹配度: {{ matchResult.match_percentage }}%</h4>
              <p>这只{{ animal.name }}与您的性格匹配度为{{ matchResult.match_percentage }}%</p>
            </div>
          </div>

        </div>
      </div>

      <!-- 无数据状态 -->
      <div v-else class="no-data">
        <p>未找到该动物的信息</p>
      </div>
    </div>
  </div>
</template>

<script>
import PersonalityTest from '@/components/PersonalityTest.vue'

export default {
  name: 'AnimalDetail',
  components: {
    PersonalityTest
  },
  data() {
    return {
      animal: null,
      currentIndex: 0,
      matchResult: null,
      loading: true,
      error: null
    }
  },
  computed: {
    currentImage() {
      if (this.animal && this.animal.images && Array.isArray(this.animal.images) && this.animal.images.length > 0 && this.animal.images[this.currentIndex]) {
        return this.animal.images[this.currentIndex]
      }
      return 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20animal%20portrait&image_size=landscape_16_9'
    }
  },
  mounted() {
    this.getAnimalDetail()
  },
  methods: {
    async getAnimalDetail() {
      this.loading = true
      this.error = null
      
      try {
        const { id } = this.$route.params
        console.log('请求动物ID:', id)
        console.log('完整请求URL:', `/animals/${id}/`)
        
        const response = await this.$axios.get(`/animals/${id}/`)
        console.log('动物详情原始响应:', response)
        console.log('响应类型:', typeof response)
        console.log('是否有data属性:', response.hasOwnProperty('data'))
        
        // 处理不同的响应格式 - 兼容模式
        if (response && typeof response === 'object') {
          // 情况1: 直接返回动物对象 {id: 1, name: '小白', ...}
          if (response.id) {
            console.log('检测到直接数据格式')
            this.animal = response
          }
          // 情况2: 包装格式 {code: 200, data: {id: 1, ...}}
          else if (response.code === 200 && response.data) {
            console.log('检测到包装格式 (code-data)')
            this.animal = response.data
          }
          // 情况3: DRF默认格式 {data: {id: 1, ...}}
          else if (response.data && response.data.id) {
            console.log('检测到DRF默认格式')
            this.animal = response.data
          }
          // 情况4: 其他情况
          else {
            console.log('使用原始响应作为动物数据')
            this.animal = response
          }
        } else {
          console.warn('响应不是对象格式:', response)
          this.animal = response
        }
        
        console.log('处理后的动物数据:', this.animal)
        
        // 确保图片数组存在且为数组类型
        if (this.animal) {
          if (!this.animal.images || !Array.isArray(this.animal.images)) {
            console.log('图片数据不存在或不是数组，初始化为空数组')
            this.animal.images = []
          } else {
            console.log('图片数据:', this.animal.images)
          }
        }
      } catch (error) {
        console.error('获取动物详情失败:')
        console.error('- 错误对象:', error)
        console.error('- 错误消息:', error.message)
        console.error('- 响应状态:', error.response?.status)
        console.error('- 响应数据:', error.response?.data)
        
        this.error = `获取动物详情失败: ${error.response?.status || '网络错误'} - ${error.message}`
        this.animal = null
      } finally {
        this.loading = false
      }
    },
    showMatchResult(result) {
      this.matchResult = result
      console.log('匹配结果:', result)
    }
  }
}
</script>

<style scoped>
.animal-detail {
  padding: 40px 0;
  background: linear-gradient(135deg, #fff8f0 0%, #ffeaa7 100%);
  min-height: 100vh;
}

.animal-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  padding: 40px;
}

.animal-images {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.main-image {
  width: 100%;
  height: 400px;
  object-fit: cover;
  border-radius: 8px;
}

.thumbnail-list {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 10px;
}

.thumbnail {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.3s, transform 0.3s;
}

.thumbnail:hover {
  opacity: 0.8;
  transform: scale(1.05);
}

.thumbnail.active {
  opacity: 1;
  border: 2px solid #ff9a3d;
}

.animal-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.animal-info h2 {
  font-size: 32px;
  color: #333;
  margin-bottom: 10px;
}

.basic-info {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 5px;
  background-color: #f9f9f9;
  padding: 8px 12px;
  border-radius: 4px;
  flex: 1 1 calc(50% - 15px);
}

.label {
  font-weight: bold;
  color: #666;
}

.value {
  color: #333;
}

.value.available {
  color: #ff9a3d;
  font-weight: bold;
}

.value.adopted {
  color: #9e9e9e;
  font-weight: bold;
}

.value.medical {
  color: #ff9800;
  font-weight: bold;
}

.description,
.personality,
.health {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
}

.description h3,
.personality h3,
.health h3 {
  font-size: 18px;
  margin-bottom: 10px;
  color: #ff9a3d;
}

.description p,
.personality p,
.health p {
  line-height: 1.6;
  color: #333;
}

.actions {
  margin-top: 20px;
}

.btn {
  padding: 12px 24px;
  border-radius: 4px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background: linear-gradient(135deg, #ff9a3d 0%, #ff6b6b 100%);
  color: white;
  border: none;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff9a3d 100%);
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
}

.btn-secondary {
  background-color: #f5f5f5;
  color: #9e9e9e;
  border: 1px solid #ddd;
}

.loading, .error, .no-data {
  text-align: center;
  padding: 60px 40px;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin: 20px 0;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #ff9a3d;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.error h3 {
  color: #f44336;
  margin-bottom: 15px;
}

.error p {
  color: #666;
  margin-bottom: 20px;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .animal-content {
    grid-template-columns: 1fr;
    padding: 20px;
  }
  
  .main-image {
    height: 300px;
  }
  
  .info-item {
    flex: 1 1 100%;
  }
}

/* 新增的加载和错误状态样式 */
.loading, .error, .no-data {
  text-align: center;
  padding: 60px 40px;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin: 20px 0;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #ff9a3d;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.error h3 {
  color: #f44336;
  margin-bottom: 15px;
}

.error p {
  color: #666;
  margin-bottom: 20px;
  line-height: 1.6;
}

/* 云领养提醒样式 */
.cloud-adoption-alert {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border: 1px solid #2196f3;
  border-radius: 8px;
  padding: 15px;
  margin: 20px 0;
  display: flex;
  align-items: center;
  gap: 15px;
}

.alert-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.alert-content h4 {
  margin: 0 0 8px 0;
  color: #1976d2;
  font-size: 18px;
}

.alert-content p {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 14px;
  line-height: 1.4;
}

.alert-link {
  color: #2196f3;
  text-decoration: none;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.3s ease;
}

.alert-link:hover {
  color: #0d47a1;
  text-decoration: underline;
}
</style>
