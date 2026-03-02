<template>
  <div class="adoption-apply">
    <div class="container">
      <h2>领养申请</h2>
      
      <!-- 云领养提醒 -->
      <div class="cloud-adoption-notice">
        <div class="notice-header">
          <i class="notice-icon">☁️</i>
          <h3>重要提醒：云领养说明</h3>
        </div>
        <div class="notice-content">
          <p>本服务为<strong>云领养系统</strong>，动物仍将留在基地由专业人员照顾。</p>
          <p>您无法实际带走动物，但可以：</p>
          <ul>
            <li>远程关爱和关注动物的生活状况</li>
            <li>申请线下互动（探访、志愿服务、短期寄养等）</li>
            <li>参与基地举办的各类活动</li>
            <li>通过捐赠等方式支持动物福利</li>
          </ul>
          <p class="highlight">如需实际接触动物，请申请「基地互动」功能！</p>
        </div>
        <div class="notice-actions">
          <router-link to="/shelters" class="btn btn-outline">查看基地互动</router-link>
        </div>
      </div>
      <div v-if="animal" class="apply-form">
        <div class="animal-preview">
          <img v-if="animal.images && animal.images.length > 0" :src="animal.images[0]" :alt="animal.name" class="animal-image">
          <img v-else src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20animal%20portrait&image_size=square" :alt="animal.name" class="animal-image">
          <h3>{{ animal.name }}</h3>
          <p>{{ animal.species === 'cat' ? '猫' : animal.species === 'dog' ? '狗' : '其他' }} · {{ animal.breed }} · {{ animal.age }}个月</p>
        </div>
        <form @submit.prevent="submitApplication">
          <div class="form-group">
            <label for="application_reason">申请原因</label>
            <textarea id="application_reason" v-model="form.application_reason" required rows="4"></textarea>
          </div>
          <div class="form-group">
            <label for="personal_info">个人情况说明</label>
            <textarea id="personal_info" v-model="form.personal_info" required rows="4"></textarea>
          </div>
          <div class="form-group">
            <label for="contact_phone">联系电话</label>
            <input type="tel" id="contact_phone" v-model="form.contact_phone" required>
          </div>
          <div class="form-group">
            <label for="contact_address">联系地址</label>
            <input type="text" id="contact_address" v-model="form.contact_address" required>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? '提交中...' : '提交申请' }}
            </button>
            <router-link :to="`/animal/${animal.id}`" class="btn btn-secondary">取消</router-link>
          </div>
          <div class="error-message" v-if="error">
            {{ error }}
          </div>
          <div class="success-message" v-if="success">
            {{ success }}
          </div>
        </form>
      </div>
      <div v-else class="loading">
        <p v-if="error">{{ error }}</p>
        <p v-else>加载中...</p>
      </div>
    </div>
  </div>
</template>

<script>
import { adoptionApi } from '@/api'

export default {
  name: 'AdoptionApply',
  data() {
    return {
      animal: null,
      form: {
        application_reason: '',
        personal_info: '',
        contact_phone: '',
        contact_address: ''
      },
      loading: false,
      error: '',
      success: ''
    }
  },
  mounted() {
    // 组件挂载初始化
    this.getAnimalDetail()
  },
  methods: {
    async getAnimalDetail() {
      try {
        const animalId = this.$route.params.animalId
        // 获取动物详情
        
        if (!animalId) {
          this.error = '未指定动物ID'
          return
        }
        
        // 请求动物数据
        const response = await this.$axios.get(`/animals/${animalId}/`)
        
        // 处理响应数据
        
        // 尝试多种可能的响应格式
        if (response && typeof response === 'object') {
          if (response.id) {
            this.animal = response
            // 成功获取动物数据
          } else if (response.data && response.data.id) {
            this.animal = response.data
            // 成功获取包装的数据
          } else if (response.code === 200 && response.data) {
            this.animal = response.data
            // 成功获取API响应格式
          } else {
            // 未知响应结构
            this.error = '响应格式不符合预期'
          }
        } else {
          // 无效响应类型
          this.error = '服务器响应格式异常'
        }
        
      } catch (error) {
        // 错误处理
        
        if (error.response) {
          // 处理错误响应
          this.error = `请求失败 (${error.response.status}): ${JSON.stringify(error.response.data)}`
        } else {
          this.error = '网络连接错误'
        }
      }
    },
    async submitApplication() {
      this.loading = true
      this.error = ''
      this.success = ''
      try {
        const animalId = this.$route.params.animalId
        const response = await adoptionApi.applyAdoption({
          ...this.form,
          animal: parseInt(animalId)
        })
        if (response.code === 200) {
          this.success = '申请提交成功，我们会尽快审核'
          // 清空表单
          this.form = {
            application_reason: '',
            personal_info: '',
            contact_phone: '',
            contact_address: ''
          }
          // 3秒后跳转到领养记录页
          setTimeout(() => {
            this.$router.push('/adoption/my')
          }, 3000)
        } else {
          this.error = response.message || '申请提交失败'
        }
      } catch (error) {
        this.error = error.response?.data?.message || '申请提交失败，请检查网络连接'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.adoption-apply {
  padding: 40px 0;
}

.cloud-adoption-notice {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border: 2px solid #2196f3;
  border-radius: 12px;
  padding: 25px;
  margin-bottom: 30px;
  box-shadow: 0 4px 15px rgba(33, 150, 243, 0.2);
}

.notice-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.notice-icon {
  font-size: 28px;
}

.notice-header h3 {
  margin: 0;
  color: #1976d2;
  font-size: 22px;
}

.notice-content {
  margin-bottom: 20px;
}

.notice-content p {
  margin: 10px 0;
  line-height: 1.6;
  color: #333;
}

.notice-content ul {
  padding-left: 25px;
  margin: 15px 0;
}

.notice-content li {
  margin: 8px 0;
  color: #555;
}

.highlight {
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
  padding: 12px;
  border-radius: 8px;
  border-left: 4px solid #ff9800;
  font-weight: bold;
  color: #e65100;
}

.notice-actions {
  text-align: center;
}

.btn-outline {
  background: transparent;
  color: #2196f3;
  border: 2px solid #2196f3;
  padding: 10px 20px;
  border-radius: 6px;
  text-decoration: none;
  display: inline-block;
  transition: all 0.3s ease;
  font-weight: 500;
}

.btn-outline:hover {
  background: #2196f3;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3);
}

.adoption-apply h2 {
  margin-bottom: 30px;
  font-size: 28px;
  color: #333;
}

.apply-form {
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  padding: 40px;
}

.animal-preview {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.animal-image {
  width: 150px;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
}

.animal-preview h3 {
  font-size: 20px;
  margin: 0;
}

.animal-preview p {
  margin: 5px 0 0;
  color: #666;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #555;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  font-family: inherit;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #ff9a3d;
  box-shadow: 0 0 0 3px rgba(255, 154, 61, 0.3);
  transform: scale(1.02);
}

.form-actions {
  margin-top: 30px;
  display: flex;
  gap: 15px;
}

.btn {
  padding: 12px 24px;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
  text-decoration: none;
  display: inline-block;
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

.btn-primary:disabled {
  background: linear-gradient(135deg, #cccccc 0%, #e0e0e0 100%);
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
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

.btn-secondary:hover {
  background: linear-gradient(135deg, #fff5e6 0%, #ffffff 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 154, 61, 0.3);
  border-color: #ff9a3d;
}

.error-message {
  margin-top: 20px;
  padding: 10px;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 4px;
}

.success-message {
  margin-top: 20px;
  padding: 10px;
  background-color: #e8f5e8;
  color: #2e7d32;
  border-radius: 4px;
}

.loading {
  text-align: center;
  padding: 40px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

@media (max-width: 768px) {
  .apply-form {
    padding: 20px;
  }
  
  .animal-preview {
    flex-direction: column;
    text-align: center;
  }
  
  .animal-image {
    width: 200px;
    height: 150px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    text-align: center;
  }
}
</style>
