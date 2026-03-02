<template>
  <div class="password-reset">
    <div class="container">
      <h2>找回密码</h2>
      
      <!-- 步骤1：输入邮箱 -->
      <div v-if="step === 1" class="reset-step">
        <p class="step-description">请输入您注册时使用的邮箱地址，我们将向该邮箱发送验证码。</p>
        <form @submit.prevent="sendVerificationCode" class="reset-form">
          <div class="form-group">
            <label for="email">邮箱地址</label>
            <input 
              type="email" 
              id="email" 
              v-model="emailForm.email" 
              required
              placeholder="请输入您的邮箱地址"
            >
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? '发送中...' : '发送验证码' }}
            </button>
            <router-link to="/login" class="btn btn-secondary">返回登录</router-link>
          </div>
          <div class="error-message" v-if="error">
            {{ error }}
          </div>
        </form>
      </div>

      <!-- 步骤2：输入验证码和新密码 -->
      <div v-if="step === 2" class="reset-step">
        <p class="step-description">验证码已发送至您的邮箱，请查收并在下方输入验证码和新密码。</p>
        <form @submit.prevent="resetPassword" class="reset-form">
          <div class="form-group">
            <label for="verificationCode">验证码</label>
            <input 
              type="text" 
              id="verificationCode" 
              v-model="resetForm.verification_code" 
              required
              maxlength="6"
              placeholder="请输入6位验证码"
            >
            <small class="hint">开发环境下验证码为：{{ devCode }}</small>
          </div>
          <div class="form-group">
            <label for="newPassword">新密码</label>
            <input 
              type="password" 
              id="newPassword" 
              v-model="resetForm.new_password" 
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
              v-model="resetForm.confirm_password" 
              required
              minlength="6"
              placeholder="请再次输入新密码"
            >
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? '重置中...' : '重置密码' }}
            </button>
            <button type="button" class="btn btn-secondary" @click="step = 1">重新发送</button>
          </div>
          <div class="error-message" v-if="error">
            {{ error }}
          </div>
          <div class="success-message" v-if="success">
            {{ success }}
          </div>
        </form>
      </div>

      <!-- 重置成功 -->
      <div v-if="step === 3" class="reset-success">
        <div class="success-icon">✓</div>
        <h3>密码重置成功！</h3>
        <p>您的密码已经重置成功，现在可以使用新密码登录系统。</p>
        <router-link to="/login" class="btn btn-primary">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PasswordReset',
  data() {
    return {
      step: 1,
      emailForm: {
        email: ''
      },
      resetForm: {
        email: '',
        verification_code: '',
        new_password: '',
        confirm_password: ''
      },
      loading: false,
      error: '',
      success: '',
      devCode: '123456' // 开发环境显示的验证码
    }
  },
  methods: {
    async sendVerificationCode() {
      this.loading = true
      this.error = ''
      try {
        const response = await this.$axios.post('/users/password-reset/', this.emailForm)
        if (response.code === 200) {
          this.resetForm.email = this.emailForm.email
          this.step = 2
          this.devCode = response.data.verification_code || '123456'
        } else {
          this.error = response.message || '发送验证码失败'
        }
      } catch (error) {
        this.error = error.response?.data?.message || '发送验证码失败，请检查网络连接'
      } finally {
        this.loading = false
      }
    },
    async resetPassword() {
      this.loading = true
      this.error = ''
      this.success = ''
      try {
        const response = await this.$axios.post('/users/password-reset-confirm/', this.resetForm)
        if (response.code === 200) {
          this.step = 3
          this.success = '密码重置成功'
        } else {
          this.error = response.message || '密码重置失败'
        }
      } catch (error) {
        this.error = error.response?.data?.message || '密码重置失败，请检查网络连接'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.password-reset {
  padding: 60px 0;
  background: linear-gradient(135deg, #fff8f0 0%, #ffeaa7 100%);
  min-height: 100vh;
  display: flex;
  align-items: center;
}

.password-reset h2 {
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
  max-width: 500px;
  margin: 0 auto;
  width: 90%;
}

.reset-step {
  background: linear-gradient(135deg, #ffffff 0%, #fff5e6 100%);
  padding: 40px;
  border-radius: 15px;
  box-shadow: 0 15px 40px rgba(255, 154, 61, 0.3);
  border: 1px solid rgba(255, 154, 61, 0.1);
}

.step-description {
  text-align: center;
  margin-bottom: 30px;
  color: #666;
  line-height: 1.6;
}

.reset-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: bold;
  color: #555;
}

.form-group input {
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

.hint {
  color: #ff6b6b;
  font-size: 14px;
  margin-top: 5px;
}

.form-actions {
  margin-top: 20px;
  display: flex;
  gap: 15px;
  flex-direction: column;
}

.btn {
  padding: 12px;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  text-align: center;
  font-weight: 500;
  border: none;
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

.reset-success {
  background: linear-gradient(135deg, #ffffff 0%, #fff5e6 100%);
  padding: 60px 40px;
  border-radius: 15px;
  box-shadow: 0 15px 40px rgba(255, 154, 61, 0.3);
  border: 1px solid rgba(255, 154, 61, 0.1);
  text-align: center;
}

.success-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #4caf50 0%, #8bc34a 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  font-size: 40px;
  color: white;
  font-weight: bold;
}

.reset-success h3 {
  color: #4caf50;
  margin-bottom: 15px;
  font-size: 24px;
}

.reset-success p {
  color: #666;
  margin-bottom: 30px;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .password-reset {
    padding: 30px 0;
  }
  
  .reset-step, .reset-success {
    padding: 30px 20px;
    margin: 0 15px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>