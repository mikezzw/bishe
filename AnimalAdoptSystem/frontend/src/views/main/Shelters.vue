<template>
  <div class="shelters-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <h1>动物基地列表</h1>
        <p>发现并了解各个动物救助基地</p>
      </div>
    </div>

    <!-- 搜索和筛选区域 -->
    <div class="search-section">
      <div class="container">
        <div class="search-bar">
          <input 
            type="text" 
            placeholder="搜索基地名称或地址..." 
            v-model="searchQuery"
            @input="handleSearch"
            class="search-input"
          >
          <button class="search-btn" @click="searchShelters">
            <i class="search-icon">🔍</i>
            搜索
          </button>
        </div>
        
        <div class="filters">
          <select v-model="selectedProvince" @change="filterByLocation" class="filter-select">
            <option value="">选择省份</option>
            <option value="北京市">北京市</option>
            <option value="上海市">上海市</option>
            <option value="广东省">广东省</option>
            <option value="浙江省">浙江省</option>
            <option value="江苏省">江苏省</option>
            <option value="四川省">四川省</option>
          </select>
          
          <select v-model="sortBy" @change="sortShelters" class="filter-select">
            <option value="name">按名称排序</option>
            <option value="animals_count">按动物数量排序</option>
            <option value="created_at">按创建时间排序</option>
          </select>
        </div>
      </div>
    </div>

    <!-- 基地列表 -->
    <div class="shelters-list">
      <div class="container">
        <div v-if="loading" class="loading">
          <div class="spinner"></div>
          <p>正在加载基地信息...</p>
        </div>
        
        <div v-else-if="shelters.length === 0" class="no-results">
          <i class="empty-icon">📭</i>
          <h3>暂无符合条件的基地</h3>
          <p>请尝试调整搜索条件</p>
        </div>
        
        <div v-else class="shelters-grid">
          <div 
            v-for="shelter in displayedShelters" 
            :key="shelter.id" 
            class="shelter-card"
            @click="viewShelterDetails(shelter)"
          >
            <div class="shelter-image">
              <img 
                :src="getImageUrl(shelter.image)"
                :alt="shelter.name"
                @error="handleImageError"
              >
              <div class="shelter-status" :class="shelter.status">
                {{ shelter.status === 'active' ? '运营中' : '暂停运营' }}
              </div>
            </div>
            
            <div class="shelter-info">
              <h3 class="shelter-name">{{ shelter.name }}</h3>
              <p class="shelter-address">
                <i class="icon">📍</i>
                {{ shelter.address }}
              </p>
              
              <div class="shelter-stats">
                <div class="stat-item">
                  <span class="stat-number">{{ shelter.current_animals }}</span>
                  <span class="stat-label">救助动物</span>
                </div>
                <div class="stat-item">
                  <span class="stat-number">{{ shelter.capacity }}</span>
                  <span class="stat-label">容纳能力</span>
                </div>
                <div class="stat-item">
                  <span class="stat-number">{{ shelter.adoption_rate || 0 }}%</span>
                  <span class="stat-label">领养率</span>
                </div>
              </div>
              
              <p class="shelter-description">{{ truncateDescription(shelter.description) }}</p>
              
              <!-- 可申请的活动 -->
              <div class="shelter-activities" v-if="shelter.activities && shelter.activities.length > 0">
                <h4 class="activities-title">可申请活动</h4>
                <div class="activities-list">
                  <div 
                    v-for="activity in shelter.activities.slice(0, 2)" 
                    :key="activity.id" 
                    class="activity-item"
                    @click.stop="applyForActivity(activity, shelter)"
                  >
                    <span class="activity-name">{{ activity.title }}</span>
                    <span class="activity-type" :class="activity.activity_type">
                      {{ getActivityTypeText(activity.activity_type) }}
                    </span>
                  </div>
                  <div v-if="shelter.activities.length > 2" class="more-activities">
                    还有 {{ shelter.activities.length - 2 }} 个活动...
                  </div>
                </div>
              </div>
              <div class="shelter-activities empty" v-else>
                <p>暂无可申请的活动</p>
              </div>
              
              <div class="shelter-contact">
                <span class="contact-item">
                  <i class="icon">📞</i>
                  {{ shelter.contact_phone }}
                </span>
                <span class="contact-item">
                  <i class="icon">✉️</i>
                  {{ shelter.email }}
                </span>
              </div>
              
              <div class="shelter-actions">
                <button class="btn btn-primary" @click.stop="viewShelterDetails(shelter)">
                  查看详情
                </button>
                <button class="btn btn-secondary" @click.stop="contactShelter(shelter)">
                  联系基地
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 分页 -->
        <div v-if="shelters.length > 0" class="pagination">
          <button 
            class="page-btn" 
            :disabled="currentPage === 1"
            @click="prevPage"
          >
            上一页
          </button>
          
          <span class="page-info">
            第 {{ currentPage }} 页，共 {{ totalPages }} 页
          </span>
          
          <button 
            class="page-btn" 
            :disabled="currentPage === totalPages"
            @click="nextPage"
          >
            下一页
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { shelterApi } from '@/api'

export default {
  name: 'Shelters',
  data() {
    return {
      shelters: [],
      currentPage: 1,
      itemsPerPage: 6,
      total: 0,
      searchQuery: '',
      selectedProvince: '',
      sortBy: 'name',
      loading: false,
      error: ''
    }
  },
  
  computed: {
    displayedShelters() {
      const startIndex = (this.currentPage - 1) * this.itemsPerPage
      const endIndex = startIndex + this.itemsPerPage
      return this.shelters.slice(startIndex, endIndex)
    },
    
    totalPages() {
      return Math.ceil(this.total / this.itemsPerPage)
    }
  },
  
  async mounted() {
    await this.loadShelters()
  },
  
  methods: {
    getImageUrl(image) {
      // 如果是数组，取第一个元素
      if (Array.isArray(image) && image.length > 0) {
        image = image[0]
      }
          
      if (!image) {
        return 'https://via.placeholder.com/300x200?text=基地图片'
      }
      // 如果是 Base64 编码 (包含 data:image 前缀)
      if (typeof image === 'string' && image.startsWith('data:image')) {
        return image
      }
      // 如果是普通 URL(以 http 开头)
      else if (typeof image === 'string' && image.startsWith('http')) {
        return image
      }
      // 如果是纯 Base64 数据 (没有 data:image 前缀)
      else if (typeof image === 'string') {
        // 假设为 Base64 编码，添加前缀
        return `data:image/jpeg;base64,${image}`
      }
      // 其他情况返回默认图片
      return 'https://via.placeholder.com/300x200?text=基地图片'
    },
    
    async loadShelters() {
      this.loading = true
      try {
        const params = {}
        
        // 添加搜索和筛选参数（移除分页参数，使用前端分页）
        if (this.searchQuery) {
          params.search = this.searchQuery
        }
        if (this.selectedProvince) {
          params.province = this.selectedProvince
        }
        if (this.sortBy) {
          params.ordering = this.sortBy
        }
        
        const response = await shelterApi.getShelters(params)
        
        console.log('获取基地列表响应:', response)
        
        // 处理分页响应
        let shelters = []
        if (response.data && response.data.results && Array.isArray(response.data.results)) {
          // 后端 API 格式：{code: 200, message: '...', data: {results: [...], count: ...}}
          shelters = response.data.results
          this.total = response.data.count || response.data.results.length
        } else if (response.results && Array.isArray(response.results)) {
          // DRF 标准格式：{results: [...], count: ...}
          shelters = response.results
          this.total = response.count || response.results.length
        } else if (Array.isArray(response)) {
          // 如果直接返回数组
          shelters = response
          this.total = response.length
        } else {
          // 处理其他可能的响应格式
          shelters = []
          this.total = 0
        }
        
        // 为每个基地获取活动数据
        const sheltersWithActivities = await Promise.all(
          shelters.map(async (shelter) => {
            try {
              const activitiesResponse = await shelterApi.getShelterActivities(shelter.id)
              console.log(`获取基地 ${shelter.name} 的活动响应:`, activitiesResponse)
              if (activitiesResponse && activitiesResponse.data) {
                if (activitiesResponse.data.results && Array.isArray(activitiesResponse.data.results)) {
                  // 后端API格式: {code: 200, message: '获取基地活动成功', data: {results: [...]}}
                  shelter.activities = activitiesResponse.data.results
                  console.log(`基地 ${shelter.name} 的活动数量:`, activitiesResponse.data.results.length)
                } else if (Array.isArray(activitiesResponse.data)) {
                  // 后端API格式: {code: 200, message: '获取基地活动成功', data: [...]}
                  shelter.activities = activitiesResponse.data
                  console.log(`基地 ${shelter.name} 的活动数量:`, activitiesResponse.data.length)
                } else {
                  console.error(`基地 ${shelter.name} 的活动响应数据格式错误:`, activitiesResponse.data)
                  shelter.activities = []
                }
              } else if (activitiesResponse.results && Array.isArray(activitiesResponse.results)) {
                // DRF分页格式
                shelter.activities = activitiesResponse.results
                console.log(`基地 ${shelter.name} 的活动数量:`, activitiesResponse.results.length)
              } else if (Array.isArray(activitiesResponse)) {
                // 直接数组格式
                shelter.activities = activitiesResponse
                console.log(`基地 ${shelter.name} 的活动数量:`, activitiesResponse.length)
              } else {
                console.error(`基地 ${shelter.name} 的活动响应格式错误:`, activitiesResponse)
                shelter.activities = []
              }
            } catch (error) {
              console.error(`获取基地 ${shelter.name} 的活动失败:`, error)
              shelter.activities = []
            }
            return shelter
          })
        )
        
        this.shelters = sheltersWithActivities
        console.log('加载完成，基地数量:', this.shelters.length)
        if (this.shelters.length > 0) {
          console.log('第一个基地的活动数量:', this.shelters[0]?.activities?.length || 0)
        } else {
          console.log('暂无基地数据')
        }
      } catch (error) {
        console.error('加载基地列表失败:', error)
        this.error = '加载基地列表失败，请稍后重试'
        this.shelters = []
        this.total = 0
      } finally {
        this.loading = false
      }
    },
    

    
    async handleSearch() {
      this.currentPage = 1
      await this.loadShelters()
    },
    
    searchShelters() {
      this.handleSearch()
    },
    
    async filterByLocation() {
      this.currentPage = 1
      await this.loadShelters()
    },
    
    async sortShelters() {
      this.currentPage = 1
      await this.loadShelters()
    },
    
    viewShelterDetails(shelter) {
      // 显示基地详情模态框
      this.showShelterDetail(shelter)
    },
    
    contactShelter(shelter) {
      // 显示联系基地模态框
      this.showContactModal(shelter)
    },
    
    applyForActivity(activity, shelter) {
      // 检查用户是否已登录
      const token = localStorage.getItem('token')
      if (!token) {
        this.$router.push('/login')
        return
      }
      
      // 显示活动申请模态框
      this.showActivityApplicationModal(activity, shelter)
    },
    
    getActivityTypeText(type) {
      const typeMap = {
        'adoption': '领养活动',
        'volunteer': '志愿活动',
        'fundraising': '筹款活动',
        'education': '教育活动',
        'other': '其他活动'
      }
      return typeMap[type] || type
    },
    
    showActivityApplicationModal(activity, shelter) {
      // 创建活动申请模态框
      const modal = document.createElement('div')
      modal.className = 'modal-overlay'
      modal.innerHTML = `
        <div class="modal-content activity-modal">
          <div class="modal-header">
            <h2>申请参与活动</h2>
            <button class="close-btn" onclick="this.closest('.modal-overlay').remove()">×</button>
          </div>
          <div class="modal-body">
            <div class="activity-info">
              <h3>${activity.title}</h3>
              <p class="activity-type-tag ${activity.activity_type}">
                ${this.getActivityTypeText(activity.activity_type)}
              </p>
              <p><strong>基地：</strong>${shelter.name}</p>
              <p><strong>地点：</strong>${activity.location}</p>
              <p><strong>时间：</strong>${new Date(activity.start_time).toLocaleString()}</p>
              <p><strong>描述：</strong>${activity.description}</p>
            </div>
            <div class="application-form">
              <h4>申请信息</h4>
              <div class="form-group">
                <label>申请类型</label>
                <select id="applicationType" class="form-control">
                  <option value="visit">探访</option>
                  <option value="volunteer">志愿服务</option>
                  <option value="foster">寄养</option>
                  <option value="other">其他</option>
                </select>
              </div>
              <div class="form-group">
                <label>申请目的</label>
                <textarea id="applicationPurpose" class="form-control" rows="3" placeholder="请输入您的申请目的..."></textarea>
              </div>
              <div class="form-group">
                <label>期望参与日期</label>
                <input type="datetime-local" id="desiredDate" class="form-control">
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">取消</button>
            <button class="btn btn-primary" onclick="this.closest('.modal-overlay').querySelector('.submit-application').click()">提交申请</button>
          </div>
        </div>
      `
      
      // 添加提交按钮的事件处理
      const submitBtn = document.createElement('button')
      submitBtn.className = 'submit-application'
      submitBtn.style.display = 'none'
      submitBtn.onclick = () => this.submitActivityApplication(activity, shelter, modal)
      modal.appendChild(submitBtn)
      
      document.body.appendChild(modal)
      this.addModalStyles()
    },
    
    async submitActivityApplication(activity, shelter, modal) {
      try {
        const applicationType = modal.querySelector('#applicationType').value
        const purpose = modal.querySelector('#applicationPurpose').value
        const desiredDate = modal.querySelector('#desiredDate').value
        
        if (!purpose || !desiredDate) {
          alert('请填写完整的申请信息')
          return
        }
        
        // 提交申请到后端
        const response = await shelterApi.submitInteraction(shelter.id, {
          activity: activity.id,
          application_type: applicationType,
          purpose: purpose,
          desired_date: new Date(desiredDate).toISOString()
        })
        
        if (response.code === 200) {
          alert('申请提交成功，等待基地审核')
          modal.remove()
        } else {
          alert('申请提交失败：' + response.message)
        }
      } catch (error) {
        console.error('提交申请失败:', error)
        alert('申请提交失败，请稍后重试')
      }
    },
    
    async showShelterDetail(shelter) {
      // 创建详情模态框
      const modal = document.createElement('div')
      modal.className = 'modal-overlay'
              
      // 处理 QR 码 URL - 从数组中获取第一个
      let qrCodeUrl = null
      if (shelter.qr_code !== undefined && shelter.qr_code !== null && Array.isArray(shelter.qr_code) && shelter.qr_code.length > 0) {
        qrCodeUrl = this.getImageUrl(shelter.qr_code[0])
      }
              
      modal.innerHTML = `
        <div class="modal-content">
          <div class="modal-header">
            <h2>${shelter.name} 详情</h2>
            <button class="close-btn" onclick="this.closest('.modal-overlay').remove()">×</button>
          </div>
          <div class="modal-body">
            <div class="detail-section">
              <h3>基本信息</h3>
              <p><strong>地址:</strong>${shelter.address}</p>
              <p><strong>联系人:</strong>${shelter.contact_name}</p>
              <p><strong>联系电话:</strong>${shelter.contact_phone}</p>
              <p><strong>邮箱:</strong>${shelter.email}</p>
              <p><strong>网站:</strong>${shelter.website || '暂无'}</p>
            </div>
            <div class="detail-section">
              <h3>运营信息</h3>
              <p><strong>容纳能力:</strong>${shelter.capacity} 只动物</p>
              <p><strong>当前动物数:</strong>${shelter.current_animals} 只</p>
              <p><strong>领养率:</strong>${shelter.adoption_rate || 0}%</p>
              <p><strong>状态:</strong><span class="status ${shelter.status}">${shelter.status === 'active' ? '运营中' : '暂停运营'}</span></p>
            </div>
            <div class="detail-section">
              <h3>基地介绍</h3>
              <p>${shelter.description}</p>
            </div>
            ${qrCodeUrl ? `
            <div class="detail-section">
              <h3>捐款渠道</h3>
              <div class="qr-code-container">
                <img src="${qrCodeUrl}" alt="收款码" style="max-width: 200px; max-height: 200px; margin: 0 auto; display: block;">
                <p style="text-align: center; margin-top: 10px; color: #666;">扫码捐款支持基地运营，也可以寄送实物，感谢您的支持!</p>
              </div>
            </div>
            ` : ''}
            <div class="detail-section" id="donations-statistics">
              <h3>💰 捐赠与使用情况</h3>
              <div class="loading-donations">正在加载捐赠统计数据...</div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">关闭</button>
            <button class="btn btn-primary" onclick="document.querySelector('.contact-modal-trigger').click(); this.closest('.modal-overlay').remove()">联系基地</button>
          </div>
        </div>
      `
          
      // 添加联系基地的隐藏触发按钮
      const contactTrigger = document.createElement('button')
      contactTrigger.className = 'contact-modal-trigger'
      contactTrigger.style.display = 'none'
      contactTrigger.onclick = () => this.showContactModal(shelter)
      modal.appendChild(contactTrigger)
          
      document.body.appendChild(modal)
          
      // 添加样式
      this.addModalStyles()
          
      // 获取捐赠统计数据
      this.loadDonationsStatistics(shelter.id)
    },
        
    async loadDonationsStatistics(shelterId) {
      try {
        const response = await shelterApi.getShelterDonationsStatistics(shelterId)
        console.log('获取捐赠统计响应:', response)
            
        if (response.code === 200 && response.data) {
          const stats = response.data
          const donationsStatDiv = document.getElementById('donations-statistics')
              
          if (donationsStatDiv) {
            const usageTypeMap = {
              'food': '食物采购',
              'medical': '医疗费用',
              'facility': '设施建设',
              'staff': '人员工资',
              'other': '其他用途'
            }
                
            let recentUsagesHtml = ''
            if (stats.recent_usages && stats.recent_usages.length > 0) {
              recentUsagesHtml = `
                <div style="margin-top: 20px;">
                  <h4 style="color: #ff6b6b; margin-bottom: 10px;">最近使用记录</h4>
                  <div style="max-height: 300px; overflow-y: auto;">
                    ${stats.recent_usages.map(usage => `
                      <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                          <span style="font-weight: bold; color: #333;">${usage.purpose}</span>
                          <span style="color: #ff6b6b; font-weight: bold;">¥${parseFloat(usage.amount).toFixed(2)}</span>
                        </div>
                        <div style="margin-top: 5px; font-size: 0.85rem; color: #666;">
                          <span>类型：${usageTypeMap[usage.usage_type] || usage.usage_type}</span>
                          <span style="margin-left: 10px;">日期：${new Date(usage.usage_date).toLocaleDateString()}</span>
                        </div>
                        ${usage.description ? `<div style="margin-top: 5px; font-size: 0.85rem; color: #888;">${usage.description}</div>` : ''}
                      </div>
                    `).join('')}
                  </div>
                </div>
              `
            } else {
              recentUsagesHtml = '<p style="text-align: center; color: #999; margin-top: 15px;">暂无使用记录</p>'
            }
                
            donationsStatDiv.innerHTML = `
              <h3>💰 捐赠与使用情况</h3>
              <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px;">
                <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 20px; border-radius: 10px; text-align: center;">
                  <div style="font-size: 1.5rem; font-weight: bold; color: #1976d2; margin-bottom: 5px;">¥${stats.total_donations_amount.toFixed(2)}</div>
                  <div style="font-size: 0.9rem; color: #666;">捐赠总额</div>
                  <div style="font-size: 0.8rem; color: #999; margin-top: 3px;">共 ${stats.total_donations_count} 笔</div>
                </div>
                <div style="background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%); padding: 20px; border-radius: 10px; text-align: center;">
                  <div style="font-size: 1.5rem; font-weight: bold; color: #c62828; margin-bottom: 5px;">¥${stats.total_used_amount.toFixed(2)}</div>
                  <div style="font-size: 0.9rem; color: #666;">已使用</div>
                  <div style="font-size: 0.8rem; color: #999; margin-top: 3px;">共 ${stats.total_usages_count} 笔</div>
                </div>
                <div style="background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%); padding: 20px; border-radius: 10px; text-align: center;">
                  <div style="font-size: 1.5rem; font-weight: bold; color: #2e7d32; margin-bottom: 5px;">¥${stats.remaining_amount.toFixed(2)}</div>
                  <div style="font-size: 0.9rem; color: #666;">剩余金额</div>
                  <div style="font-size: 0.8rem; color: #999; margin-top: 3px;">可用余额</div>
                </div>
              </div>
              ${recentUsagesHtml}
            `
          }
        }
      } catch (error) {
        console.error('加载捐赠统计数据失败:', error)
        const donationsStatDiv = document.getElementById('donations-statistics')
        if (donationsStatDiv) {
          donationsStatDiv.innerHTML = `
            <h3>💰 捐赠与使用情况</h3>
            <p style="text-align: center; color: #999; padding: 20px;">加载捐赠统计数据失败</p>
          `
        }
      }
    },
    
    showContactModal(shelter) {
      // 创建联系模态框
      const modal = document.createElement('div')
      modal.className = 'modal-overlay'
      modal.innerHTML = `
        <div class="modal-content contact-modal">
          <div class="modal-header">
            <h2>联系 ${shelter.name}</h2>
            <button class="close-btn" onclick="this.closest('.modal-overlay').remove()">×</button>
          </div>
          <div class="modal-body">
            <div class="contact-info">
              <div class="contact-item">
                <i class="icon">📞</i>
                <div>
                  <strong>电话联系</strong>
                  <p>${shelter.contact_phone}</p>
                </div>
              </div>
              <div class="contact-item">
                <i class="icon">✉️</i>
                <div>
                  <strong>邮件联系</strong>
                  <p>${shelter.email}</p>
                </div>
              </div>
              ${shelter.website ? `
              <div class="contact-item">
                <i class="icon">🌐</i>
                <div>
                  <strong>官方网站</strong>
                  <p><a href="${shelter.website}" target="_blank">${shelter.website}</a></p>
                </div>
              </div>
              ` : ''}
            </div>
            <div class="quick-actions">
              <h3>快捷操作</h3>
              <div class="action-buttons">
                <button class="btn btn-primary" onclick="window.location.href='tel:${shelter.contact_phone.replace(/[^0-9]/g, '')}'">
                  直接拨打电话
                </button>
                <button class="btn btn-secondary" onclick="window.location.href='mailto:${shelter.email}'">
                  发送邮件
                </button>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">关闭</button>
          </div>
        </div>
      `
      
      document.body.appendChild(modal)
      
      // 添加样式
      this.addModalStyles()
    },
    
    addModalStyles() {
      // 检查是否已经添加过样式
      if (document.getElementById('shelter-modal-styles')) return
      
      const style = document.createElement('style')
      style.id = 'shelter-modal-styles'
      style.textContent = `
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 1000;
          animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        
        .modal-content {
          background: white;
          border-radius: 15px;
          width: 90%;
          max-width: 600px;
          max-height: 80vh;
          overflow-y: auto;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
          animation: slideUp 0.3s ease;
        }
        
        .contact-modal {
          max-width: 500px;
        }
        
        @keyframes slideUp {
          from { 
            opacity: 0;
            transform: translateY(30px);
          }
          to { 
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .modal-header {
          padding: 20px;
          border-bottom: 1px solid #eee;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        
        .modal-header h2 {
          margin: 0;
          color: #333;
        }
        
        .close-btn {
          background: none;
          border: none;
          font-size: 24px;
          cursor: pointer;
          color: #999;
          padding: 5px;
          border-radius: 50%;
          width: 30px;
          height: 30px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .close-btn:hover {
          background: #f5f5f5;
          color: #333;
        }
        
        .modal-body {
          padding: 20px;
        }
        
        .detail-section {
          margin-bottom: 25px;
        }
        
        .detail-section h3 {
          color: #ff6b6b;
          margin-bottom: 15px;
          padding-bottom: 8px;
          border-bottom: 2px solid #ff6b6b;
        }
        
        .loading-donations {
          text-align: center;
          padding: 30px;
          color: #999;
          font-style: italic;
        }
        
        .detail-section p {
          margin: 10px 0;
          line-height: 1.6;
        }
        
        .status {
          padding: 3px 10px;
          border-radius: 15px;
          color: white;
          font-size: 12px;
          font-weight: bold;
        }
        
        .status.active {
          background: #28a745;
        }
        
        .status.inactive {
          background: #dc3545;
        }
        
        .contact-info {
          margin-bottom: 25px;
        }
        
        .contact-item {
          display: flex;
          align-items: center;
          gap: 15px;
          padding: 15px;
          background: #f8f9fa;
          border-radius: 10px;
          margin-bottom: 15px;
        }
        
        .contact-item .icon {
          font-size: 24px;
        }
        
        .contact-item strong {
          display: block;
          color: #333;
          margin-bottom: 5px;
        }
        
        .contact-item p {
          margin: 0;
          color: #666;
        }
        
        .contact-item a {
          color: #ff6b6b;
          text-decoration: none;
        }
        
        .contact-item a:hover {
          text-decoration: underline;
        }
        
        .quick-actions {
          text-align: center;
        }
        
        .quick-actions h3 {
          color: #ff6b6b;
          margin-bottom: 20px;
        }
        
        .action-buttons {
          display: flex;
          gap: 15px;
          justify-content: center;
          flex-wrap: wrap;
        }
        
        .modal-footer {
          padding: 20px;
          border-top: 1px solid #eee;
          display: flex;
          justify-content: flex-end;
          gap: 10px;
        }
        
        .btn {
          padding: 10px 20px;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 600;
          transition: all 0.3s ease;
        }
        
        .btn-primary {
          background: linear-gradient(135deg, #ff9a3d 0%, #ff6b6b 100%);
          color: white;
        }
        
        .btn-primary:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(255, 107, 107, 0.4);
        }
        
        .btn-secondary {
          background: #6c757d;
          color: white;
        }
        
        .btn-secondary:hover {
          background: #5a6268;
          transform: translateY(-2px);
        }
        
        @media (max-width: 768px) {
          .modal-content {
            width: 95%;
            margin: 10px;
          }
          
          .action-buttons {
            flex-direction: column;
          }
          
          .contact-item {
            flex-direction: column;
            text-align: center;
          }
        }
      `
      
      document.head.appendChild(style)
    },
    
    truncateDescription(description) {
      if (description.length <= 60) return description
      return description.substring(0, 60) + '...'
    },
    
    handleImageError(event) {
      event.target.src = 'https://via.placeholder.com/300x200?text=图片加载失败'
    },
    
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--
        this.loadShelters()
      }
    },
    
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++
        this.loadShelters()
      }
    }
  }
}
</script>

<style scoped>
.shelters-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #fff8f0 0%, #ffeaa7 100%);
}

.page-header {
  background: linear-gradient(135deg, #ff9a3d 0%, #ff6b6b 100%);
  color: white;
  padding: 60px 0;
  text-align: center;
  box-shadow: 0 4px 20px rgba(255, 154, 61, 0.4);
}

.page-header h1 {
  font-size: 2.5rem;
  margin-bottom: 15px;
  font-weight: 700;
}

.page-header p {
  font-size: 1.2rem;
  opacity: 0.9;
  max-width: 600px;
  margin: 0 auto;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.search-section {
  background: white;
  padding: 30px 0;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.search-bar {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.search-input {
  flex: 1;
  padding: 12px 20px;
  border: 2px solid #e1e5e9;
  border-radius: 30px;
  font-size: 16px;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #ff9a3d;
  box-shadow: 0 0 0 3px rgba(255, 154, 61, 0.3);
  transform: scale(1.02);
}

.search-btn {
  background: linear-gradient(135deg, #ff9a3d 0%, #ff6b6b 100%);
  color: white;
  border: none;
  padding: 12px 25px;
  border-radius: 30px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 15px rgba(255, 154, 61, 0.3);
}

.search-btn:hover {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff9a3d 100%);
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
}

.filters {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.filter-select {
  padding: 10px 15px;
  border: 2px solid #e1e5e9;
  border-radius: 25px;
  background: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-select:focus {
  outline: none;
  border-color: #ff9a3d;
  box-shadow: 0 0 0 2px rgba(255, 154, 61, 0.2);
}

.shelters-list {
  padding: 50px 0;
}

.loading {
  text-align: center;
  padding: 50px;
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

.no-results {
  text-align: center;
  padding: 50px;
}

.empty-icon {
  font-size: 4rem;
  opacity: 0.3;
  display: block;
  margin-bottom: 20px;
}

.shelters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 30px;
  margin-bottom: 40px;
}

.shelter-card {
  background: white;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 5px 20px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
  cursor: pointer;
}

.shelter-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 15px 30px rgba(0,0,0,0.15);
}

.shelter-image {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.shelter-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.shelter-card:hover .shelter-image img {
  transform: scale(1.05);
}

.shelter-status {
  position: absolute;
  top: 15px;
  right: 15px;
  padding: 5px 15px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  color: white;
}

.shelter-status.active {
  background: #28a745;
}

.shelter-status.inactive {
  background: #dc3545;
}

.shelter-info {
  padding: 25px;
}

.shelter-name {
  font-size: 1.4rem;
  font-weight: 700;
  margin: 0 0 15px 0;
  color: #333;
}

.shelter-address {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  margin: 0 0 20px 0;
  font-size: 0.9rem;
}

.icon {
  font-size: 1.1rem;
}

.shelter-stats {
  display: flex;
  gap: 20px;
  margin: 20px 0;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 10px;
}

.stat-item {
  text-align: center;
  flex: 1;
}

.stat-number {
  display: block;
  font-size: 1.3rem;
  font-weight: 700;
  color: #ff6b6b;
  background: linear-gradient(135deg, #ff6b6b 0%, #ff9a3d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 0.8rem;
  color: #666;
  margin-top: 5px;
}

.shelter-description {
  color: #555;
  line-height: 1.6;
  margin: 20px 0;
  font-size: 0.95rem;
}

/* 活动相关样式 */
.shelter-activities {
  margin: 20px 0;
  padding: 15px;
  background: linear-gradient(135deg, #fff8f0 0%, #fff5e6 100%);
  border-radius: 10px;
  border: 1px solid rgba(255, 154, 61, 0.2);
}

.shelter-activities.empty {
  text-align: center;
  color: #999;
  font-style: italic;
  padding: 20px;
}

.activities-title {
  margin: 0 0 15px 0;
  font-size: 1.1rem;
  color: #ff6b6b;
  font-weight: 600;
}

.activities-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.activity-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: white;
  border-radius: 8px;
  border: 1px solid rgba(255, 154, 61, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.activity-item:hover {
  background: linear-gradient(135deg, #fff5e6 0%, #ffffff 100%);
  transform: translateX(5px);
  border-color: rgba(255, 154, 61, 0.3);
}

.activity-name {
  font-size: 0.95rem;
  color: #333;
  font-weight: 500;
}

.activity-type {
  font-size: 0.8rem;
  padding: 4px 10px;
  border-radius: 15px;
  font-weight: 600;
}

.activity-type.adoption {
  background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
  color: #c62828;
}

.activity-type.volunteer {
  background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
  color: #2e7d32;
}

.activity-type.fundraising {
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
  color: #ef6c00;
}

.activity-type.education {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  color: #1565c0;
}

.activity-type.other {
  background: linear-gradient(135deg, #f5f5f5 0%, #eeeeee 100%);
  color: #616161;
}

.more-activities {
  text-align: center;
  font-size: 0.85rem;
  color: #ff9a3d;
  padding: 5px;
  font-style: italic;
}

/* 活动申请模态框样式 */
.activity-modal .activity-info {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.activity-modal .activity-info h3 {
  margin: 0 0 10px 0;
  color: #ff6b6b;
}

.activity-type-tag {
  display: inline-block;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 15px;
}

.application-form {
  background: #fafafa;
  padding: 20px;
  border-radius: 10px;
}

.application-form h4 {
  margin: 0 0 15px 0;
  color: #333;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #555;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 0.95rem;
}

.form-control:focus {
  outline: none;
  border-color: #ff9a3d;
  box-shadow: 0 0 0 2px rgba(255, 154, 61, 0.2);
}

.shelter-contact {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 20px 0;
  font-size: 0.9rem;
  color: #666;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.shelter-actions {
  display: flex;
  gap: 10px;
  margin-top: 25px;
}

.btn {
  flex: 1;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.btn-primary {
  background: linear-gradient(135deg, #ff9a3d 0%, #ff6b6b 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(255, 154, 61, 0.3);
}

.btn-primary:hover {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff9a3d 100%);
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
  transform: translateY(-2px);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 30px;
}

.page-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, #ff9a3d 0%, #ff6b6b 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 10px rgba(255, 154, 61, 0.3);
}

.page-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff9a3d 100%);
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(255, 107, 107, 0.4);
}

.page-btn:disabled {
  background: linear-gradient(135deg, #cccccc 0%, #e0e0e0 100%);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.page-info {
  font-size: 0.9rem;
  color: #666;
}

@media (max-width: 768px) {
  .shelters-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .search-bar {
    flex-direction: column;
  }
  
  .filters {
    flex-direction: column;
    align-items: center;
  }
  
  .shelter-stats {
    flex-direction: column;
    gap: 10px;
  }
  
  .shelter-actions {
    flex-direction: column;
  }
  
  .pagination {
    flex-direction: column;
    gap: 15px;
  }
}
</style>