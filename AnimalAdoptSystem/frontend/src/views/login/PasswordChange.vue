<template>
  <div class="password-change">
    <div class="container">
      <h2>修改密码</h2>
      
      <div class="change-content">
        <form @submit.prevent="changePassword" class="change-form">
          <div class="form-group">
            <label for="oldPassword">原密码</label>
            <input 
              type="password" 
              id="oldPassword" 
              v-model="form.old_password" 
              required
              placeholder="请输入当前密码"
            >
          </div>
          <div class="form-group">
            <label for="newPassword">新密码</label>
            <input 
              type="password" 
              id="newPassword" 
              v-model="form.new_password" 
              required
              minlength="6"
              placeholder="请输入至少6位新密码"
            >
          </div>
          <div class="form-group">
            <label for="confirmPassword">确认新密码</label>
            <input 
              type="password" 
              id="confirmPassword" 
              v-model="form.confirm_password" 
              required
              minlength="6"
              placeholder="请再次输入新密码"
            >
          </div>
          <div class="password-strength" v-if="form.new_password">
            <div class="strength-bar">
              <div 
                class="strength-fill" 
                :class="passwordStrength.class"
                :style="{ width: passwordStrength.percentage + '%' }"
              ></div>
            </div>
            <span class="strength-text">{{ passwordStrength.text }}</span>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? '修改中...' : '确认修改' }}
            </button>
            <button type="button" class="btn btn-secondary" @click="$router.back()">
              取消
            </button>
          </div>
          <div class="error-message" v-if="error">
            {{ error }}
          </div>
          <div class="success-message" v-if="success">
            {{ success }}
          </div>
        </form>
        
        <div class="password-tips">
          <h3>密码安全提示</h3>
          <ul>
            <li>密码长度至少6位字符</li>
            <li>建议包含大小写字母、数字和特殊符号</li>
            <li>避免使用生日、姓名等容易被猜到的信息</li>
            <li>定期更换密码以提高账户安全性</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PasswordChange',
  data() {
    return {
      form: {
        old_password: '',
        new_password: '',
        confirm_password: ''
      },
      loading: false,
      error: '',
      success: ''
    }
  },
  computed: {
    passwordStrength() {
      const password = this.form.new_password
      let score = 0
      let text = '弱'
      let className = 'weak'
      
      if (password.length >= 6) score += 1
      if (/[a-z]/.test(password)) score += 1
      if (/[A-Z]/.test(password)) score += 1
      if (/[0-9]/.test(password)) score += 1
      if (/[^A-Za-z0-9]/.test(password)) score += 1
      
      const percentage = (score / 5) * 100
      
      if (score >= 4) {
        text = '强'
        className = 'strong'
      } else if (score >= 3) {
        text = '中等'
        className = 'medium'
      } else if (score >= 2) {
        text = '一般'
        className = 'fair'
      }
      
      return {
        percentage,
        text,
        class: className
      }
    }
  },
  methods: {
    async changePassword() {
      this.loading = true
      this.error = ''
      this.success = ''
      
      // 前端验证
      if (this.form.new_password !== this.form.confirm_password) {
        this.error = '两次输入的新密码不一致'
        this.loading = false
        return
      }
      
      if (this.form.new_password.length < 6) {
        this.error = '新密码长度至少6位'
        this.loading = false
        return
      }
      
      try {
        const response = await this.$axios.post('/users/password-change/', this.form)
        if (response.code === 200) {
          this.success = '密码修改成功'
          // 清空表单
          this.form = {
            old_password: '',
            new_password: '',
            confirm_password: ''
          }
          // 2秒后自动跳转
          setTimeout(() => {
            this.$router.push('/profile')
          }, 2000)
        } else {
          this.error = response.message || '密码修改失败'
        }
      } catch (error) {
        this.error = error.response?.data?.message || '密码修改失败，请检查网络连接'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.password-change {
  padding: 40px 0;
  background: linear-gradient(135deg, #fff8f0 0%, #ffeaa7 100%);
  min-height: 100vh;
}

.password-change h2 {
  text-align: center;
  margin-bottom: 30px;
  font-size: 28px;
  color: #ff6b6b;
  background: linear-gradient(135deg, #ff6b6b 0%, #ff9a3d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  width: 90%;
}

.change-content {
  background: linear-gradient(135deg, #ffffff 0%, #fff5e6 100%);
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 15px 40px rgba(255, 154, 61, 0.3);
  padding: 40px;
  border: 1px solid rgba(255, 154, 61, 0.1);
}

.change-form {
  max-width: 500px;
  margin: 0 auto 40px;
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

.form-group input {
  width: 100%;
  padding: 12px;
  border: 2px solid #ffcc99;
  border-radius: 8px;
  font-size: 16px;
  background: linear-gradient(135deg, #ffffff 0%, #fffaf5 100%);
  transition: all 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #ff9a3d;
  box-shadow: 0 0 0 3px rgba(255, 154, 61, 0.3);
  transform: scale(1.02);
}

.password-strength {
  margin: 15px 0;
}

.strength-bar {
  height: 8px;
  background-color: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.strength-fill {
  height: 100%;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.strength-fill.weak {
  background: linear-gradient(90deg, #f44336, #ff9800);
}

.strength-fill.fair {
  background: linear-gradient(90deg, #ff9800, #ffc107);
}

.strength-fill.medium {
  background: linear-gradient(90deg, #ffc107, #4caf50);
}

.strength-fill.strong {
  background: linear-gradient(90deg, #4caf50, #2e7d32);
}

.strength-text {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.form-actions {
  margin-top: 30px;
  display: flex;
  gap: 15px;
  justify-content: center;
}

.btn {
  padding: 12px 30px;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  text-align: center;
  font-weight: 500;
  border: none;
  min-width: 120px;
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

.success-message {
  margin-top: 20px;
  padding: 15px;
  background: linear-gradient(135deg, #e8f5e8 0%, #f0fff0 100%);
  color: #2e7d32;
  border-radius: 8px;
  text-align: center;
  border: 1px solid rgba(46, 125, 50, 0.3);
  box-shadow: 0 2px 8px rgba(46, 125, 50, 0.2);
}

.password-tips {
  background: linear-gradient(135deg, #fff8f0 0%, #fff5e6 100%);
  padding: 25px;
  border-radius: 10px;
  border-left: 4px solid #ff9a3d;
}

.password-tips h3 {
  color: #ff6b6b;
  margin-bottom: 15px;
  font-size: 20px;
}

.password-tips ul {
  list-style: none;
  padding: 0;
}

.password-tips li {
  padding: 8px 0;
  padding-left: 25px;
  position: relative;
  color: #666;
  line-height: 1.5;
}

.password-tips li:before {
  content: "•";
  color: #ff9a3d;
  font-size: 20px;
  position: absolute;
  left: 0;
  top: 8px;
}

@media (max-width: 768px) {
  .password-change {
    padding: 20px 0;
  }
  
  .change-content {
    padding: 25px;
    margin: 0 15px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
  
  .password-tips {
    margin-top: 30px;
  }
}
</style>