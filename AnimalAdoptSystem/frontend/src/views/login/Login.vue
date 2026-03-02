<template>
  <div class="login">
    <div class="container">
      <h2>用户登录</h2>
      <form class="login-form" @submit.prevent="login">
        <div class="form-group">
          <label for="username">用户名</label>
          <input type="text" id="username" v-model="form.username" required>
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input type="password" id="password" v-model="form.password" required>
        </div>
        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? '登录中...' : '登录' }}
          </button>
          <div class="form-links">
            <router-link to="/password-reset" class="link">忘记密码？</router-link>
            <router-link to="/register" class="btn btn-secondary">注册新账号</router-link>
          </div>
        </div>
        <div class="error-message" v-if="error">
          {{ error }}
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { userApi } from '@/api'

export default {
  name: 'Login',
  data() {
    return {
      form: {
        username: '',
        password: ''
      },
      loading: false,
      error: ''
    }
  },
  methods: {
    async login() {
      this.loading = true
      this.error = ''
      try {
        const response = await userApi.login(this.form)
        if (response.code === 200) {
          localStorage.setItem('token', response.data.access)
          localStorage.setItem('user', JSON.stringify(response.data.user))
          
          // 根据用户类型跳转到不同的界面
          if (response.data.user.user_type === 'shelter') {
            // 基地用户跳转到基地管理界面
            this.$router.push('/shelter/dashboard')
          } else {
            // 普通用户和志愿者跳转到首页
            this.$router.push('/')
          }
        } else {
          this.error = response.message || '登录失败'
        }
      } catch (error) {
        console.error('登录错误:', error)
        if (error.response && error.response.data) {
          this.error = error.response.data.message || '用户名或密码错误'
        } else {
          this.error = '登录失败，请检查网络连接'
        }
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login {
  padding: 60px 0;
  background: linear-gradient(135deg, #fff8f0 0%, #ffeaa7 100%);
  min-height: 100vh;
  display: flex;
  align-items: center;
}

.login h2 {
  text-align: center;
  margin-bottom: 40px;
  font-size: 28px;
  color: #ff6b6b;
  background: linear-gradient(135deg, #ff6b6b 0%, #ff9a3d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-form {
  max-width: 400px;
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

.form-actions {
  margin-top: 30px;
  text-align: center;
}

.form-links {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 15px;
}

.form-links .btn {
  width: 100%;
  margin-bottom: 10px;
}

.link {
  color: #ff6b6b;
  text-decoration: none;
  text-align: center;
  font-size: 14px;
  transition: all 0.3s ease;
}

.link:hover {
  color: #ff9a3d;
  text-decoration: underline;
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
  width: 100%;
  margin-bottom: 10px;
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
  width: 100%;
  margin-bottom: 10px;
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
</style>
