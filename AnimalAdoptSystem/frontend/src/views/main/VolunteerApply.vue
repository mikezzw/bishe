<template>
  <div class="volunteer-apply">
    <div class="container">
      <h2>申请成为志愿者</h2>
      
      <div class="application-guide">
        <div class="guide-section">
          <h3>📋 申请须知</h3>
          <ul>
            <li>年满18周岁，身体健康</li>
            <li>热爱动物，有责任心和耐心</li>
            <li>能够定期参与志愿服务活动</li>
            <li>遵守基地规章制度</li>
          </ul>
        </div>
        
        <div class="guide-section">
          <h3>🌟 志愿者权益</h3>
          <ul>
            <li>参与各类动物救助活动</li>
            <li>获得专业技能培训</li>
            <li>积累志愿服务时长</li>
            <li>优先参与基地特色活动</li>
          </ul>
        </div>
      </div>

      <form @submit.prevent="submitApplication" class="application-form" v-if="!submitted">
        <div class="form-section">
          <h3>基本信息</h3>
          
          <div class="form-row">
            <div class="form-group">
              <label for="name">姓名 *</label>
              <input 
                type="text" 
                id="name" 
                v-model="formData.name" 
                required 
                :class="{ 'error': errors.name }"
              >
              <span class="error-msg" v-if="errors.name">{{ errors.name }}</span>
            </div>
            
            <div class="form-group">
              <label for="gender">性别 *</label>
              <select id="gender" v-model="formData.gender" required>
                <option value="">请选择</option>
                <option value="male">男</option>
                <option value="female">女</option>
              </select>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="age">年龄 *</label>
              <input 
                type="number" 
                id="age" 
                v-model.number="formData.age" 
                min="18" 
                max="80" 
                required
                :class="{ 'error': errors.age }"
              >
              <span class="error-msg" v-if="errors.age">{{ errors.age }}</span>
            </div>
            
            <div class="form-group">
              <label for="education">学历 *</label>
              <select id="education" v-model="formData.education" required>
                <option value="">请选择</option>
                <option value="高中及以下">高中及以下</option>
                <option value="大专">大专</option>
                <option value="本科">本科</option>
                <option value="硕士及以上">硕士及以上</option>
              </select>
            </div>
          </div>
          
          <div class="form-group">
            <label for="occupation">职业 *</label>
            <input 
              type="text" 
              id="occupation" 
              v-model="formData.occupation" 
              required
              placeholder="请输入您的职业"
            >
          </div>
        </div>

        <div class="form-section">
          <h3>志愿服务信息</h3>
          
          <div class="form-group">
            <label for="skills">技能特长 *</label>
            <textarea 
              id="skills" 
              v-model="formData.skills" 
              rows="3" 
              required
              placeholder="请描述您的技能特长，如：宠物护理、摄影、文案写作等"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label for="availability">可服务时间 *</label>
            <textarea 
              id="availability" 
              v-model="formData.availability" 
              rows="2" 
              required
              placeholder="请说明您可以参与志愿服务的时间安排"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label for="experience">志愿者经历</label>
            <textarea 
              id="experience" 
              v-model="formData.experience" 
              rows="3"
              placeholder="请描述您过往的志愿者经历（如有）"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label for="motivation">志愿服务动机 *</label>
            <textarea 
              id="motivation" 
              v-model="formData.motivation" 
              rows="4" 
              required
              placeholder="请说明您为什么想成为志愿者，以及您对动物保护的理解"
            ></textarea>
          </div>
        </div>

        <div class="form-actions">
          <button type="button" class="btn btn-secondary" @click="resetForm">重置</button>
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? '提交中...' : '提交申请' }}
          </button>
        </div>
        
        <div class="error-message" v-if="error">
          {{ error }}
        </div>
      </form>

      <div class="success-message" v-if="submitted">
        <div class="success-icon">✓</div>
        <h3>申请提交成功！</h3>
        <p>感谢您的申请，我们将在3个工作日内完成审核。</p>
        <p>审核结果将通过系统消息通知您。</p>
        <router-link to="/" class="btn btn-primary">返回首页</router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VolunteerApply',
  data() {
    return {
      formData: {
        name: '',
        gender: '',
        age: null,
        education: '',
        occupation: '',
        skills: '',
        availability: '',
        experience: '',
        motivation: ''
      },
      errors: {},
      loading: false,
      submitted: false,
      error: ''
    }
  },
  mounted() {
    // 检查用户是否已登录
    const token = localStorage.getItem('token')
    if (!token) {
      this.$router.push('/login')
      return
    }
    
    // 检查是否已经是志愿者
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    if (user.user_type === 'volunteer') {
      this.submitted = true
      this.error = '您已经是志愿者了，无需重复申请'
    }
  },
  methods: {
    validateForm() {
      this.errors = {}
      
      // 姓名验证
      if (!this.formData.name.trim()) {
        this.errors.name = '请输入姓名'
      } else if (this.formData.name.trim().length < 2) {
        this.errors.name = '姓名至少2个字符'
      }
      
      // 年龄验证
      if (!this.formData.age) {
        this.errors.age = '请输入年龄'
      } else if (this.formData.age < 18 || this.formData.age > 80) {
        this.errors.age = '年龄必须在18-80岁之间'
      }
      
      // 其他必填项验证
      if (!this.formData.gender) {
        this.errors.gender = '请选择性别'
      }
      
      if (!this.formData.education) {
        this.errors.education = '请选择学历'
      }
      
      if (!this.formData.occupation.trim()) {
        this.errors.occupation = '请输入职业'
      }
      
      if (!this.formData.skills.trim()) {
        this.errors.skills = '请描述您的技能特长'
      }
      
      if (!this.formData.availability.trim()) {
        this.errors.availability = '请说明可服务时间'
      }
      
      if (!this.formData.motivation.trim()) {
        this.errors.motivation = '请说明志愿服务动机'
      }
      
      return Object.keys(this.errors).length === 0
    },
    
    async submitApplication() {
      if (!this.validateForm()) {
        return
      }
      
      this.loading = true
      this.error = ''
      
      try {
        const response = await this.$axios.post('/volunteers/profiles/', this.formData)
        
        if (response.code === 200 || response.code === 201) {
          this.submitted = true
          
          // 更新本地用户信息
          const user = JSON.parse(localStorage.getItem('user') || '{}')
          user.user_type = 'volunteer'
          localStorage.setItem('user', JSON.stringify(user))
        } else {
          this.error = response.message || '申请提交失败'
        }
      } catch (error) {
        console.error('志愿者申请失败:', error)
        if (error.response?.status === 400) {
          this.error = error.response.data.message || '您已经提交过志愿者申请'
        } else {
          this.error = error.response?.data?.message || '申请提交失败，请稍后重试'
        }
      } finally {
        this.loading = false
      }
    },
    
    resetForm() {
      this.formData = {
        name: '',
        gender: '',
        age: null,
        education: '',
        occupation: '',
        skills: '',
        availability: '',
        experience: '',
        motivation: ''
      }
      this.errors = {}
      this.error = ''
    }
  }
}
</script>

<style scoped>
.volunteer-apply {
  padding: 40px 0;
  background: linear-gradient(135deg, #fff8f0 0%, #ffeaa7 100%);
  min-height: 100vh;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px;
}

h2 {
  text-align: center;
  color: #ff6b6b;
  margin-bottom: 30px;
  font-size: 28px;
}

.application-guide {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.guide-section {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(255, 154, 61, 0.2);
  border: 1px solid rgba(255, 154, 61, 0.1);
}

.guide-section h3 {
  color: #ff9a3d;
  margin-bottom: 15px;
  font-size: 18px;
}

.guide-section ul {
  padding-left: 20px;
}

.guide-section li {
  margin-bottom: 8px;
  color: #666;
  line-height: 1.5;
}

.application-form {
  background: white;
  padding: 30px;
  border-radius: 15px;
  box-shadow: 0 8px 25px rgba(255, 154, 61, 0.3);
  border: 1px solid rgba(255, 154, 61, 0.1);
}

.form-section {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.form-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.form-section h3 {
  color: #ff6b6b;
  margin-bottom: 20px;
  font-size: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
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
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  font-family: inherit;
  transition: all 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #ff9a3d;
  box-shadow: 0 0 0 3px rgba(255, 154, 61, 0.2);
}

.form-group input.error,
.form-group select.error,
.form-group textarea.error {
  border-color: #ff6b6b;
}

.error-msg {
  color: #ff6b6b;
  font-size: 14px;
  margin-top: 5px;
  display: block;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.btn {
  padding: 12px 30px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.btn-primary {
  background: linear-gradient(135deg, #ff9a3d 0%, #ff6b6b 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
}

.btn-primary:disabled {
  background: #cccccc;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: linear-gradient(135deg, #ffffff 0%, #fff5e6 100%);
  color: #ff6b6b;
  border: 2px solid #ffcc99;
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #fff5e6 0%, #ffffff 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 154, 61, 0.3);
  border-color: #ff9a3d;
}

.error-message {
  background: #ffebee;
  color: #c62828;
  padding: 15px;
  border-radius: 8px;
  margin-top: 20px;
  text-align: center;
}

.success-message {
  background: white;
  padding: 40px;
  border-radius: 15px;
  box-shadow: 0 8px 25px rgba(255, 154, 61, 0.3);
  text-align: center;
  border: 1px solid rgba(255, 154, 61, 0.1);
}

.success-icon {
  font-size: 60px;
  color: #4caf50;
  margin-bottom: 20px;
}

.success-message h3 {
  color: #ff6b6b;
  margin-bottom: 15px;
}

.success-message p {
  color: #666;
  margin-bottom: 10px;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .application-guide {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>