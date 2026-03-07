<template>
  <div class="register">
    <div class="container mx-auto">
      <div class="register-form">
        <h2>用户注册</h2>
        <form @submit.prevent="register">
          <!-- 用户类型选择 -->
          <div class="form-group">
            <label>用户类型：</label>
            <select v-model="form.user_type" required>
              <option value="normal">领养者</option>
              <option value="volunteer">志愿者</option>
              <option value="shelter">基地管理员</option>
            </select>
          </div>

          <!-- 基础信息 -->
          <div class="form-group">
            <label>用户名：</label>
            <input type="text" v-model="form.username" required placeholder="请输入用户名">
          </div>

          <div class="form-group">
            <label>邮箱：</label>
            <input type="email" v-model="form.email" required placeholder="请输入邮箱地址">
          </div>

          <div class="form-group">
            <label>手机号：</label>
            <input type="tel" v-model="form.phone" required placeholder="请输入手机号码">
          </div>

          <div class="form-group">
            <label>密码：</label>
            <input type="password" v-model="form.password" required placeholder="请输入密码（至少6位）">
          </div>

          <div class="form-group">
            <label>确认密码：</label>
            <input type="password" v-model="form.password2" required placeholder="请再次输入密码">
          </div>

          <!-- 基地管理员额外信息 -->
          <div v-if="form.user_type === 'shelter'" class="shelter-fields">
            <h3>基地信息</h3>
            <div class="form-group">
              <label>基地名称：</label>
              <input type="text" v-model="form.shelter_name" placeholder="请输入基地名称">
            </div>
            <div class="form-group">
              <label>基地地址：</label>
              <input type="text" v-model="form.shelter_address" placeholder="请输入基地详细地址">
            </div>
            <div class="form-group">
              <label>联系人姓名：</label>
              <input type="text" v-model="form.shelter_contact_name" placeholder="请输入联系人姓名">
            </div>
            <div class="form-group">
              <label>基地描述：</label>
              <textarea v-model="form.shelter_description" placeholder="请简要描述您的基地"></textarea>
            </div>
            <div class="form-group">
              <label>容纳能力：</label>
              <input type="number" v-model="form.shelter_capacity" placeholder="请输入基地最大容纳动物数量">
            </div>
            <div class="form-group">
              <label>收款码：</label>
              <input type="file" @change="handleQrCodeUpload" accept="image/*">
              <div v-if="form.shelter_qr_code" class="qr-code-preview">
                <img :src="form.shelter_qr_code" alt="收款码预览" style="max-width: 200px; max-height: 200px;">
              </div>
            </div>
          </div>

          <!-- 错误信息显示 -->
          <div v-if="error" class="error-message">
            {{ error }}
          </div>

          <!-- 提交按钮 -->
          <div class="form-actions">
            <button type="submit" :disabled="loading" class="btn btn-primary">
              {{ loading ? '注册中...' : '注册' }}
            </button>
            <router-link to="/login" class="btn btn-secondary">
              已有账号？立即登录
            </router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { userApi } from '@/api'

export default {
  name: 'Register',
  data() {
    return {
      form: {
        username: '',
        email: '',
        password: '',
        password2: '',
        user_type: 'normal',
        phone: '',
        // 基地相关字段
        shelter_name: '',
        shelter_address: '',
        shelter_contact_name: '',
        shelter_description: '',
        shelter_capacity: '',
        shelter_qr_code: null
      },
      qrCodeFile: null,
      error: '',
      loading: false
    }
  },
  watch: {
    'form.user_type'(newVal) {
      // 当切换用户类型时，清空基地相关字段
      if (newVal !== 'shelter') {
        this.form.shelter_name = ''
        this.form.shelter_address = ''
        this.form.shelter_contact_name = ''
        this.form.shelter_description = ''
        this.form.shelter_capacity = ''
        this.form.shelter_qr_code = null
        this.qrCodeFile = null
      }
    }
  },
  methods: {
    handleQrCodeUpload(event) {
      const file = event.target.files[0]
      if (file) {
        this.qrCodeFile = file
        // 生成预览URL
        const reader = new FileReader()
        reader.onload = (e) => {
          this.form.shelter_qr_code = e.target.result
        }
        reader.readAsDataURL(file)
      }
    },
    async register() {
      // 前端验证
      if (this.form.password.length < 6) {
        this.error = '密码长度至少6位'
        return
      }
      
      if (this.form.password !== this.form.password2) {
        this.error = '两次输入的密码不一致'
        return
      }
      
      // 验证基地注册字段
      if (this.form.user_type === 'shelter') {
        if (!this.form.shelter_name || !this.form.shelter_address || !this.form.shelter_contact_name || !this.form.shelter_capacity) {
          this.error = '请填写完整的基地信息'
          return
        }
      }
      
      this.loading = true
      this.error = ''
      try {
        if (this.form.user_type === 'shelter' && this.form.shelter_qr_code) {
          // 使用 Base64 数据发送
          const requestData = {
            username: this.form.username,
            email: this.form.email,
            password: this.form.password,
            password2: this.form.password2,
            user_type: this.form.user_type,
            phone: this.form.phone,
            shelter_name: this.form.shelter_name,
            shelter_address: this.form.shelter_address,
            shelter_contact_name: this.form.shelter_contact_name,
            shelter_description: this.form.shelter_description,
            shelter_capacity: this.form.shelter_capacity,
            shelter_qr_code: this.form.shelter_qr_code  // Base64 字符串
          }
                
          // 发送注册请求
          const response = await userApi.register(requestData)
          if (response.code === 200) {
            // 注册成功后跳转到登录页
            this.$router.push('/login')
          } else {
            this.error = response.message || '注册失败'
          }
        } else {
          // 准备发送的数据
          const requestData = {
            username: this.form.username,
            email: this.form.email,
            password: this.form.password,
            password2: this.form.password2,
            user_type: this.form.user_type,
            phone: this.form.phone
          }
          
          // 如果是基地用户，添加基地相关信息
          if (this.form.user_type === 'shelter') {
            requestData.shelter_name = this.form.shelter_name
            requestData.shelter_address = this.form.shelter_address
            requestData.shelter_contact_name = this.form.shelter_contact_name
            requestData.shelter_description = this.form.shelter_description
            requestData.shelter_capacity = this.form.shelter_capacity
          }
          
          // 发送注册请求
          const response = await userApi.register(requestData)
          if (response.code === 200) {
            // 注册成功后跳转到登录页
            this.$router.push('/login')
          } else {
            this.error = response.message || '注册失败'
          }
        }
      } catch (error) {
        // 注册错误处理
        console.error('注册失败:', error)
        
        // 显示具体的错误信息
        if (error.response && error.response.data) {
          if (typeof error.response.data === 'object') {
            if (error.response.data.errors) {
              // 如果是验证错误，显示具体的字段错误
              const errorMessages = []
              for (const [field, messages] of Object.entries(error.response.data.errors)) {
                if (Array.isArray(messages)) {
                  errorMessages.push(`${field}: ${messages.join(', ')}`)
                } else {
                  errorMessages.push(`${field}: ${messages}`)
                }
              }
              this.error = errorMessages.join('; ')
            } else if (error.response.data.message) {
              this.error = error.response.data.message
            } else {
              this.error = JSON.stringify(error.response.data)
            }
          } else {
            this.error = error.response.data
          }
        } else if (error.response && error.response.status) {
          this.error = `注册失败 (${error.response.status})`
        } else {
          this.error = '网络连接错误，请检查网络连接'
        }
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.register {
  padding: 60px 0;
  background: linear-gradient(135deg, #fff8f0 0%, #ffeaa7 100%);
  min-height: 100vh;
  display: flex;
  align-items: center;
}

.register h2 {
  text-align: center;
  margin-bottom: 40px;
  font-size: 28px;
  color: #ff6b6b;
  background: linear-gradient(135deg, #ff6b6b 0%, #ff9a3d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.register-form {
  max-width: 500px;
  margin: 0 auto;
  background: linear-gradient(135deg, #ffffff 0%, #fff5e6 100%);
  padding: 40px;
  border-radius: 15px;
  box-shadow: 0 15px 40px rgba(255, 154, 61, 0.3);
  border: 1px solid rgba(255, 154, 61, 0.1);
  backdrop-filter: blur(10px);
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
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 2px solid #ffcc99;
  border-radius: 8px;
  font-size: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #fffaf5 100%);
  transition: all 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #ff9a3d;
  box-shadow: 0 0 0 3px rgba(255, 154, 61, 0.3);
  transform: scale(1.02);
}

.form-actions {
  margin-top: 30px;
}

.form-actions .btn {
  width: 100%;
  margin-bottom: 10px;
}

.btn-primary {
  background: linear-gradient(135deg, #ff9a3d 0%, #ff6b6b 100%);
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
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
  padding: 12px;
  border-radius: 8px;
  font-size: 16px;
  text-decoration: none;
  display: block;
  text-align: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(255, 154, 61, 0.2);
  font-weight: 500;
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #fff5e6 0%, #ffffff 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 154, 61, 0.3);
  border-color: #ff9a3d;
}

.shelter-fields {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 2px solid rgba(255, 154, 61, 0.2);
  background: linear-gradient(135deg, #fff8f0 0%, #fff5e6 100%);
  border-radius: 10px;
  padding: 20px;
}

.shelter-fields h3 {
  margin-bottom: 20px;
  font-size: 20px;
  color: #ff6b6b;
  background: linear-gradient(135deg, #ff6b6b 0%, #ff9a3d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.error-message {
  margin-top: 20px;
  padding: 15px;
  background: linear-gradient(135deg, #ffebee 0%, #fff5e6 100%);
  color: #ff6b6b;
  border-radius: 8px;
  text-align: center;
  border: 1px solid rgba(255, 107, 107, 0.3);
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.2);
}
</style>