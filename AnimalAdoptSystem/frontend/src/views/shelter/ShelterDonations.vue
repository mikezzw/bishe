<template>
  <div class="shelter-donations">
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
        <router-link to="/shelter/volunteers" class="nav-item">
          <i class="nav-icon">🤝</i>
          <span>志愿者管理</span>
        </router-link>
        <router-link to="/shelter/donations" class="nav-item active">
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
        <h1>捐赠管理</h1>
        <div class="header-actions">
          <button class="btn btn-primary" @click="exportDonations">
            <i class="btn-icon">📤</i>
            导出记录
          </button>
          <button class="btn btn-primary" @click="openImportModal">
            <i class="btn-icon">📥</i>
            导入捐赠
          </button>
          <button class="btn btn-secondary" @click="refreshDonations">
            <i class="btn-icon">🔄</i>
            刷新
          </button>
        </div>
      </div>
      
      <!-- 捐赠统计 -->
      <div class="donation-stats">
        <div class="stat-card">
          <div class="stat-icon">💰</div>
          <div class="stat-content">
            <h3>总捐赠金额</h3>
            <p class="stat-value">¥{{ (typeof totalDonationAmount === 'number' && !isNaN(totalDonationAmount)) ? totalDonationAmount.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '0.00' }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📋</div>
          <div class="stat-content">
            <h3>总捐赠次数</h3>
            <p class="stat-value">{{ totalDonationCount }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-content">
            <h3>捐赠人数</h3>
            <p class="stat-value">{{ totalDonors }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📈</div>
          <div class="stat-content">
            <h3>本月捐赠</h3>
            <p class="stat-value">¥{{ monthlyDonationAmount.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</p>
          </div>
        </div>
      </div>
      
      <!-- 搜索和筛选 -->
      <div class="search-filter">
        <div class="search-box">
          <input type="text" placeholder="搜索捐赠人姓名或联系方式..." v-model="searchQuery" @input="searchDonations">
          <button class="btn btn-secondary">搜索</button>
        </div>
        <div class="filter-box">
          <select v-model="filterStatus" @change="filterDonations">
            <option value="">所有状态</option>
            <option value="pending">待处理</option>
            <option value="completed">已完成</option>
          </select>
          <select v-model="filterType" @change="filterDonations">
            <option value="">所有类型</option>
            <option value="money">资金</option>
            <option value="goods">物资</option>
          </select>
        </div>
      </div>
      
      <!-- 捐赠使用情况 -->
      <div class="donation-usage-section" style="margin-bottom: 40px;">
        <div class="section-header">
          <h2>捐赠使用情况</h2>
          <button class="btn btn-primary" @click="openAddUsageModal">
            <i class="btn-icon">➕</i>
            添加使用记录
          </button>
        </div>
        
        <!-- 使用情况统计 -->
        <div class="usage-stats">
          <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-content">
            <h3>总使用金额</h3>
            <p class="stat-value">¥{{ (typeof totalUsageAmount === 'number' && !isNaN(totalUsageAmount)) ? totalUsageAmount.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '0.00' }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">💰</div>
          <div class="stat-content">
            <h3>剩余金额</h3>
            <p class="stat-value">¥{{ (typeof remainingAmount === 'number' && !isNaN(remainingAmount)) ? remainingAmount.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '0.00' }}</p>
          </div>
          </div>
        </div>
        
        <!-- 使用情况列表 -->
        <div class="usage-list">
          <div class="usage-card" v-for="usage in donationUsages" :key="usage.id">
            <div class="usage-header">
              <h3>{{ usage.purpose }}</h3>
              <div class="usage-amount">¥{{ (typeof usage.amount === 'number' && !isNaN(usage.amount)) ? usage.amount.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '0.00' }}</div>
            </div>
            <div class="usage-info">
              <div class="usage-meta">
                <span class="meta-item">📅 {{ formatDate(usage.usage_date) }}</span>
                <span class="meta-item">👤 {{ usage.approver || '系统' }}</span>
              </div>
              <div class="usage-description">
                <h4>使用说明</h4>
                <p>{{ usage.description || '无' }}</p>
              </div>
              <div class="usage-attachments" v-if="usage.attachments && usage.attachments.length > 0">
                <h4>相关凭证</h4>
                <div class="attachments-list">
                  <a href="#" v-for="(attachment, index) in usage.attachments" :key="index" class="attachment-item">
                    📎 {{ attachment }}
                  </a>
                </div>
              </div>
            </div>
            <div class="usage-actions">
              <button class="btn btn-sm btn-primary" @click="openEditUsageModal(usage)">
                编辑
              </button>
              <button class="btn btn-sm btn-danger" @click="deleteUsageRecord(usage.id)">
                删除
              </button>
            </div>
          </div>
          <div class="empty-state" v-if="donationUsages.length === 0">
            <p>暂无捐赠使用记录</p>
          </div>
        </div>
      </div>
      
      <!-- 捐赠列表 -->
      <div class="donations-list">
        <div class="donation-card" v-for="donation in filteredDonations" :key="donation.id">
          <div class="donation-header">
            <h3>{{ donation.donor_name || (donation.donor ? donation.donor.username : '未知捐赠人') }}</h3>
            <div class="donation-amount">¥{{ (parseFloat(donation.amount) || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</div>
          </div>
          <div class="donation-info">
            <div class="donation-meta">
              <span class="meta-item">📞 {{ donation.donor ? donation.donor.phone || '无' : '无' }}</span>
              <span class="meta-item">📧 {{ donation.donor ? donation.donor.email || '无' : '无' }}</span>
              <span class="meta-item">📅 {{ formatDate(donation.created_at) }}</span>
              <span class="meta-item">🎯 {{ getTypeText(donation.donation_type) }}</span>
              <span class="meta-item">📦 {{ getStatusText(donation.status) }}</span>
            </div>
            <div class="donation-description">
              <h4>捐赠说明</h4>
              <p>{{ donation.goods_description || donation.service_description || '无' }}</p>
            </div>
            <div class="donation-remarks">
              <h4>备注</h4>
              <p>无</p>
            </div>
          </div>
          <div class="donation-actions">
            <button class="btn btn-sm btn-primary" @click="openEditModal(donation)">
              编辑
            </button>
            <button class="btn btn-sm btn-success" v-if="donation.status === 'pending'" @click="markAsCompleted(donation.id)">
              标记为已完成
            </button>
            <button class="btn btn-sm btn-danger" @click="deleteDonation(donation.id)">
              删除
            </button>
          </div>
        </div>
        <div class="empty-state" v-if="filteredDonations.length === 0">
          <p>暂无捐赠记录</p>
        </div>
      </div>
      
      <!-- 编辑捐赠模态框 -->
      <div class="modal" v-if="showEditModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>编辑捐赠记录</h2>
            <button class="btn-close" @click="showEditModal = false">×</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateDonation">
              <div class="form-group">
                <label for="donor_name">捐赠人姓名</label>
                <input type="text" id="donor_name" v-model="editDonation.donor_name" required>
              </div>
              <div class="form-group">
                <label for="donor_phone">联系电话</label>
                <input type="tel" id="donor_phone" v-model="editDonation.donor_phone" required>
              </div>
              <div class="form-group">
                <label for="donor_email">电子邮箱</label>
                <input type="email" id="donor_email" v-model="editDonation.donor_email">
              </div>
              <div class="form-group">
                <label for="amount">捐赠金额</label>
                <input type="number" id="amount" v-model="editDonation.amount" step="0.01" min="0" required>
              </div>
              <div class="form-group">
                <label for="donation_type">捐赠类型</label>
                <select id="donation_type" v-model="editDonation.donation_type" required>
                  <option value="money">资金</option>
                  <option value="goods">物资</option>
                </select>
              </div>
              <div class="form-group">
                <label for="donation_date">捐赠日期</label>
                <input type="date" id="donation_date" v-model="editDonation.donation_date" required>
              </div>
              <div class="form-group">
                <label for="status">状态</label>
                <select id="status" v-model="editDonation.status" required>
                  <option value="pending">待处理</option>
                  <option value="completed">已完成</option>
                </select>
              </div>
              <div class="form-group">
                <label for="description">捐赠说明</label>
                <textarea id="description" v-model="editDonation.description" rows="3"></textarea>
              </div>
              <div class="form-group">
                <label for="remarks">备注</label>
                <textarea id="remarks" v-model="editDonation.remarks" rows="3"></textarea>
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
      
      <!-- 添加捐赠使用记录模态框 -->
      <div class="modal" v-if="showAddUsageModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>添加捐赠使用记录</h2>
            <button class="btn-close" @click="showAddUsageModal = false">×</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="addUsageRecord">
              <div class="form-group">
                <label for="usage_donation">选择捐赠记录</label>
                <select id="usage_donation" v-model="newUsage.donation" required>
                  <option value="">请选择捐赠记录</option>
                  <option v-for="donation in donations" :key="donation.id" :value="donation.id">
                    {{ donation.donor_name || (donation.donor ? donation.donor.username : '未知捐赠人') }} - ¥{{ (parseFloat(donation.amount) || 0).toFixed(2) }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label for="usage_purpose">使用用途</label>
                <input type="text" id="usage_purpose" v-model="newUsage.purpose" required>
              </div>
              <div class="form-group">
                <label for="usage_amount">使用金额</label>
                <input type="number" id="usage_amount" v-model="newUsage.amount" step="0.01" min="0" required>
              </div>
              <div class="form-group">
                <label for="usage_date">使用日期</label>
                <input type="date" id="usage_date" v-model="newUsage.usage_date" required>
              </div>
              <div class="form-group">
                <label for="usage_description">使用说明</label>
                <textarea id="usage_description" v-model="newUsage.description" rows="3"></textarea>
              </div>
              <div class="form-group">
                <label>相关凭证</label>
                <div class="file-upload-area">
                  <div class="file-preview-container" v-if="newUsage.attachments && newUsage.attachments.length > 0">
                    <div class="file-preview" v-for="(file, index) in newUsage.attachments" :key="index">
                      <div class="file-info">
                        <span class="file-icon">📄</span>
                        <span class="file-name">{{ file.name }}</span>
                        <span class="file-size">({{ formatFileSize(file.size) }})</span>
                      </div>
                      <button type="button" class="remove-file-btn" @click="removeFile(index)">×</button>
                    </div>
                  </div>
                  <div class="upload-placeholder" @click="$refs.fileInput.click()">
                    <div class="upload-icon">📁</div>
                    <p>点击上传文件</p>
                    <p class="upload-hint">支持 PDF、Excel、Word 等格式，最多可上传5个文件</p>
                  </div>
                  <input 
                    type="file" 
                    ref="fileInput" 
                    accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png" 
                    multiple 
                    @change="handleFileUpload" 
                    style="display: none"
                  >
                </div>
              </div>
              <div class="form-actions">
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  {{ loading ? '添加中...' : '添加' }}
                </button>
                <button type="button" class="btn btn-secondary" @click="showAddUsageModal = false">取消</button>
              </div>
            </form>
          </div>
        </div>
      </div>
      
      <!-- 编辑捐赠使用记录模态框 -->
      <div class="modal" v-if="showEditUsageModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>编辑捐赠使用记录</h2>
            <button class="btn-close" @click="showEditUsageModal = false">×</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateUsageRecord">
              <div class="form-group">
                <label for="edit_usage_purpose">使用用途</label>
                <input type="text" id="edit_usage_purpose" v-model="editUsage.purpose" required>
              </div>
              <div class="form-group">
                <label for="edit_usage_amount">使用金额</label>
                <input type="number" id="edit_usage_amount" v-model="editUsage.amount" step="0.01" min="0" required>
              </div>
              <div class="form-group">
                <label for="edit_usage_date">使用日期</label>
                <input type="date" id="edit_usage_date" v-model="editUsage.usage_date" required>
              </div>
              <div class="form-group">
                <label for="edit_usage_description">使用说明</label>
                <textarea id="edit_usage_description" v-model="editUsage.description" rows="3"></textarea>
              </div>
              <div class="form-group">
                <label>相关凭证</label>
                <div class="file-upload-area">
                  <div class="file-preview-container" v-if="editUsage.attachments && editUsage.attachments.length > 0">
                    <div class="file-preview" v-for="(file, index) in editUsage.attachments" :key="index">
                      <div class="file-info">
                        <span class="file-icon">📄</span>
                        <span class="file-name">{{ file.name }}</span>
                        <span class="file-size">({{ formatFileSize(file.size) }})</span>
                      </div>
                      <button type="button" class="remove-file-btn" @click="removeEditFile(index)">×</button>
                    </div>
                  </div>
                  <div class="upload-placeholder" @click="$refs.editFileInput.click()" v-if="!editUsage.attachments || editUsage.attachments.length < 5">
                    <div class="upload-icon">📁</div>
                    <p>点击上传更多文件</p>
                    <p class="upload-hint">支持 PDF、Excel、Word 等格式，最多可上传5个文件</p>
                  </div>
                  <input 
                    type="file" 
                    ref="editFileInput" 
                    accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png" 
                    multiple 
                    @change="handleEditFileUpload" 
                    style="display: none"
                  >
                </div>
              </div>
              <div class="form-actions">
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  {{ loading ? '更新中...' : '更新' }}
                </button>
                <button type="button" class="btn btn-secondary" @click="showEditUsageModal = false">取消</button>
              </div>
            </form>
          </div>
        </div>
      </div>
      
      <!-- 导入捐赠模态框 -->
      <div class="modal" v-if="showImportModal">
        <div class="modal-content" style="max-width: 800px;">
          <div class="modal-header">
            <h2>导入捐赠信息</h2>
            <button class="btn-close" @click="showImportModal = false">×</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="importDonations">
              <div class="form-group">
                <label>导入方式</label>
                <div class="import-methods">
                  <label class="method-option">
                    <input type="radio" v-model="importMethod" value="manual" checked>
                    <span>手动输入</span>
                  </label>
                  <label class="method-option">
                    <input type="radio" v-model="importMethod" value="csv">
                    <span>CSV文件上传</span>
                  </label>
                </div>
              </div>
              
              <!-- 手动输入方式 -->
              <div v-if="importMethod === 'manual'">
                <div class="form-group">
                  <label>捐赠人</label>
                  <input type="text" v-model="manualDonation.donor_name" placeholder="请输入捐赠人姓名" required>
                </div>
                <div class="form-group">
                  <label>捐赠金额</label>
                  <input type="number" v-model="manualDonation.amount" step="0.01" min="0.01" placeholder="请输入捐赠金额" required>
                </div>
              </div>
              
              <!-- CSV文件上传方式 -->
              <div v-else-if="importMethod === 'csv'">
                <div class="form-group">
                  <label>上传CSV文件</label>
                  <div class="file-upload-area">
                    <div class="file-preview-container" v-if="importFile">
                      <div class="file-preview">
                        <div class="file-info">
                          <span class="file-icon">📄</span>
                          <span class="file-name">{{ importFile.name }}</span>
                          <span class="file-size">({{ formatFileSize(importFile.size) }})</span>
                        </div>
                        <button type="button" class="remove-file-btn" @click="removeImportFile">×</button>
                      </div>
                    </div>
                    <div class="upload-placeholder" @click="$refs.importFileInput.click()" v-if="!importFile">
                      <div class="upload-icon">📁</div>
                      <p>点击上传CSV文件</p>
                      <p class="upload-hint">文件格式：捐赠人,捐赠金额</p>
                    </div>
                    <input 
                      type="file" 
                      ref="importFileInput" 
                      accept=".csv" 
                      @change="handleImportFile" 
                      style="display: none"
                    >
                  </div>
                </div>
                
                <div class="form-group" v-if="importData.length > 0">
                  <label>预览数据</label>
                  <div class="import-preview">
                    <table class="preview-table">
                      <thead>
                        <tr>
                          <th>捐赠人</th>
                          <th>捐赠金额</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(item, index) in importData" :key="index">
                          <td>{{ item.donor_name }}</td>
                          <td>{{ item.amount }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
              
              <div class="form-actions">
                <button type="submit" class="btn btn-primary" :disabled="loading || !canImport">
                  {{ loading ? '导入中...' : '导入' }}
                </button>
                <button type="button" class="btn btn-secondary" @click="showImportModal = false">取消</button>
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
export default {
  name: 'ShelterDonations',
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user')) || {},
      donations: [],
      donationUsages: [],
      searchQuery: '',
      filterStatus: '',
      filterType: '',
      showEditModal: false,
      showAddUsageModal: false,
      showEditUsageModal: false,
      editDonation: {
        id: '',
        donor_name: '',
        donor_phone: '',
        donor_email: '',
        amount: '',
        donation_type: 'money',
        donation_date: '',
        status: 'pending',
        description: '',
        remarks: ''
      },
      newUsage: {
        donation: '',
        purpose: '',
        amount: '',
        usage_date: '',
        description: '',
        attachmentsInput: '',
        attachments: []
      },
      editUsage: {
        id: '',
        purpose: '',
        amount: '',
        usage_date: '',
        description: '',
        attachmentsInput: '',
        attachments: []
      },
      loading: false,
      error: '',
      success: '',
      showImportModal: false,
      importMethod: 'manual',
      importFile: null,
      importData: [],
      manualDonation: {
        donor_name: '',
        amount: ''
      }
    }
  },
  computed: {
    filteredDonations() {
      let result = [...this.donations]
      
      // 搜索
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        result = result.filter(donation => {
          const donorName = (donation.donor_name || (donation.donor ? donation.donor.username : '')).toLowerCase()
          const donorPhone = donation.donor ? donation.donor.phone || '' : ''
          const donorEmail = donation.donor ? donation.donor.email.toLowerCase() : ''
          return donorName.includes(query) || donorPhone.includes(query) || donorEmail.includes(query)
        })
      }
      
      // 状态筛选
      if (this.filterStatus) {
        result = result.filter(donation => donation.status === this.filterStatus)
      }
      
      // 类型筛选
      if (this.filterType) {
        result = result.filter(donation => donation.donation_type === this.filterType)
      }
      
      return result
    },
    totalDonationAmount() {
      return this.donations.reduce((total, donation) => {
        const amount = parseFloat(donation.amount) || 0
        return total + amount
      }, 0)
    },
    totalDonationCount() {
      return this.donations.length
    },
    totalDonors() {
      const donors = new Set(this.donations.map(donation => donation.donor_name || (donation.donor ? donation.donor.username : '未知')))
      return donors.size
    },
    monthlyDonationAmount() {
      const now = new Date()
      const currentMonth = now.getMonth() + 1
      const currentYear = now.getFullYear()
      
      return this.donations.reduce((total, donation) => {
        const donationDate = new Date(donation.donation_date)
        if (donationDate.getMonth() + 1 === currentMonth && donationDate.getFullYear() === currentYear) {
          return total + (parseFloat(donation.amount) || 0)
        }
        return total
      }, 0)
    },
    totalUsageAmount() {
      return this.donationUsages.reduce((total, usage) => {
        const amount = parseFloat(usage.amount) || 0
        return total + amount
      }, 0)
    },
    remainingAmount() {
      const totalDonations = this.donations.reduce((total, donation) => {
        const amount = parseFloat(donation.amount) || 0
        return total + amount
      }, 0)
      const totalUsage = this.totalUsageAmount
      return totalDonations - totalUsage
    },
    canImport() {
      if (this.importMethod === 'manual') {
        return this.manualDonation.donor_name && this.manualDonation.amount && this.manualDonation.amount > 0
      } else if (this.importMethod === 'csv') {
        return this.importData.length > 0
      }
      return false
    }
  },
  mounted() {
    // 检查用户是否已登录且为基地管理员或系统管理员
    if (!this.user || (this.user.user_type !== 'shelter' && this.user.user_type !== 'admin')) {
      this.$router.push('/login')
      return
    }
    
    // 加载捐赠数据
    this.loadDonations()
  },
  methods: {
    async loadDonations() {
      this.loading = true
      this.error = ''
      
      try {
        console.log('用户信息:', this.user)
        console.log('用户信息完整结构:', JSON.parse(JSON.stringify(this.user)))
        
        // 获取用户关联的基地ID
        let shelterId = null
        if (this.user.shelter) {
          console.log('用户信息中的shelter字段:', this.user.shelter)
          if (typeof this.user.shelter === 'object' && this.user.shelter.id) {
            shelterId = this.user.shelter.id
            console.log('从用户信息中获取基地ID:', shelterId)
          } else if (typeof this.user.shelter === 'number') {
            // 如果shelter直接是ID数字
            shelterId = this.user.shelter
            console.log('从用户信息中获取基地ID（直接数字）:', shelterId)
          }
        } else if (this.user.shelter_id) {
          // 可能字段名是shelter_id
          shelterId = this.user.shelter_id
          console.log('从用户信息中获取基地ID（shelter_id字段）:', shelterId)
        } else if (this.user.user_type === 'admin') {
          // 管理员可以查看所有捐赠
          console.log('管理员尝试获取基地列表')
          const response = await this.$axios.get('/shelters/')
          console.log('基地列表响应:', response)
          
          // 处理不同的响应格式
          let shelters = []
          if (response.code === 200) {
            if (response.data && response.data.results) {
              shelters = response.data.results
            } else if (Array.isArray(response.data)) {
              shelters = response.data
            }
          } else if (response.results) {
            // 处理默认的DRF响应格式
            shelters = response.results
          }
          
          if (shelters.length > 0) {
            shelterId = shelters[0].id
            console.log('从基地列表中获取基地ID:', shelterId)
          }
        }
        
        if (shelterId) {
          console.log('获取捐赠数据，基地ID:', shelterId)
          const response = await this.$axios.get(`/shelters/${shelterId}/donations/`)
          console.log('捐赠数据响应:', response)
          
          // 处理不同的响应格式
          if (response.code === 200) {
            if (response.data && response.data.results) {
              this.donations = response.data.results.map(donation => ({
                ...donation,
                amount: parseFloat(donation.amount) || 0
              }))
              console.log('处理后的捐赠数据:', this.donations)
            } else if (Array.isArray(response.data)) {
              this.donations = response.data.map(donation => ({
                ...donation,
                amount: parseFloat(donation.amount) || 0
              }))
              console.log('处理后的捐赠数据:', this.donations)
            } else {
              this.donations = []
            }
          } else if (response.results) {
            // 处理默认的DRF响应格式
            this.donations = response.results.map(donation => ({
              ...donation,
              amount: parseFloat(donation.amount) || 0
            }))
            console.log('处理后的捐赠数据:', this.donations)
          } else {
            this.donations = []
          }
          
          // 加载捐赠使用记录
          await this.loadDonationUsages(shelterId)
        } else {
          console.error('未找到关联的基地信息')
          this.error = '未找到关联的基地信息'
          this.donations = []
          this.donationUsages = []
        }
      } catch (error) {
        console.error('加载捐赠数据失败:', error)
        this.error = '加载捐赠数据失败，请检查网络连接'
        this.donations = []
        this.donationUsages = []
      } finally {
        this.loading = false
      }
    },
    
    async loadDonationUsages(shelterId) {
      try {
        console.log('获取捐赠使用记录，基地ID:', shelterId)
        const response = await this.$axios.get(`/shelters/${shelterId}/usages/`)
        console.log('捐赠使用记录响应:', response)
        
        // 处理不同的响应格式
          if (response.code === 200) {
            if (response.data && response.data.results) {
              this.donationUsages = response.data.results.map(usage => ({
                ...usage,
                amount: parseFloat(usage.amount) || 0
              }))
              console.log('处理后的捐赠使用记录:', this.donationUsages)
            } else if (Array.isArray(response.data)) {
              this.donationUsages = response.data.map(usage => ({
                ...usage,
                amount: parseFloat(usage.amount) || 0
              }))
              console.log('处理后的捐赠使用记录:', this.donationUsages)
            } else {
              this.donationUsages = []
            }
          } else if (response.results) {
            // 处理默认的DRF响应格式
            this.donationUsages = response.results.map(usage => ({
              ...usage,
              amount: parseFloat(usage.amount) || 0
            }))
            console.log('处理后的捐赠使用记录:', this.donationUsages)
          } else {
            this.donationUsages = []
          }
      } catch (error) {
        console.error('加载捐赠使用记录失败:', error)
        this.donationUsages = []
      }
    },
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.$router.push('/login')
    },
    getTypeText(type) {
      const typeMap = {
        'money': '资金',
        'goods': '物资'
      }
      return typeMap[type] || type
    },
    getStatusText(status) {
      const statusMap = {
        'pending': '待处理',
        'completed': '已完成'
      }
      return statusMap[status] || status
    },
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })
    },
    refreshDonations() {
      this.loadDonations()
    },
    exportDonations() {
      try {
        // 准备导出数据
        const exportData = this.filteredDonations.map(donation => ({
          '捐赠人姓名': donation.donor_name || (donation.donor ? donation.donor.username : '未知'),
          '联系电话': donation.donor ? donation.donor.phone || '' : '',
          '电子邮箱': donation.donor ? donation.donor.email || '' : '',
          '捐赠金额': `¥${(typeof donation.amount === 'number' && !isNaN(donation.amount)) ? donation.amount.toFixed(2) : '0.00'}`,

          '捐赠类型': this.getTypeText(donation.donation_type),
          '捐赠日期': this.formatDate(donation.created_at),
          '状态': this.getStatusText(donation.status),
          '捐赠说明': donation.goods_description || donation.service_description || '',
          '备注': '',
          '创建时间': this.formatDateTime(donation.created_at)
        }));
        
        // 如果没有数据，显示提示
        if (exportData.length === 0) {
          this.error = '没有可导出的数据';
          setTimeout(() => { this.error = ''; }, 3000);
          return;
        }
        
        // 生成CSV内容
        const csvContent = this.convertToCSV(exportData);
        
        // 创建下载链接
        const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        // 设置文件名（包含当前日期）
        const now = new Date();
        const fileName = `捐赠记录_${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}.csv`;
        
        link.setAttribute('href', url);
        link.setAttribute('download', fileName);
        link.style.visibility = 'hidden';
        
        // 触发下载
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // 显示成功消息
        this.success = `成功导出 ${exportData.length} 条捐赠记录`;
        setTimeout(() => { this.success = ''; }, 3000);
        
      } catch (error) {
        console.error('导出失败:', error);
        this.error = '导出失败，请稍后重试';
        setTimeout(() => { this.error = ''; }, 3000);
      }
    },
    
    // 将对象数组转换为CSV格式
    convertToCSV(data) {
      if (!data || data.length === 0) return '';
      
      const headers = Object.keys(data[0]);
      const csvRows = [];
      
      // 添加表头
      csvRows.push(headers.join(','));
      
      // 添加数据行
      for (const row of data) {
        const values = headers.map(header => {
          let value = row[header];
          // 处理包含逗号或引号的值
          if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
            value = `"${value.replace(/"/g, '""')}"`;
          }
          return value;
        });
        csvRows.push(values.join(','));
      }
      
      return csvRows.join('\n');
    },
    
    // 格式化日期时间为完整格式
    formatDateTime(dateTimeString) {
      const date = new Date(dateTimeString);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    },
    searchDonations() {
      // 搜索逻辑已在computed中处理
    },
    filterDonations() {
      // 筛选逻辑已在computed中处理
    },
    openEditModal(donation) {
      this.editDonation = JSON.parse(JSON.stringify(donation))
      this.showEditModal = true
      this.error = ''
      this.success = ''
    },
    async updateDonation() {
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        // 模拟API调用
        // const response = await this.$axios.put(`/shelters/donations/${this.editDonation.id}/`, this.editDonation)
        // if (response.code === 200) {
          // 更新成功
          const index = this.donations.findIndex(d => d.id === this.editDonation.id)
          if (index !== -1) {
            this.donations[index] = {
              ...this.editDonation,
              updated_at: new Date().toISOString()
            }
          }
          this.showEditModal = false
          this.success = '捐赠记录已更新'
          
          // 3秒后清除成功信息
          setTimeout(() => {
            this.success = ''
          }, 3000)
        // } else {
        //   this.error = response.message || '更新失败'
        // }
      } catch (error) {
        this.error = error.response?.data?.message || '更新失败，请检查网络连接'
      } finally {
        this.loading = false
      }
    },
    async markAsCompleted(id) {
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        // 模拟API调用
        // const response = await this.$axios.put(`/shelters/donations/${id}/complete/`)
        // if (response.code === 200) {
          // 标记成功
          const index = this.donations.findIndex(d => d.id === id)
          if (index !== -1) {
            this.donations[index].status = 'completed'
            this.donations[index].updated_at = new Date().toISOString()
          }
          this.success = '捐赠记录已标记为已完成'
          
          // 3秒后清除成功信息
          setTimeout(() => {
            this.success = ''
          }, 3000)
        // } else {
        //   this.error = response.message || '标记失败'
        // }
      } catch (error) {
        this.error = error.response?.data?.message || '标记失败，请检查网络连接'
      } finally {
        this.loading = false
      }
    },
    async deleteDonation(id) {
      if (!confirm('确定要删除这个捐赠记录吗？')) {
        return
      }
          
      this.loading = true
      this.error = ''
      this.success = ''
          
      try {
        // 获取基地 ID
        let shelterId = null
        if (this.user.shelter) {
          if (typeof this.user.shelter === 'object' && this.user.shelter.id) {
            shelterId = this.user.shelter.id
          } else if (typeof this.user.shelter === 'number') {
            shelterId = this.user.shelter
          }
        } else if (this.user.shelter_id) {
          shelterId = this.user.shelter_id
        }
            
        if (!shelterId) {
          this.error = '未找到关联的基地信息'
          return
        }
            
        // 调用真实的后端 API
        const response = await this.$axios.delete(`/shelters/${shelterId}/donations/${id}/`)
        console.log('删除捐赠响应:', response)
            
        if (response.code === 200 || response.status === 204) {
          // 删除成功
          this.donations = this.donations.filter(d => d.id !== id)
          this.success = '捐赠记录已删除'
              
          // 3 秒后清除成功信息
          setTimeout(() => {
            this.success = ''
          }, 3000)
        } else {
          this.error = response.message || '删除失败'
        }
      } catch (error) {
        console.error('删除捐赠失败:', error)
        this.error = error.response?.data?.message || '删除失败，请检查网络连接'
      } finally {
        this.loading = false
      }
    },
    openAddUsageModal() {
      this.newUsage = {
        purpose: '',
        amount: '',
        usage_date: new Date().toISOString().split('T')[0],
        description: '',
        attachments: []
      }
      this.showAddUsageModal = true
      this.error = ''
      this.success = ''
    },
    openEditUsageModal(usage) {
      this.editUsage = JSON.parse(JSON.stringify(usage))
      // 将字符串附件转换为文件对象数组（模拟）
      if (usage.attachments && Array.isArray(usage.attachments)) {
        this.editUsage.attachments = usage.attachments.map(name => ({
          name: name,
          size: 1024, // 模拟大小
          type: 'application/pdf' // 模拟类型
        }))
      } else {
        this.editUsage.attachments = []
      }
      this.showEditUsageModal = true
      this.error = ''
      this.success = ''
    },
    handleFileUpload(event) {
      const files = event.target.files
      if (!files || files.length === 0) return
      
      // 限制最多上传5个文件
      const maxFiles = 5
      const currentCount = this.newUsage.attachments.length
      const canUpload = maxFiles - currentCount
      
      if (canUpload <= 0) {
        this.error = '最多只能上传5个文件'
        setTimeout(() => { this.error = '' }, 3000)
        return
      }
      
      const filesToProcess = Array.from(files).slice(0, canUpload)
      
      filesToProcess.forEach(file => {
        // 验证文件大小 (10MB)
        if (file.size > 10 * 1024 * 1024) {
          this.error = `文件 ${file.name} 大小不能超过10MB`
          setTimeout(() => { this.error = '' }, 3000)
          return
        }
        
        // 添加文件到附件列表
        this.newUsage.attachments.push(file)
      })
      
      // 清空input，允许重复选择同一文件
      event.target.value = ''
    },
    handleEditFileUpload(event) {
      const files = event.target.files
      if (!files || files.length === 0) return
      
      // 限制最多上传5个文件
      const maxFiles = 5
      const currentCount = this.editUsage.attachments.length
      const canUpload = maxFiles - currentCount
      
      if (canUpload <= 0) {
        this.error = '最多只能上传5个文件'
        setTimeout(() => { this.error = '' }, 3000)
        return
      }
      
      const filesToProcess = Array.from(files).slice(0, canUpload)
      
      filesToProcess.forEach(file => {
        // 验证文件大小 (10MB)
        if (file.size > 10 * 1024 * 1024) {
          this.error = `文件 ${file.name} 大小不能超过10MB`
          setTimeout(() => { this.error = '' }, 3000)
          return
        }
        
        // 添加文件到附件列表
        this.editUsage.attachments.push(file)
      })
      
      // 清空input，允许重复选择同一文件
      event.target.value = ''
    },
    removeFile(index) {
      this.newUsage.attachments.splice(index, 1)
    },
    removeEditFile(index) {
      this.editUsage.attachments.splice(index, 1)
    },
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },
    async addUsageRecord() {
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        // 处理附件
        const attachmentNames = this.newUsage.attachments.map(file => file.name)
        
        const usageData = {
          ...this.newUsage,
          attachments: attachmentNames,
          approver: this.user.username,
          usage_type: 'food' // 默认使用类型，根据实际需求修改
        }
        
        // 调用真实的后端API
        // 获取基地ID
        let shelterId = null
        if (this.user.shelter) {
          if (typeof this.user.shelter === 'object' && this.user.shelter.id) {
            shelterId = this.user.shelter.id
          } else if (typeof this.user.shelter === 'number') {
            shelterId = this.user.shelter
          }
        } else if (this.user.shelter_id) {
          shelterId = this.user.shelter_id
        }
        
        if (!shelterId) {
          this.error = '未找到关联的基地信息'
          return
        }
        
        const response = await this.$axios.post(`/shelters/${shelterId}/usages/`, usageData)
        console.log('添加使用记录响应:', response)
        
        if (response.code === 200 || response.status === 201) {
          // 添加成功
          this.showAddUsageModal = false
          this.success = '捐赠使用记录已添加'
          
          // 3秒后清除成功信息
          setTimeout(() => {
            this.success = ''
          }, 3000)
          
          // 重置表单
          this.newUsage = {
            donation: '',
            purpose: '',
            amount: '',
            usage_date: '',
            description: '',
            attachmentsInput: '',
            attachments: []
          }
          
          // 重新加载捐赠使用记录
          await this.loadDonationUsages(shelterId)
        } else {
          this.error = response.message || '添加失败'
        }
      } catch (error) {
        console.error('添加使用记录失败:', error)
        this.error = error.response?.data?.message || '添加失败，请检查网络连接'
      } finally {
        this.loading = false
      }
    },
    async updateUsageRecord() {
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        // 处理附件
        const attachmentNames = this.editUsage.attachments.map(file => file.name)
        
        const usageData = {
          ...this.editUsage,
          attachments: attachmentNames,
          approver: this.user.username
        }
        
        // 调用真实的后端API
        // 获取基地ID
        let shelterId = null
        if (this.user.shelter) {
          if (typeof this.user.shelter === 'object' && this.user.shelter.id) {
            shelterId = this.user.shelter.id
          } else if (typeof this.user.shelter === 'number') {
            shelterId = this.user.shelter
          }
        } else if (this.user.shelter_id) {
          shelterId = this.user.shelter_id
        }
        
        if (!shelterId) {
          this.error = '未找到关联的基地信息'
          return
        }
        
        const response = await this.$axios.put(`/shelters/${shelterId}/usages/${this.editUsage.id}/`, usageData)
        console.log('更新使用记录响应:', response)
        
        if (response.code === 200 || response.status === 200) {
          // 更新成功
          this.showEditUsageModal = false
          this.success = '捐赠使用记录已更新'
          
          // 3秒后清除成功信息
          setTimeout(() => {
            this.success = ''
          }, 3000)
          
          // 重新加载捐赠使用记录
          await this.loadDonationUsages(shelterId)
        } else {
          this.error = response.message || '更新失败'
        }
      } catch (error) {
        console.error('更新使用记录失败:', error)
        this.error = error.response?.data?.message || '更新失败，请检查网络连接'
      } finally {
        this.loading = false
      }
    },
    async deleteUsageRecord(id) {
      if (!confirm('确定要删除这个使用记录吗？')) {
        return
      }
      
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        // 调用真实的后端API
        // 获取基地ID
        let shelterId = null
        if (this.user.shelter) {
          if (typeof this.user.shelter === 'object' && this.user.shelter.id) {
            shelterId = this.user.shelter.id
          } else if (typeof this.user.shelter === 'number') {
            shelterId = this.user.shelter
          }
        } else if (this.user.shelter_id) {
          shelterId = this.user.shelter_id
        }
        
        if (!shelterId) {
          this.error = '未找到关联的基地信息'
          return
        }
        
        const response = await this.$axios.delete(`/shelters/${shelterId}/usages/${id}/`)
        console.log('删除使用记录响应:', response)
        
        if (response.code === 200 || response.status === 204) {
          // 删除成功
          this.success = '捐赠使用记录已删除'
          
          // 3秒后清除成功信息
          setTimeout(() => {
            this.success = ''
          }, 3000)
          
          // 重新加载捐赠使用记录
          await this.loadDonationUsages(shelterId)
        } else {
          this.error = response.message || '删除失败'
        }
      } catch (error) {
        console.error('删除使用记录失败:', error)
        this.error = error.response?.data?.message || '删除失败，请检查网络连接'
      } finally {
        this.loading = false
      }
    },
    // 导入捐赠相关方法
    openImportModal() {
      this.showImportModal = true
      this.importFile = null
      this.importData = []
      this.error = ''
      this.success = ''
    },
    handleImportFile(event) {
      const file = event.target.files[0]
      if (!file) return
      
      // 验证文件类型
      if (!file.name.endsWith('.csv')) {
        this.error = '请上传CSV格式的文件'
        setTimeout(() => { this.error = '' }, 3000)
        return
      }
      
      // 验证文件大小 (10MB)
      if (file.size > 10 * 1024 * 1024) {
        this.error = '文件大小不能超过10MB'
        setTimeout(() => { this.error = '' }, 3000)
        return
      }
      
      this.importFile = file
      this.parseCSV(file)
    },
    parseCSV(file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const text = e.target.result
          const lines = text.split('\n')
          const data = []
          
          // 跳过表头，从第二行开始解析
          for (let i = 1; i < lines.length; i++) {
            const line = lines[i].trim()
            if (!line) continue
            
            const parts = line.split(',')
            if (parts.length >= 2) {
              const donor_name = parts[0].trim()
              const amount = parseFloat(parts[1].trim())
              
              if (donor_name && !isNaN(amount) && amount > 0) {
                data.push({
                  donor_name,
                  amount
                })
              }
            }
          }
          
          this.importData = data
          if (data.length === 0) {
            this.error = 'CSV文件中没有有效的捐赠数据'
            setTimeout(() => { this.error = '' }, 3000)
          }
        } catch (error) {
          console.error('解析CSV文件失败:', error)
          this.error = '解析CSV文件失败，请检查文件格式'
          setTimeout(() => { this.error = '' }, 3000)
        }
      }
      reader.onerror = () => {
        this.error = '读取文件失败'
        setTimeout(() => { this.error = '' }, 3000)
      }
      reader.readAsText(file, 'UTF-8')
    },
    removeImportFile() {
      this.importFile = null
      this.importData = []
    },
    async importDonations() {
      if (!this.canImport) {
        this.error = '没有可导入的数据'
        setTimeout(() => { this.error = '' }, 3000)
        return
      }
      
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        console.log('用户信息:', this.user)
        console.log('用户信息完整结构:', JSON.parse(JSON.stringify(this.user)))
        
        // 获取用户关联的基地ID
        let shelterId = null
        if (this.user.shelter) {
          console.log('用户信息中的shelter字段:', this.user.shelter)
          if (typeof this.user.shelter === 'object' && this.user.shelter.id) {
            shelterId = this.user.shelter.id
            console.log('从用户信息中获取基地ID:', shelterId)
          } else if (typeof this.user.shelter === 'number') {
            // 如果shelter直接是ID数字
            shelterId = this.user.shelter
            console.log('从用户信息中获取基地ID（直接数字）:', shelterId)
          }
        } else if (this.user.shelter_id) {
          // 可能字段名是shelter_id
          shelterId = this.user.shelter_id
          console.log('从用户信息中获取基地ID（shelter_id字段）:', shelterId)
        } else if (this.user.user_type === 'admin') {
          // 管理员可以查看所有捐赠
          console.log('管理员尝试获取基地列表')
          const shelterResponse = await this.$axios.get('/shelters/')
          console.log('基地列表响应:', shelterResponse)
          
          // 处理不同的响应格式
          let shelters = []
          if (shelterResponse.code === 200) {
            if (shelterResponse.data && shelterResponse.data.results) {
              shelters = shelterResponse.data.results
            } else if (Array.isArray(shelterResponse.data)) {
              shelters = shelterResponse.data
            }
          } else if (shelterResponse.results) {
            // 处理默认的DRF响应格式
            shelters = shelterResponse.results
          }
          
          if (shelters.length > 0) {
            shelterId = shelters[0].id
            console.log('从基地列表中获取基地ID:', shelterId)
          }
        }
        
        if (!shelterId) {
          console.error('未找到关联的基地信息')
          this.error = '未找到关联的基地信息'
          return
        }
        
        let donationsToImport = []
        
        // 根据导入方式准备数据
        if (this.importMethod === 'manual') {
          donationsToImport = [{
            donor_name: this.manualDonation.donor_name,
            amount: parseFloat(this.manualDonation.amount),
            donation_type: 'money'
          }]
        } else if (this.importMethod === 'csv') {
          donationsToImport = this.importData.map(item => ({
            donor_name: item.donor_name,
            amount: parseFloat(item.amount),
            donation_type: 'money'
          }))
        }
        
        console.log('准备导入的捐赠数据:', donationsToImport)
        
        // 调用后端API导入捐赠
        for (const donationData of donationsToImport) {
          console.log('导入捐赠数据:', donationData)
          const response = await this.$axios.post(`/shelters/${shelterId}/donations/`, donationData)
          console.log('导入响应:', response)
          
          // 处理不同的响应格式
          if (!response.code && !response.data) {
            // 可能是默认的DRF响应
            if (response.status === 201) {
              // 创建成功
              continue
            } else {
              throw new Error('导入失败')
            }
          } else if (response.code !== 200) {
            throw new Error(response.message || '导入失败')
          }
        }
        
        // 导入成功，重新加载数据
        await this.loadDonations()
        this.showImportModal = false
        this.success = `成功导入 ${donationsToImport.length} 条捐赠记录`
        
        // 重置手动输入表单
        this.manualDonation = {
          donor_name: '',
          amount: ''
        }
        
        // 3秒后清除成功信息
        setTimeout(() => {
          this.success = ''
        }, 3000)
      } catch (error) {
        console.error('导入捐赠失败:', error)
        this.error = error.response?.data?.message || '导入失败，请检查网络连接'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.shelter-donations {
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

/* 导入预览样式 */
.import-preview {
  margin-top: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.preview-table {
  width: 100%;
  border-collapse: collapse;
}

.preview-table th,
.preview-table td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.preview-table th {
  background-color: #f5f5f5;
  font-weight: bold;
}

.preview-table tr:hover {
  background-color: #f9f9f9;
}

/* 导入方式选择样式 */
.import-methods {
  display: flex;
  gap: 20px;
  margin-top: 10px;
}

.method-option {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

.method-option input[type="radio"] {
  margin: 0;
}

.method-option span {
  font-size: 14px;
  color: #333;
}

/* 捐赠统计样式 */
/* 捐赠使用情况样式 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.usage-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.donation-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.usage-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.usage-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  padding: 20px;
  transition: all 0.3s ease;
}

.usage-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.usage-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.usage-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
  flex: 1;
}

.usage-amount {
  font-size: 20px;
  font-weight: bold;
  color: #f44336;
  margin-left: 15px;
}

.usage-info {
  margin-bottom: 20px;
}

.usage-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
  font-size: 14px;
  color: #666;
}

.usage-description {
  margin-bottom: 15px;
}

.usage-description h4 {
  margin: 0 0 5px 0;
  font-size: 14px;
  font-weight: bold;
  color: #555;
}

.usage-description p {
  margin: 0;
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}

.usage-attachments {
  margin-bottom: 15px;
}

.usage-attachments h4 {
  margin: 0 0 5px 0;
  font-size: 14px;
  font-weight: bold;
  color: #555;
}

.attachments-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.attachment-item {
  display: inline-block;
  padding: 5px 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
  font-size: 12px;
  color: #333;
  text-decoration: none;
  transition: all 0.3s ease;
}

.attachment-item:hover {
  background-color: #e0e0e0;
}

.usage-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.stat-card {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 15px;
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

/* 捐赠列表样式 */
.donations-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.donation-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  padding: 20px;
  transition: all 0.3s ease;
}

.donation-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.donation-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.donation-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
  flex: 1;
}

.donation-amount {
  font-size: 20px;
  font-weight: bold;
  color: #ff9a3d;
  margin-left: 15px;
}

.donation-info {
  margin-bottom: 20px;
}

.donation-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
  font-size: 14px;
  color: #666;
}

.meta-item {
  display: inline-block;
}

.donation-description,
.donation-remarks {
  margin-bottom: 15px;
}

.donation-description h4,
.donation-remarks h4 {
  margin: 0 0 5px 0;
  font-size: 14px;
  font-weight: bold;
  color: #555;
}

.donation-description p,
.donation-remarks p {
  margin: 0;
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}

.donation-actions {
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

/* 文件上传样式 */
.file-upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  background-color: #fafafa;
  transition: all 0.3s ease;
}

.file-upload-area:hover {
  border-color: #ff9a3d;
  background-color: #f0f8f0;
}

.file-preview-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 15px;
}

.file-preview {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-icon {
  font-size: 20px;
}

.file-name {
  font-size: 14px;
  color: #333;
}

.file-size {
  font-size: 12px;
  color: #666;
}

.remove-file-btn {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #f44336;
  color: white;
  border: none;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s ease;
}

.remove-file-btn:hover {
  background-color: #da190b;
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
  .shelter-donations {
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
  
  .donation-stats {
    grid-template-columns: 1fr;
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
  
  .donations-list {
    grid-template-columns: 1fr;
  }
  
  .donation-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .donation-amount {
    margin-left: 0;
  }
  
  .donation-meta {
    flex-direction: column;
    gap: 10px;
  }
  
  .modal-content {
    width: 95%;
    max-height: 95vh;
  }
}
</style>