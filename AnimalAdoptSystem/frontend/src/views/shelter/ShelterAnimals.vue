<template>
  <div class="shelter-animals">
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
        <router-link to="/shelter/animals" class="nav-item active">
          <i class="nav-icon">🐾</i>
          <span>基地动物</span>
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
        <h1>基地动物管理</h1>
        <div class="header-actions">
          <button class="btn btn-primary" @click="openAddModal">
            <i class="btn-icon">➕</i>
            添加动物
          </button>
        </div>
      </div>
      
      <!-- 搜索和筛选 -->
      <div class="search-filter">
        <div class="search-box">
          <input type="text" placeholder="搜索宠物名称..." v-model="searchQuery" @input="searchAnimals">
          <button class="btn btn-secondary">搜索</button>
        </div>
        <div class="filter-box">
          <select v-model="filterStatus" @change="filterAnimals">
            <option value="">所有状态</option>
            <option value="available">可领养</option>
            <option value="adopted">已领养</option>
            <option value="pending">待审核</option>
          </select>
          <select v-model="filterSpecies" @change="filterAnimals">
            <option value="">所有种类</option>
            <option value="dog">狗</option>
            <option value="cat">猫</option>
            <option value="other">其他</option>
          </select>
        </div>
      </div>
      
      <!-- 宠物列表 -->
      <div class="animals-list">
        <div class="animal-card" v-for="animal in filteredAnimals" :key="animal.id">
          <div class="animal-image">
            <img :src="animal.images[0] || '@/assets/fengmian.jpg'" :alt="animal.name" @error="handleImageError">
          </div>
          <div class="animal-info">
            <h3>{{ animal.name }}</h3>
            <p class="animal-meta">{{ getSpeciesText(animal.species) }} · {{ animal.breed }} · {{ animal.age }}个月</p>
            <p class="animal-description">{{ animal.description }}</p>
            <div class="animal-stats">
              <span class="stat-item">性别: {{ getGenderText(animal.gender) }}</span>
              <span class="stat-item">体重: {{ animal.weight }}kg</span>
              <span class="stat-item">状态: <span class="status-badge" :class="animal.status">{{ getStatusText(animal.status) }}</span></span>
            </div>
            <div class="animal-actions">
              <button class="btn btn-sm btn-primary" @click="openEditModal(animal)">编辑</button>
              <button class="btn btn-sm btn-info" @click="viewAdoptionApplications(animal.id)">领养申请</button>
              <button class="btn btn-sm btn-danger" @click="deleteAnimal(animal.id)">删除</button>
            </div>
          </div>
        </div>
        <div class="empty-state" v-if="filteredAnimals.length === 0">
          <p>暂无宠物数据</p>
        </div>
      </div>
      
      <!-- 添加宠物模态框 -->
      <div class="modal" v-if="showAddModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>添加宠物</h2>
            <button class="btn-close" @click="showAddModal = false">×</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="addAnimal">
              <div class="form-group">
                <label for="name">宠物名称</label>
                <input type="text" id="name" v-model="newAnimal.name" required>
              </div>

              <div class="form-group">
                <label for="breed">品种 *</label>
                <div class="breed-input-container">
                  <input type="text" id="breed" v-model="newAnimal.breed" required placeholder="请输入品种或上传图片自动识别">
                  <button type="button" class="btn-identify" @click="openImageIdentify" :disabled="isIdentifying">
                    <i class="fa fa-camera"></i>
                    {{ isIdentifying ? '识别中...' : '图像识别' }}
                  </button>
                </div>
              </div>
              <div class="form-group">
                <label for="age">年龄 (个月)</label>
                <input type="number" id="age" v-model="newAnimal.age" min="1" required>
              </div>
              <div class="form-group">
                <label for="gender">性别</label>
                <select id="gender" v-model="newAnimal.gender" required>
                  <option value="male">公</option>
                  <option value="female">母</option>
                  <option value="unknown">未知</option>
                </select>
              </div>
              <div class="form-group">
                <label for="weight">体重 (kg)</label>
                <input type="number" id="weight" v-model="newAnimal.weight" step="0.1" min="0.1" required>
              </div>
              <div class="form-group">
                <label for="status">状态</label>
                <select id="status" v-model="newAnimal.status" required>
                  <option value="available">可领养</option>
                  <option value="adopted">已领养</option>
                  <option value="pending">待审核</option>
                </select>
              </div>
              <div class="form-group">
                <label for="description">描述</label>
                <textarea id="description" v-model="newAnimal.description" rows="3"></textarea>
              </div>
              <div class="form-group">
                <label for="health_status">健康状况</label>
                <input type="text" id="health_status" v-model="newAnimal.health_status">
              </div>
              <div class="form-group">
                <label for="found_place">发现地点</label>
                <input type="text" id="found_place" v-model="newAnimal.found_place">
              </div>
              <div class="form-group">
                <label for="found_date">发现日期</label>
                <input type="date" id="found_date" v-model="newAnimal.found_date">
              </div>
              <div class="form-group">
                <label>宠物照片</label>
                <div class="image-upload-area">
                  <div class="image-preview-container" v-if="newAnimal.images && newAnimal.images.length > 0">
                    <div class="image-preview" v-for="(image, index) in newAnimal.images" :key="index">
                      <img :src="image" :alt="'宠物照片 ' + (index + 1)">
                      <button type="button" class="remove-image-btn" @click="removeImage(index)">×</button>
                    </div>
                  </div>
                  <div class="upload-placeholder" @click="$refs.imageInput.click()">
                    <div class="upload-icon">📷</div>
                    <p>点击上传照片</p>
                    <p class="upload-hint">支持 JPG、PNG 格式，最多可上传5张</p>
                  </div>
                  <input 
                    type="file" 
                    ref="imageInput" 
                    accept="image/*" 
                    multiple 
                    @change="handleImageUpload" 
                    style="display: none"
                  >
                </div>
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
      
      <!-- 编辑宠物模态框 -->
      <div class="modal" v-if="showEditModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>编辑宠物</h2>
            <button class="btn-close" @click="showEditModal = false">×</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateAnimal">
              <div class="form-group">
                <label for="edit-name">宠物名称</label>
                <input type="text" id="edit-name" v-model="editAnimal.name" required>
              </div>

              <div class="form-group">
                <label for="edit-breed">品种</label>
                <input type="text" id="edit-breed" v-model="editAnimal.breed" required>
              </div>
              <div class="form-group">
                <label for="edit-age">年龄 (个月)</label>
                <input type="number" id="edit-age" v-model="editAnimal.age" min="1" required>
              </div>
              <div class="form-group">
                <label for="edit-gender">性别</label>
                <select id="edit-gender" v-model="editAnimal.gender" required>
                  <option value="male">公</option>
                  <option value="female">母</option>
                  <option value="unknown">未知</option>
                </select>
              </div>
              <div class="form-group">
                <label for="edit-weight">体重 (kg)</label>
                <input type="number" id="edit-weight" v-model="editAnimal.weight" step="0.1" min="0.1" required>
              </div>
              <div class="form-group">
                <label for="edit-status">状态</label>
                <select id="edit-status" v-model="editAnimal.status" required>
                  <option value="available">可领养</option>
                  <option value="adopted">已领养</option>
                  <option value="pending">待审核</option>
                </select>
              </div>
              <div class="form-group">
                <label for="edit-description">描述</label>
                <textarea id="edit-description" v-model="editAnimal.description" rows="3"></textarea>
              </div>
              <div class="form-group">
                <label for="edit-health_status">健康状况</label>
                <input type="text" id="edit-health_status" v-model="editAnimal.health_status">
              </div>
              <div class="form-group">
                <label for="edit-found_place">发现地点</label>
                <input type="text" id="edit-found_place" v-model="editAnimal.found_place">
              </div>
              <div class="form-group">
                <label for="edit-found_date">发现日期</label>
                <input type="date" id="edit-found_date" v-model="editAnimal.found_date">
              </div>
              <div class="form-group">
                <label>宠物照片</label>
                <div class="image-upload-area">
                  <div class="image-preview-container" v-if="editAnimal.images && editAnimal.images.length > 0">
                    <div class="image-preview" v-for="(image, index) in editAnimal.images" :key="index">
                      <img :src="image" :alt="'宠物照片 ' + (index + 1)">
                      <button type="button" class="remove-image-btn" @click="removeEditImage(index)">×</button>
                    </div>
                  </div>
                  <div class="upload-placeholder" @click="$refs.editImageInput.click()" v-if="!editAnimal.images || editAnimal.images.length < 5">
                    <div class="upload-icon">📷</div>
                    <p>点击上传更多照片</p>
                    <p class="upload-hint">支持 JPG、PNG 格式，最多可上传5张</p>
                  </div>
                  <input 
                    type="file" 
                    ref="editImageInput" 
                    accept="image/*" 
                    multiple 
                    @change="handleEditImageUpload" 
                    style="display: none"
                  >
                </div>
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
    
    <!-- 领养申请模态框 -->
    <div class="modal" v-if="showAdoptionModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>领养申请管理</h2>
          <button class="btn-close" @click="showAdoptionModal = false">×</button>
        </div>
        <div class="modal-body">
          <div v-if="loadingApplications" class="loading">加载中...</div>
          <div v-else-if="adoptionApplications.length === 0" class="empty-state">
            <p>暂无领养申请</p>
          </div>
          <div v-else class="adoption-applications-list">
            <div class="adoption-application-item" v-for="app in adoptionApplications" :key="app.id">
              <div class="application-header">
                <h3>申请人: {{ app.applicant.username }}</h3>
                <span class="status-badge" :class="app.status">{{ getApplicationStatusText(app.status) }}</span>
              </div>
              <div class="application-details">
                <p><strong>申请理由:</strong> {{ app.application_reason }}</p>
                <p><strong>个人信息:</strong> {{ app.personal_info }}</p>
                <p><strong>联系电话:</strong> {{ app.contact_phone }}</p>
                <p><strong>联系地址:</strong> {{ app.contact_address }}</p>
                <p><strong>申请时间:</strong> {{ formatDate(app.created_at) }}</p>
                <p v-if="app.reviewed_at"><strong>审核时间:</strong> {{ formatDate(app.reviewed_at) }}</p>
                <p v-if="app.review_comments"><strong>审核意见:</strong> {{ app.review_comments }}</p>
              </div>
              <div class="application-actions" v-if="app.status === 'pending'">
                <button class="btn btn-sm btn-success" @click="approveApplication(app.id)">通过</button>
                <button class="btn btn-sm btn-danger" @click="rejectApplication(app.id)">拒绝</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 图像识别模态框 -->
    <div class="modal" v-if="showIdentifyModal">
      <div class="modal-content identify-modal">
        <div class="modal-header">
          <h2>图像识别品种</h2>
          <button class="btn-close" @click="closeImageIdentify">×</button>
        </div>
        <div class="modal-body">
          <div class="upload-section">
            <div class="upload-area" @click="$refs.imageInput.click()">
              <input 
                ref="imageInput" 
                type="file" 
                accept="image/*" 
                @change="handleIdentifyImageUpload"
                style="display: none"
              >
              <div v-if="!selectedImage" class="upload-placeholder">
                <i class="fa fa-cloud-upload"></i>
                <p>点击上传动物图片</p>
                <p class="hint">支持 JPG、PNG 格式，最大 5MB</p>
              </div>
              <div v-else class="image-preview">
                <img :src="selectedImage" alt="预览图片">
              </div>
            </div>
          </div>
          
          <div class="result-section" v-if="identifyResult">
            <h3>识别结果</h3>
            <div class="result-item">
              <label>识别品种:</label>
              <span class="result-value">{{ identifyResult.breed }}</span>
            </div>
            <div class="result-item">
              <label>置信度:</label>
              <span class="result-value confidence">{{ (identifyResult.confidence * 100).toFixed(1) }}%</span>
            </div>
            <div class="result-item" v-if="identifyResult.baike_info && identifyResult.baike_info.description">
              <label>百科介绍:</label>
              <span class="result-value desc">{{ identifyResult.baike_info.description }}</span>
            </div>
          </div>
          
          <div class="error-message" v-if="error">
            {{ error }}
          </div>
        </div>
        <div class="modal-footer">
          <button 
            class="btn btn-primary" 
            @click="identifyBreed" 
            :disabled="!selectedImage || isIdentifying"
          >
            {{ isIdentifying ? '识别中...' : '开始识别' }}
          </button>
          <button 
            class="btn btn-secondary" 
            @click="closeImageIdentify"
            :disabled="isIdentifying"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { adoptionApi } from '@/api'

export default {
  name: 'ShelterAnimals',
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user')) || {},
      animals: [],
      searchQuery: '',
      filterStatus: '',
      filterSpecies: '',
      showAddModal: false,
      showEditModal: false,
      showIdentifyModal: false,
      isIdentifying: false,
      selectedImage: null,
      identifyResult: null,
      newAnimal: {
        name: '',
        species: 'dog',
        breed: '',
        age: '',
        gender: 'unknown',
        weight: '',
        status: 'available',
        description: '',
        health_status: '',
        found_place: '',
        found_date: '',
        images: []
      },
      editAnimal: {
        id: '',
        name: '',
        species: 'dog',
        breed: '',
        age: '',
        gender: 'unknown',
        weight: '',
        status: 'available',
        description: '',
        health_status: '',
        found_place: '',
        found_date: '',
        images: []
      },
      loading: false,
      error: '',
      success: '',
      showAdoptionModal: false,
      adoptionApplications: [],
      loadingApplications: false,
      currentAnimalId: null
    }
  },
  computed: {
    filteredAnimals() {
      let result = [...this.animals]
      
      console.log('计算filteredAnimals:', {
        animalsCount: this.animals.length,
        searchQuery: this.searchQuery,
        filterStatus: this.filterStatus,
        filterSpecies: this.filterSpecies,
        originalAnimals: this.animals.map(a => ({id: a.id, name: a.name, species: a.species, status: a.status}))
      })
      
      // 搜索
      if (this.searchQuery) {
        result = result.filter(animal => 
          animal.name.toLowerCase().includes(this.searchQuery.toLowerCase())
        )
      }
      
      // 状态筛选
      if (this.filterStatus) {
        result = result.filter(animal => animal.status === this.filterStatus)
      }
      
      // 种类筛选
      if (this.filterSpecies) {
        result = result.filter(animal => animal.species === this.filterSpecies)
      }
      
      console.log('过滤后结果数量:', result.length)
      return result
    }
  },
  mounted() {
    // 检查用户是否已登录且为基地管理员或系统管理员
    if (!this.user || (this.user.user_type !== 'shelter' && this.user.user_type !== 'admin')) {
      this.$router.push('/')
      return
    }
    
    // 获取动物列表
    this.fetchAnimals()
  },
  methods: {
    async fetchAnimals() {
      this.loading = true
      this.error = ''
      try {
        // 获取当前用户的基地ID
        const userId = this.user.id
        console.log('正在获取用户基地信息，用户ID:', userId)
        const response = await this.$axios.get(`/shelters/staff/user/${userId}/shelter/`)
        
        console.log('基地信息响应:', response)
        
        if (response.code === 200 && response.data) {
          let shelterId = null
          
          // 处理后端返回的数组数据
          if (Array.isArray(response.data)) {
            // 优先选择用户在User模型中关联的基地
            if (this.user.shelter && this.user.shelter.id) {
              const userAssignedShelter = response.data.find(item => item.shelter.id === this.user.shelter.id)
              if (userAssignedShelter) {
                shelterId = userAssignedShelter.shelter.id
              } else if (response.data.length > 0) {
                // 如果没有找到用户关联的基地，选择第一个管理员角色的基地
                const managerShelter = response.data.find(item => item.role === 'manager')
                if (managerShelter) {
                  shelterId = managerShelter.shelter.id
                } else {
                  // 如果没有管理员角色，选择第一个基地
                  shelterId = response.data[0].shelter.id
                }
              }
            } else {
              // 如果用户没有关联基地，选择第一个管理员角色的基地
              const managerShelter = response.data.find(item => item.role === 'manager')
              if (managerShelter) {
                shelterId = managerShelter.shelter.id
              } else if (response.data.length > 0) {
                // 如果没有管理员角色，选择第一个基地
                shelterId = response.data[0].shelter.id
              }
            }
          } else {
            // 如果是单个对象，直接使用
            shelterId = response.data.id
          }
          
          console.log('获取到基地ID:', shelterId)
          
          if (shelterId) {
            // 获取该基地的所有动物
            const animalsResponse = await this.$axios.get(`/animals/?shelter=${shelterId}`)
            
            console.log('动物数据响应:', animalsResponse)
            
            if (animalsResponse.code === 200 && animalsResponse.data) {
              // 确保处理分页数据
              let animalData = []
              if (Array.isArray(animalsResponse.data)) {
                animalData = animalsResponse.data
              } else if (animalsResponse.data.results) {
                animalData = animalsResponse.data.results
              } else {
                animalData = [animalsResponse.data]
              }
              
              this.animals = animalData.map(animal => ({
                ...animal,
                images: Array.isArray(animal.images) ? animal.images : []
              }))
              console.log('成功加载动物数据，数量:', this.animals.length)
              console.log('动物列表:', this.animals.map(a => ({id: a.id, name: a.name, status: a.status, species: a.species})))
            }
          } else {
            console.error('未找到基地ID')
            this.error = '未找到基地信息'
          }
        }
      } catch (error) {
        console.error('获取动物数据失败:', error)
        console.error('错误详情:', error.response?.data)
        this.error = '获取动物数据失败: ' + (error.response?.data?.message || error.response?.data?.detail || error.message)
      } finally {
        this.loading = false
      }
    },
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.$router.push('/login')
    },
    getSpeciesText(species) {
      const speciesMap = {
        'dog': '狗',
        'cat': '猫',
        'other': '其他'
      }
      return speciesMap[species] || species
    },
    getGenderText(gender) {
      const genderMap = {
        'male': '公',
        'female': '母',
        'unknown': '未知'
      }
      return genderMap[gender] || gender
    },
    getStatusText(status) {
      const statusMap = {
        'available': '可领养',
        'adopted': '已领养',
        'pending': '待审核'
      }
      return statusMap[status] || status
    },
    openAddModal() {
      // 重置表单
      this.newAnimal = {
        name: '',
        species: 'dog',
        breed: '',
        age: '',
        gender: 'unknown',
        weight: '',
        status: 'available',
        description: '',
        health_status: '',
        found_place: '',
        found_date: '',
        images: []
      }
      this.showAddModal = true
      this.error = ''
      this.success = ''
    },
    openEditModal(animal) {
      this.editAnimal = JSON.parse(JSON.stringify(animal))
      this.showEditModal = true
      this.error = ''
      this.success = ''
    },
    async addAnimal() {
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        // 获取当前用户的基地ID
        const userId = this.user.id
        const shelterResponse = await this.$axios.get(`/shelters/staff/user/${userId}/shelter/`)
        
        if (shelterResponse.code === 200 && shelterResponse.data) {
          let shelterId = null
          
          // 处理后端返回的数组数据
          if (Array.isArray(shelterResponse.data)) {
            // 优先选择用户在User模型中关联的基地
            if (this.user.shelter && this.user.shelter.id) {
              const userAssignedShelter = shelterResponse.data.find(item => item.shelter.id === this.user.shelter.id)
              if (userAssignedShelter) {
                shelterId = userAssignedShelter.shelter.id
              } else if (shelterResponse.data.length > 0) {
                // 如果没有找到用户关联的基地，选择第一个管理员角色的基地
                const managerShelter = shelterResponse.data.find(item => item.role === 'manager')
                if (managerShelter) {
                  shelterId = managerShelter.shelter.id
                } else {
                  // 如果没有管理员角色，选择第一个基地
                  shelterId = shelterResponse.data[0].shelter.id
                }
              }
            } else {
              // 如果用户没有关联基地，选择第一个管理员角色的基地
              const managerShelter = shelterResponse.data.find(item => item.role === 'manager')
              if (managerShelter) {
                shelterId = managerShelter.shelter.id
              } else if (shelterResponse.data.length > 0) {
                // 如果没有管理员角色，选择第一个基地
                shelterId = shelterResponse.data[0].shelter.id
              }
            }
          } else {
            // 如果是单个对象，直接使用
            shelterId = shelterResponse.data.id
          }
          
          if (shelterId) {
            // 准备动物数据，确保数据格式正确
            const animalData = {
              ...this.newAnimal,
              shelter: shelterId,
              // 确保日期格式正确
              found_date: this.newAnimal.found_date ? this.newAnimal.found_date : new Date().toISOString().split('T')[0]
            }
            
            // 确保必填字段都有值
            if (!animalData.name) {
              this.error = '请填写宠物名称'
              this.loading = false
              return
            }
            if (!animalData.breed) {
              this.error = '请填写宠物品种或使用图像识别功能'
              this.loading = false
              return
            }
            if (!animalData.description) {
              animalData.description = '暂无描述'
            }
            if (!animalData.personality) {
              animalData.personality = '暂无性格描述'
            }
            if (!animalData.health_status) {
              animalData.health_status = '健康'
            }
            if (!animalData.found_place) {
              animalData.found_place = '未知地点'
            }
            
            console.log('发送的动物数据:', animalData)
            const response = await this.$axios.post('/animals/', animalData)
            
            if (response.code === 200) {
              // 添加成功，重新加载数据
              await this.fetchAnimals()
              // 重置筛选器以确保能看到新添加的宠物
              this.resetFilters()
              this.showAddModal = false
              this.success = '宠物添加成功'
              
              // 3秒后清除成功信息
              setTimeout(() => {
                this.success = ''
              }, 3000)
            } else {
              this.error = response.message || '添加失败'
            }
          } else {
            console.error('未找到基地ID')
            this.error = '未找到基地信息'
          }
        }
      } catch (error) {
        console.error('添加动物失败:', error)
        console.error('错误详情:', error.response?.data)
        console.error('完整错误响应:', error.response)
        const errorMessage = error.response?.data?.message || error.response?.data?.detail || error.message
        const errorFields = error.response?.data?.errors || error.response?.data
        
        let fullErrorMessage = '添加失败: ' + errorMessage
        
        // 如果有字段错误，显示具体字段错误
        if (errorFields && typeof errorFields === 'object') {
          const fieldErrors = []
          for (const [field, errors] of Object.entries(errorFields)) {
            if (Array.isArray(errors)) {
              fieldErrors.push(`${field}: ${errors.join(', ')}`)
            }
          }
          if (fieldErrors.length > 0) {
            fullErrorMessage += '\n具体错误:\n' + fieldErrors.join('\n')
          }
        }
        
        this.error = fullErrorMessage
      } finally {
        this.loading = false
      }
    },
    async updateAnimal() {
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        const response = await this.$axios.put(`/animals/${this.editAnimal.id}/`, this.editAnimal)
        
        if (response.code === 200) {
          // 更新成功，重新加载数据
          await this.fetchAnimals()
          this.showEditModal = false
          this.success = '宠物信息更新成功'
          
          // 3秒后清除成功信息
          setTimeout(() => {
            this.success = ''
          }, 3000)
        } else {
          this.error = response.message || '更新失败'
        }
      } catch (error) {
        console.error('更新动物失败:', error)
        this.error = '更新失败: ' + (error.response?.data?.message || error.message)
      } finally {
        this.loading = false
      }
    },
    async deleteAnimal(id) {
      if (!confirm('确定要删除这个宠物吗？')) {
        return
      }
      
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        const response = await this.$axios.delete(`/animals/${id}/`)
        
        if (response.code === 200) {
          // 删除成功，重新加载数据
          await this.fetchAnimals()
          this.success = '宠物删除成功'
          
          // 3秒后清除成功信息
          setTimeout(() => {
            this.success = ''
          }, 3000)
        } else {
          this.error = response.message || '删除失败'
        }
      } catch (error) {
        console.error('删除动物失败:', error)
        this.error = '删除失败: ' + (error.response?.data?.message || error.message)
      } finally {
        this.loading = false
      }
    },
    handleImageUpload(event) {
      const files = event.target.files
      if (!files || files.length === 0) return
      
      // 限制最多上传5张图片
      const maxImages = 5
      const currentCount = this.newAnimal.images.length
      const canUpload = maxImages - currentCount
      
      if (canUpload <= 0) {
        this.error = '最多只能上传5张图片'
        setTimeout(() => { this.error = '' }, 3000)
        return
      }
      
      const filesToProcess = Array.from(files).slice(0, canUpload)
      
      filesToProcess.forEach(file => {
        // 验证文件类型
        if (!file.type.startsWith('image/')) {
          this.error = '请选择图片文件'
          setTimeout(() => { this.error = '' }, 3000)
          return
        }
        
        // 验证文件大小 (5MB)
        if (file.size > 5 * 1024 * 1024) {
          this.error = '图片大小不能超过5MB'
          setTimeout(() => { this.error = '' }, 3000)
          return
        }
        
        // 转换为 base64 或 URL
        const reader = new FileReader()
        reader.onload = (e) => {
          this.newAnimal.images.push(e.target.result)
        }
        reader.readAsDataURL(file)
      })
      
      // 清空input，允许重复选择同一文件
      event.target.value = ''
    },
    handleEditImageUpload(event) {
      const files = event.target.files
      if (!files || files.length === 0) return
      
      // 限制最多上传5张图片
      const maxImages = 5
      const currentCount = this.editAnimal.images.length
      const canUpload = maxImages - currentCount
      
      if (canUpload <= 0) {
        this.error = '最多只能上传5张图片'
        setTimeout(() => { this.error = '' }, 3000)
        return
      }
      
      const filesToProcess = Array.from(files).slice(0, canUpload)
      
      filesToProcess.forEach(file => {
        // 验证文件类型
        if (!file.type.startsWith('image/')) {
          this.error = '请选择图片文件'
          setTimeout(() => { this.error = '' }, 3000)
          return
        }
        
        // 验证文件大小 (5MB)
        if (file.size > 5 * 1024 * 1024) {
          this.error = '图片大小不能超过5MB'
          setTimeout(() => { this.error = '' }, 3000)
          return
        }
        
        // 转换为 base64 或 URL
        const reader = new FileReader()
        reader.onload = (e) => {
          this.editAnimal.images.push(e.target.result)
        }
        reader.readAsDataURL(file)
      })
      
      // 清空input，允许重复选择同一文件
      event.target.value = ''
    },
    removeImage(index) {
      this.newAnimal.images.splice(index, 1)
    },
    removeEditImage(index) {
      this.editAnimal.images.splice(index, 1)
    },
    searchAnimals() {
      // 搜索逻辑已在computed中处理
    },
    filterAnimals() {
      // 筛选逻辑已在computed中处理
    },
    resetFilters() {
      this.searchQuery = ''
      this.filterStatus = ''
      this.filterSpecies = ''
      console.log('筛选器已重置')
      // 显示重置成功的提示
      this.success = '筛选器已重置，显示所有宠物'
      setTimeout(() => {
        if (this.success === '筛选器已重置，显示所有宠物') {
          this.success = ''
        }
      }, 2000)
    },
    handleImageError(event) {
      // 当默认图片加载失败时，使用纯色背景
      event.target.src = ''
      event.target.style.backgroundColor = '#f0f0f0'
      event.target.style.display = 'flex'
      event.target.style.alignItems = 'center'
      event.target.style.justifyContent = 'center'
      event.target.style.fontSize = '14px'
      event.target.style.color = '#666'
      event.target.innerText = '暂无图片'
    },
    openImageIdentify() {
      this.showIdentifyModal = true
      this.selectedImage = null
      this.identifyResult = null
      this.error = ''
    },
    closeImageIdentify() {
      this.showIdentifyModal = false
      this.selectedImage = null
      this.identifyResult = null
      this.error = ''
    },
    handleIdentifyImageUpload(event) {
      const file = event.target.files[0]
      if (!file) return
      
      // 验证文件类型
      if (!file.type.startsWith('image/')) {
        this.error = '请选择图片文件'
        setTimeout(() => { this.error = '' }, 3000)
        return
      }
      
      // 验证文件大小 (5MB)
      if (file.size > 5 * 1024 * 1024) {
        this.error = '图片大小不能超过5MB'
        setTimeout(() => { this.error = '' }, 3000)
        return
      }
      
      // 显示预览
      const reader = new FileReader()
      reader.onload = (e) => {
        this.selectedImage = e.target.result
      }
      reader.readAsDataURL(file)
      
      // 清空input
      event.target.value = ''
    },
    async identifyBreed() {
      if (!this.selectedImage) {
        this.error = '请先选择图片'
        setTimeout(() => { this.error = '' }, 3000)
        return
      }
      
      this.isIdentifying = true
      this.error = ''
      this.identifyResult = null
      
      try {
        // 将base64图片数据发送到后端
        const response = await this.$axios.post('/animals/breed-identify/', {
          image_data: this.selectedImage
        })
        
        if (response.code === 200) {
          this.identifyResult = response.data
          // 自动填充品种字段
          this.newAnimal.breed = response.data.breed
          this.newAnimal.species = response.data.species || 'other'
          this.success = `识别成功: ${response.data.breed} (${(response.data.confidence * 100).toFixed(1)}%)`
          setTimeout(() => { this.success = '' }, 3000)
        } else {
          this.error = response.message || '识别失败'
        }
      } catch (error) {
        this.error = error.response?.data?.message || '识别失败，请检查网络连接'
      } finally {
        this.isIdentifying = false
      }
    },
    async viewAdoptionApplications(animalId) {
      this.currentAnimalId = animalId
      this.loadingApplications = true
      this.adoptionApplications = []
      this.showAdoptionModal = true
      
      try {
        const response = await adoptionApi.getAnimalApplications(animalId)
        
        if (response.code === 200 && response.data) {
          let applicationsData = []
          if (Array.isArray(response.data)) {
            applicationsData = response.data
          } else if (response.data.results) {
            applicationsData = response.data.results
          } else {
            applicationsData = [response.data]
          }
          
          this.adoptionApplications = applicationsData
        } else {
          this.error = response.message || '获取领养申请失败'
        }
      } catch (error) {
        console.error('获取领养申请失败:', error)
        this.error = '获取领养申请失败: ' + (error.response?.data?.message || error.message)
      } finally {
        this.loadingApplications = false
      }
    },
    async approveApplication(applicationId) {
      try {
        const response = await adoptionApi.reviewApplication(applicationId, {
          status: 'approved'
        })
        
        if (response.code === 200) {
          // 更新本地申请状态
          const index = this.adoptionApplications.findIndex(app => app.id === applicationId)
          if (index !== -1) {
            this.adoptionApplications[index].status = 'approved'
            this.adoptionApplications[index].reviewed_at = new Date().toISOString()
          }
          
          // 重新加载动物列表，以更新动物状态
          await this.fetchAnimals()
          
          this.success = '领养申请已通过'
          setTimeout(() => { this.success = '' }, 3000)
        } else {
          this.error = response.message || '审核失败'
        }
      } catch (error) {
        console.error('审核领养申请失败:', error)
        const errorMessage = error.response?.data?.message || error.message
        const errorDetails = error.response?.data?.details || ''
        this.error = `审核失败: ${errorMessage} ${errorDetails}`
      }
    },
    async rejectApplication(applicationId) {
      try {
        const response = await adoptionApi.reviewApplication(applicationId, {
          status: 'rejected'
        })
        
        if (response.code === 200) {
          // 更新本地申请状态
          const index = this.adoptionApplications.findIndex(app => app.id === applicationId)
          if (index !== -1) {
            this.adoptionApplications[index].status = 'rejected'
            this.adoptionApplications[index].reviewed_at = new Date().toISOString()
          }
          
          this.success = '领养申请已拒绝'
          setTimeout(() => { this.success = '' }, 3000)
        } else {
          this.error = response.message || '审核失败'
        }
      } catch (error) {
        console.error('审核领养申请失败:', error)
        const errorMessage = error.response?.data?.message || error.message
        const errorDetails = error.response?.data?.details || ''
        this.error = `审核失败: ${errorMessage} ${errorDetails}`
      }
    },
    getApplicationStatusText(status) {
      const statusMap = {
        'pending': '待审核',
        'approved': '审核通过',
        'rejected': '审核拒绝',
        'completed': '已领养',
        'cancelled': '已取消'
      }
      return statusMap[status] || status
    },
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.shelter-animals {
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

/* 宠物列表样式 */
.animals-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.animal-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  overflow: hidden;
  transition: all 0.3s ease;
}

.animal-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.animal-image {
  width: 100%;
  height: 200px;
  overflow: hidden;
}

.animal-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.animal-info {
  padding: 20px;
}

.animal-info h3 {
  margin: 0 0 10px 0;
  font-size: 20px;
  color: #333;
}

.animal-meta {
  margin: 0 0 15px 0;
  font-size: 14px;
  color: #666;
}

.animal-description {
  margin: 0 0 20px 0;
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}

.animal-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 20px;
  font-size: 14px;
  color: #666;
}

.stat-item {
  display: inline-block;
}

.status-badge {
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.status-badge.available {
  background-color: #e8f5e8;
  color: #388e3c;
}

.status-badge.adopted {
  background-color: #e3f2fd;
  color: #1976d2;
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

.animal-actions {
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

/* 领养申请列表样式 */
.adoption-applications-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.adoption-application-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  background-color: #f9f9f9;
  transition: all 0.3s ease;
}

.adoption-application-item:hover {
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.application-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e0e0e0;
}

.application-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.application-details {
  margin-bottom: 15px;
  font-size: 14px;
  line-height: 1.5;
  color: #666;
}

.application-details p {
  margin: 5px 0;
}

.application-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  padding-top: 10px;
  border-top: 1px solid #e0e0e0;
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

/* 图片上传样式 */
.image-upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  background-color: #fafafa;
  transition: all 0.3s ease;
}

.image-upload-area:hover {
  border-color: #ff9a3d;
  background-color: #f0f8f0;
}

.image-preview-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 15px;
  justify-content: flex-start;
}

.image-preview {
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-image-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: rgba(244, 67, 54, 0.8);
  color: white;
  border: none;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s ease;
}

.remove-image-btn:hover {
  background-color: rgba(244, 67, 54, 1);
}

.upload-placeholder {
  padding: 30px;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.upload-placeholder:hover {
  background-color: #e8f5e8;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.upload-placeholder p {
  margin: 5px 0;
  color: #666;
}

.upload-hint {
  font-size: 12px;
  color: #999;
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
  background-color: #4caf50;
  color: white;
}

.btn-success:hover {
  background-color: #388e3c;
}

.btn-info {
  background-color: #2196F3;
  color: white;
}

.btn-info:hover {
  background-color: #0b7dda;
}

.btn-icon {
  font-size: 16px;
}

/* 图像识别按钮样式 */
.breed-input-container {
  display: flex;
  gap: 10px;
}

.btn-identify {
  background: linear-gradient(135deg, #ff9a3d 0%, #ff6b6b 100%);
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 5px;
  white-space: nowrap;
}

.btn-identify:hover:not(:disabled) {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff9a3d 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(255, 107, 107, 0.3);
}

.btn-identify:disabled {
  background: #cccccc;
  cursor: not-allowed;
  transform: none;
}

/* 图像识别模态框样式 */
.identify-modal {
  max-width: 500px;
}

.upload-section {
  margin-bottom: 20px;
}

.upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 30px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #ffffff 0%, #fff5e6 100%);
}

.upload-area:hover {
  border-color: #ff9a3d;
  background: linear-gradient(135deg, #fff5e6 0%, #ffffff 100%);
}

.upload-placeholder {
  color: #999;
}

.upload-placeholder i {
  font-size: 48px;
  margin-bottom: 10px;
  display: block;
}

.upload-placeholder p {
  margin: 5px 0;
}

.upload-placeholder .hint {
  font-size: 12px;
  color: #bbb;
}

.image-preview {
  max-width: 100%;
  max-height: 300px;
  overflow: hidden;
  border-radius: 8px;
}

.image-preview img {
  width: 100%;
  height: auto;
  display: block;
}

.result-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.result-section h3 {
  margin-top: 0;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.result-item:last-child {
  border-bottom: none;
}

.result-item label {
  font-weight: bold;
  color: #666;
}

.result-value {
  color: #333;
  font-weight: 500;
}

.result-value.confidence {
  color: #ff9a3d;
  font-weight: bold;
}

.result-value.desc {
  font-size: 14px;
  line-height: 1.4;
  max-width: 200px;
  text-align: right;
}

.modal-footer {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding: 20px;
  border-top: 1px solid #eee;
}

.modal-footer .btn {
  min-width: 100px;
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
  .breed-input-container {
    flex-direction: column;
  }
  
  .btn-identify {
    width: 100%;
    justify-content: center;
  }
  
  .identify-modal {
    width: 95%;
    max-width: none;
  }
  
  .result-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .result-value.desc {
    text-align: left;
    max-width: 100%;
  }
  
  .modal-footer {
    flex-direction: column;
  }
  
  .modal-footer .btn {
    width: 100%;
  }
  .shelter-animals {
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
  
  .animals-list {
    grid-template-columns: 1fr;
  }
  
  .animal-stats {
    flex-direction: column;
    gap: 10px;
  }
  
  .modal-content {
    width: 95%;
    max-height: 95vh;
  }
  
  .image-preview {
    width: 80px;
    height: 80px;
  }
  
  .image-preview-container {
    justify-content: center;
  }
  
  .upload-placeholder {
    padding: 20px;
  }
  
  .upload-icon {
    font-size: 36px;
  }
}
</style>