<template>
  <div class="home">
    <!-- 错误提示 -->
    <div class="error-alert" v-if="errorMessage">
      <div class="alert-content">
        <span class="alert-icon">⚠️</span>
        <span class="alert-message">{{ errorMessage }}</span>
        <button class="alert-close" @click="clearError">×</button>
      </div>
    </div>
    
    <section class="hero">
      <div class="container">
        <h2>欢迎来到流浪动物云领养系统</h2>
        <p>帮助流浪动物找到温暖的家，让每一个生命都能被温柔以待</p>
        <div class="hero-buttons">
          <router-link to="/animals" class="btn btn-primary">浏览可领养动物</router-link>
          <router-link to="/adoption/recommend" class="btn btn-primary">智能推荐领养</router-link>
        </div>
      </div>
    </section>
    
    <section class="features">
      <div class="container">
        <h3>核心功能</h3>
        <div class="features-grid">
          <div class="feature-item">
            <h4>线上领养流程</h4>
            <p>从申请提交到审核反馈，全流程线上操作，方便快捷</p>
          </div>
          <div class="feature-item">
            <h4>性格精准匹配</h4>
            <p>基于OCEAN人格量表，为您匹配最适合的动物伙伴</p>
          </div>
          <div class="feature-item">
            <h4>品种智能识别</h4>
            <p>利用AI技术，自动识别动物品种，提供准确信息</p>
          </div>
          <div class="feature-item">
            <h4>互动交流社区</h4>
            <p>分享领养经验，交流养护知识，共建爱心社区</p>
          </div>
          <div class="feature-item">
            <h4>志愿服务机会</h4>
            <p>参与动物救助活动，贡献爱心力量，成为志愿者</p>
            <router-link to="/volunteer/activities" class="btn btn-secondary-small">查看活动</router-link>
          </div>
          <div class="feature-item">
            <h4>基地互动申请</h4>
            <p>申请探访、志愿服务或寄养，与动物近距离接触</p>
            <router-link to="/shelters" class="btn btn-secondary-small">查看基地</router-link>
          </div>
        </div>
      </div>
    </section>
    
    <section class="latest-animals">
      <div class="container">
        <h3>最新可领养动物</h3>
        <div class="animals-grid" v-if="animals.length > 0">
          <div class="animal-card" v-for="animal in animals" :key="animal.id">
            <router-link :to="`/animal/${animal.id}`">
              <img v-if="animal.images && animal.images.length > 0" :src="animal.images[0]" :alt="animal.name" class="animal-image">
              <img v-else src="https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=cute%20animal%20portrait&image_size=square" :alt="animal.name" class="animal-image">
              <h4>{{ animal.name }}</h4>
              <p class="animal-info">{{ animal.species === 'cat' ? '猫' : animal.species === 'dog' ? '狗' : '其他' }} · {{ animal.breed }} · {{ animal.age }}个月</p>
              <p class="animal-desc">{{ animal.description.substring(0, 100) }}...</p>
              <button class="btn btn-secondary">查看详情</button>
            </router-link>
          </div>
        </div>
        <div class="no-animals" v-else>
          <p>暂无可领养动物</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { animalApi } from '@/api'

export default {
  name: 'Home',
  data() {
    return {
      animals: [],
      errorMessage: ''
    }
  },
  watch: {
    '$route.query.error'(newVal) {
      if (newVal) {
        this.errorMessage = newVal
      }
    }
  },

  mounted() {
    this.getLatestAnimals()
  },
  methods: {
    clearError() {
      this.errorMessage = ''
      // 清除URL中的错误参数
      if (this.$route.query.error) {
        this.$router.replace({ query: {} })
      }
    },
    async getLatestAnimals() {
      try {
        console.log('开始获取可领养动物列表...')
        // 使用统一的API配置，避免axios拦截器问题
        const response = await animalApi.getAvailableAnimals()
        console.log('获取可领养动物列表响应:', response)
        console.log('响应类型:', typeof response)
        console.log('响应是否为对象:', typeof response === 'object')
        
        // 处理后端API返回格式 {code: 200, message: '获取可领养动物成功', data: [...]}
        let animalsData = [];
        if (response && typeof response === 'object' && response.data) {
          // 后端API格式
          animalsData = response.data;
          console.log('✅ 从后端响应获取可领养动物数据，共', animalsData.length, '条');
        } else if (Array.isArray(response)) {
          // 直接数组格式
          animalsData = response;
          console.log('✅ 从数组响应获取可领养动物数据，共', animalsData.length, '条');
        } else {
          console.error('⚠️ 未知的响应格式:', response);
          animalsData = [];
        }
        
        if (animalsData.length > 0) {
          this.animals = animalsData.slice(0, 4); // 只显示前4个
          console.log('更新后的animals:', this.animals);
        }
      } catch (error) {
        console.error('获取可领养动物列表失败:', error)
      }
    }
  }
}
</script>

<style scoped>
/* 错误提示样式 */
.error-alert {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  max-width: 90%;
  width: 500px;
}

.alert-content {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  gap: 12px;
}

.alert-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.alert-message {
  flex: 1;
  color: #856404;
  font-weight: 500;
}

.alert-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #856404;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.alert-close:hover {
  background-color: rgba(133, 100, 4, 0.1);
}

/* 其他原有样式保持不变 */
.hero {
  background: linear-gradient(rgba(255, 154, 61, 0.5), rgba(255, 107, 107, 0.5)),
              url('@/image/fengmian.jpg') center/cover no-repeat;
  color: white;
  padding: 80px 0;
  text-align: center;
  box-shadow: 0 4px 20px rgba(255, 154, 61, 0.4);
}

.hero h2 {
  font-size: 36px;
  margin-bottom: 20px;
}

.hero-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 30px;
}

.hero-buttons .btn {
  min-width: 200px;
  text-align: center;
}

.hero p {
  font-size: 18px;
  margin-bottom: 30px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.btn {
  display: inline-block;
  padding: 10px 20px;
  border-radius: 4px;
  text-decoration: none;
  font-size: 16px;
  transition: background-color 0.3s;
}

.btn-primary {
  background: linear-gradient(135deg, #ffffff 0%, #fff5e6 100%);
  color: #ff6b6b;
  font-weight: bold;
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 15px rgba(255, 255, 255, 0.3);
}

.btn-primary:hover {
  background: linear-gradient(135deg, #fff5e6 0%, #ffffff 100%);
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(255, 255, 255, 0.5);
}

.btn-secondary {
  background: linear-gradient(135deg, #ff9a3d 0%, #ff6b6b 100%);
  color: white;
  border: none;
  cursor: pointer;
  padding: 8px 16px;
  font-size: 14px;
  box-shadow: 0 4px 10px rgba(255, 154, 61, 0.3);
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff9a3d 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(255, 107, 107, 0.4);
}



.btn-secondary-small {
  background: linear-gradient(135deg, #ffcc99 0%, #ff9a3d 100%);
  color: white;
  border: none;
  padding: 8px 16px;
  font-size: 14px;
  border-radius: 6px;
  margin-top: 10px;
  display: inline-block;
  transition: all 0.3s ease;
}

.btn-secondary-small:hover {
  background: linear-gradient(135deg, #ff9a3d 0%, #ff6b6b 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 154, 61, 0.4);
}

.features {
  padding: 60px 0;
  background: linear-gradient(135deg, #fff8f0 0%, #ffeaa7 50%, #fff8f0 100%);
  margin: 0 auto;

}

.features h3 {
  text-align: center;
  font-size: 28px;
  margin-bottom: 40px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;

}

.feature-item {
  background: linear-gradient(135deg, #ffffff 0%, #fff5e6 100%);
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(255, 154, 61, 0.2);
  text-align: center;
  border: 1px solid rgba(255, 154, 61, 0.1);
  transition: all 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 35px rgba(255, 154, 61, 0.3);
}

.feature-item h4 {
  font-size: 20px;
  margin-bottom: 15px;
  color: #ff6b6b;
  background: linear-gradient(135deg, #ff6b6b 0%, #ff9a3d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.latest-animals {
  padding: 60px 0;
}

.latest-animals h3 {
  text-align: center;
  font-size: 28px;
  margin-bottom: 40px;
}

.animals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
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
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 15px 40px rgba(255, 154, 61, 0.4);
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
  border: 1px dashed rgba(255, 154, 61, 0.3);
}
</style>
