<template>
  <div class="animals">
    <div class="container">
      <h2>流浪动物列表</h2>
      
      <div class="filter-bar">
        <div class="search-box">
          <input type="text" v-model="searchQuery" placeholder="搜索动物名称或品种" class="search-input">
          <button class="btn btn-secondary" @click="search">搜索</button>
        </div>
        <div class="filter-options">
          <select v-model="filterSpecies" class="filter-select">
            <option value="">全部物种</option>
            <option value="cat">猫</option>
            <option value="dog">狗</option>
            <option value="other">其他</option>
          </select>
          <select v-model="filterStatus" class="filter-select">
            <option value="">全部状态</option>
            <option value="available">可领养</option>
            <option value="adopted">已领养</option>
            <option value="medical">医疗中</option>
          </select>
        </div>
      </div>
      
      <div class="animals-grid" v-if="animals.length > 0">
        <div class="animal-card" v-for="animal in animals" :key="animal.id">
          <router-link :to="`/animal/${animal.id}`">
            <img v-if="animal.images && Array.isArray(animal.images) && animal.images.length > 0 && animal.images[0]" :src="animal.images[0]" :alt="animal.name" class="animal-image">
            <img v-else src="https://placehold.co/300x200?text=可爱的动物" :alt="animal.name" class="animal-image">
            <h4>{{ animal.name }}</h4>
            <p class="animal-info">{{ animal.species === 'cat' ? '猫' : animal.species === 'dog' ? '狗' : '其他' }} · {{ animal.breed }} · {{ animal.age }}个月</p>
            <p class="animal-shelter" v-if="animal.shelter_info">
              <i class="icon">🏠</i>
              {{ animal.shelter_info.name }}
            </p>
            <p class="animal-status" :class="animal.status">
              {{ animal.status === 'available' ? '可领养' : animal.status === 'adopted' ? '已领养' : animal.status === 'medical' ? '医疗中' : '审核中' }}
            </p>
            <p class="animal-desc">{{ animal.description.substring(0, 100) }}...</p>
            <button
                class="btn btn-secondary"
                v-if="animal.status === 'available'"
                @click.stop="applyForAdoption(animal.id)"
              >
                申请领养
              </button>

          </router-link>
        </div>
      </div>
      <div class="no-animals" v-else>
        <p>未找到符合条件的动物</p>
      </div>
      
      <div class="pagination" v-if="total > pageSize">
        <button class="btn btn-secondary" @click="prevPage" :disabled="currentPage === 1">上一页</button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <button class="btn btn-secondary" @click="nextPage" :disabled="currentPage === totalPages">下一页</button>
      </div>
    </div>
  </div>
</template>

<script>
import { animalApi } from '@/api'

export default {
  name: 'Animals',
  data() {
    return {
      animals: [],
      searchQuery: '',
      filterSpecies: '',
      filterStatus: '',
      currentPage: 1,
      pageSize: 12,
      total: 0,
      loading: false
    }
  },
  computed: {
    totalPages() {
      return Math.ceil(this.total / this.pageSize)
    }
  },
  mounted() {
    this.getAnimals()
  },
  methods: {

    // 在methods中添加
    applyForAdoption(animalId) {
      // 检查用户是否已登录
      const token = localStorage.getItem('token')
      if (!token) {
        this.$router.push('/login')
        return
      }
      // 跳转到申请页面
      this.$router.push(`/adoption/apply/${animalId}`)
    },

    async getAnimals() {
      this.loading = true
      try {
        console.log('发送请求到:', '/animals/')
        console.log('请求参数:', {
          search: this.searchQuery,
          species: this.filterSpecies,
          status: this.filterStatus,
          page: this.currentPage,
          page_size: this.pageSize
        })
        
        const response = await animalApi.getAnimals({
          search: this.searchQuery,
          species: this.filterSpecies,
          status: this.filterStatus,
          page: this.currentPage,
          page_size: this.pageSize
        })
        
        console.log('原始响应:', response)
        console.log('响应类型:', typeof response)
        console.log('响应结构:', Object.keys(response))
        
        // 处理不同的响应格式
        let animalsData = []
        let totalCount = 0
        
        // 优先检查DRF标准分页格式
        if (response.results && Array.isArray(response.results)) {
          console.log('检测到DRF分页格式')
          animalsData = response.results
          totalCount = response.count || animalsData.length
        } 
        // 检查自定义响应格式
        else if (response.code === 200 && response.data) {
          console.log('检测到自定义响应格式')
          if (Array.isArray(response.data)) {
            animalsData = response.data
            totalCount = animalsData.length
          } else if (response.data.results && Array.isArray(response.data.results)) {
            animalsData = response.data.results
            totalCount = response.data.count || animalsData.length
          } else {
            animalsData = [response.data]
            totalCount = 1
          }
        } 
        // 检查直接数组格式
        else if (Array.isArray(response)) {
          console.log('检测到直接数组格式')
          animalsData = response
          totalCount = response.length
        }
        // 检查单个对象格式
        else if (response.id) {
          console.log('检测到单个对象格式')
          animalsData = [response]
          totalCount = 1
        }
        else {
          console.log('未知响应格式')
          console.log('响应内容:', response)
          animalsData = []
          totalCount = 0
        }
        
        console.log('解析后的动物数据:', animalsData)
        console.log('总数:', totalCount)
        
        // 确保每个动物都有 images 数组
        this.animals = animalsData.map(animal => ({
          ...animal,
          images: Array.isArray(animal.images) ? animal.images : []
        }))
        this.total = totalCount
        
        console.log('最终动物列表:', this.animals)
      } catch (error) {
        console.error('获取动物列表失败:')
        console.error('错误对象:', error)
        console.error('错误信息:', error.message)
        if (error.response) {
          console.error('响应状态:', error.response.status)
          console.error('响应数据:', error.response.data)
          console.error('响应头:', error.response.headers)
        }
        // 显示用户友好的错误信息
        alert('获取动物列表失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    search() {
      this.currentPage = 1
      this.getAnimals()
    },
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--
        this.getAnimals()
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++
        this.getAnimals()
      }
    }
  },
  watch: {
    filterSpecies() {
      this.currentPage = 1
      this.getAnimals()
    },
    filterStatus() {
      this.currentPage = 1
      this.getAnimals()
    }
  }
}
</script>

<style scoped>
.animals {
  padding: 40px 0;
  background: linear-gradient(135deg, #fff8f0 0%, #ffeaa7 100%);
  min-height: 100vh;
}

.animals h2 {
  margin-bottom: 30px;
  font-size: 28px;
  color: #ff6b6b;
  background: linear-gradient(135deg, #ff6b6b 0%, #ff9a3d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-align: center;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 10px;
}

.search-box {
  display: flex;
  gap: 10px;
}

.search-input {
  padding: 12px;
  border: 2px solid #ffcc99;
  border-radius: 8px;
  font-size: 16px;
  width: 300px;
  background: linear-gradient(135deg, #ffffff 0%, #fff5e6 100%);
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #ff9a3d;
  box-shadow: 0 0 0 3px rgba(255, 154, 61, 0.2);
  transform: scale(1.02);
}

.filter-options {
  display: flex;
  gap: 10px;
}

.filter-select {
  padding: 12px;
  border: 2px solid #ffcc99;
  border-radius: 8px;
  font-size: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #fff5e6 100%);
  transition: all 0.3s ease;
}

.filter-select:focus {
  outline: none;
  border-color: #ff9a3d;
  box-shadow: 0 0 0 3px rgba(255, 154, 61, 0.2);
}

.animals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 30px;
  margin-bottom: 30px;
}

.animal-card {
  background: linear-gradient(135deg, #ffffff 0%, #fff5e6 100%);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 25px rgba(255, 154, 61, 0.2);
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 154, 61, 0.1);
}

.animal-card:hover {
  transform: translateY(-8px) scale(1.03);
  box-shadow: 0 15px 40px rgba(255, 154, 61, 0.4);
  border-color: rgba(255, 154, 61, 0.3);
}

.animal-card a {
  text-decoration: none;
  color: inherit;
  display: block;
}

.animal-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.animal-card h4 {
  font-size: 20px;
  margin: 15px;
}

.animal-info {
  margin: 0 15px 10px;
  font-size: 14px;
  color: #666;
}

.animal-shelter {
  margin: 0 15px 5px;
  font-size: 13px;
  color: #ff9a3d;
  display: flex;
  align-items: center;
  gap: 5px;
}

.animal-shelter .icon {
  font-size: 14px;
}

.animal-status {
  margin: 0 15px 10px;
  font-size: 14px;
  font-weight: bold;
  padding: 2px 8px;
  border-radius: 12px;
  display: inline-block;
}

.animal-status.available {
  color: #ff6b6b;
  background: linear-gradient(135deg, #ffebee 0%, #fff5e6 100%);
  border: 1px solid rgba(255, 107, 107, 0.2);
}

.animal-status.adopted {
  color: #ff9a3d;
  background: linear-gradient(135deg, #fff3e0 0%, #fff8f0 100%);
  border: 1px solid rgba(255, 154, 61, 0.2);
}

.animal-status.medical {
  color: #ff9a3d;
  background: linear-gradient(135deg, #fff8dc 0%, #fff5e6 100%);
  border: 1px solid rgba(255, 154, 61, 0.3);
}

.animal-desc {
  margin: 0 15px 15px;
  font-size: 14px;
  color: #333;
  line-height: 1.5;
}

.animal-card .btn {
  margin: 0 15px 15px;
}

.no-animals {
  text-align: center;
  padding: 40px;
  background: linear-gradient(135deg, #fff8f0 0%, #ffeaa7 100%);
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(255, 154, 61, 0.2);
  border: 2px dashed rgba(255, 154, 61, 0.3);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 30px;
}

.page-info {
  font-size: 16px;
  color: #666;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-primary {
  background: linear-gradient(135deg, #ff9a3d 0%, #ff6b6b 100%);
  color: white;
  border: none;
  box-shadow: 0 4px 10px rgba(255, 154, 61, 0.3);
}

.btn-primary:hover {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff9a3d 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(255, 107, 107, 0.4);
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

.btn:disabled {
  background: linear-gradient(135deg, #e0e0e0 0%, #f5f5f5 100%);
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}
</style>
