<template>
  <div class="smart-recommend">
    <div class="container">
      <h2>智能领养推荐</h2>
      
      <!-- 推荐引导区域 -->
      <div class="recommend-guide">
        <div class="guide-header">
          <i class="guide-icon">🎯</i>
          <h3>个性化领养建议</h3>
        </div>
        <div class="guide-content">
          <p>为了帮您找到最合适的动物伙伴，我们提供两种选择：</p>
          <div class="options">
            <div class="option-card" :class="{selected: selectedOption === 'test'}" @click="selectOption('test')">
              <div class="option-icon">🧠</div>
              <h4>性格测试推荐</h4>
              <p>通过5分钟性格测试，基于OCEAN人格模型为您精准匹配最适合的动物</p>
              <div class="benefits">
                <span class="benefit-tag">精准匹配</span>
                <span class="benefit-tag">科学依据</span>
                <span class="benefit-tag">提高成功率</span>
              </div>
            </div>
            
            <div class="option-card" :class="{selected: selectedOption === 'browse'}" @click="selectOption('browse')">
              <div class="option-icon">🐾</div>
              <h4>自由浏览选择</h4>
              <p>直接浏览所有可领养动物，根据个人喜好自由选择</p>
              <div class="benefits">
                <span class="benefit-tag">灵活选择</span>
                <span class="benefit-tag">快速决策</span>
                <span class="benefit-tag">无需测试</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 性格测试区域 -->
      <div v-if="selectedOption === 'test'" class="personality-section">
        <div class="section-header">
          <h3>性格匹配测试</h3>
          <p>请诚实地回答以下问题，我们将基于您的答案推荐最适合的动物伙伴</p>
        </div>
        
        <div v-if="!testCompleted" class="personality-test-container">
          <PersonalityTest @match-calculated="handleMatchResult" />
          
          <div class="test-actions">
            <button @click="skipToBrowse" class="btn btn-secondary">跳过测试，直接浏览</button>
          </div>
        </div>
        
        <!-- 测试结果显示和推荐 -->
        <div v-else class="recommendation-results">
          <div class="match-summary">
            <div class="match-score">
              <div class="score-circle">
                <span class="score-number">{{ recommendedAnimals.length > 0 ? Math.round(Math.max(...recommendedAnimals.map(a => a.match_score))) : matchResult.match_percentage }}%</span>
              </div>
              <h4>性格匹配度</h4>
              <p>{{ matchResult.match_reason }}</p>
            </div>
          </div>
          
          <div class="recommended-animals">
            <h4>为您推荐的动物</h4>
            <div class="animals-grid">
              <div v-for="animal in recommendedAnimals" :key="animal.id" class="animal-card">
                <img :src="animal.images[0] || 'https://via.placeholder.com/300x200?text=动物图片'" :alt="animal.name" class="animal-image">
                <div class="animal-info">
                  <h5>{{ animal.name }}</h5>
                  <p class="animal-breed">{{ animal.breed }} · {{ animal.age }}个月</p>
                  <p class="match-indicator">匹配度: {{ animal.match_score }}%</p>
                  <router-link :to="`/adoption/apply/${animal.id}`" class="btn btn-primary">申请领养</router-link>
                </div>
              </div>
            </div>
          </div>
          
          <div class="additional-options">
            <button @click="resetTest" class="btn btn-outline">
              <span class="btn-icon">🔄</span>
              重新测试
            </button>
            <router-link to="/animals" class="btn btn-secondary">
              <span class="btn-icon">🐾</span>
              浏览所有动物
            </router-link>
            <button @click="skipToBrowse" class="btn btn-primary">
              <span class="btn-icon">➡️</span>
              直接浏览
            </button>
          </div>
        </div>
      </div>
      
      <!-- 自由浏览区域 -->
      <div v-if="selectedOption === 'browse'" class="browse-section">
        <div class="section-header">
          <h3>自由浏览可领养动物</h3>
          <p>以下是目前所有可领养的动物，您可以根据个人喜好进行选择</p>
        </div>
        
        <div v-if="animals.length > 0" class="animals-grid">
          <div v-for="animal in animals" :key="animal.id" class="animal-card">
            <img :src="animal.images[0] || 'https://via.placeholder.com/300x200?text=动物图片'" :alt="animal.name" class="animal-image">
            <div class="animal-info">
              <h5>{{ animal.name }}</h5>
              <p class="animal-breed">{{ animal.breed }} · {{ animal.age }}个月</p>
              <p class="animal-description">{{ animal.description.substring(0, 100) }}...</p>
              <router-link :to="`/adoption/apply/${animal.id}`" class="btn btn-primary">申请领养</router-link>
            </div>
          </div>
        </div>
        
        <div v-else class="no-animals">
          <p>暂无可领养的动物</p>
        </div>
        
        <div class="back-to-options">
          <button @click="selectedOption = ''" class="btn btn-outline">返回选择页面</button>
        </div>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-overlay">
        <div class="spinner"></div>
        <p>正在加载数据...</p>
      </div>
      
      <!-- 错误提示 -->
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script>
import PersonalityTest from '@/components/PersonalityTest.vue'

export default {
  name: 'SmartRecommend',
  components: {
    PersonalityTest
  },
  data() {
    return {
      selectedOption: '',
      testCompleted: false,
      matchResult: null,
      recommendedAnimals: [],
      animals: [],
      loading: false,
      error: ''
    }
  },
  mounted() {
    this.loadAvailableAnimals()
  },
  methods: {
    selectOption(option) {
      this.selectedOption = option
      this.testCompleted = false
      this.matchResult = null
      this.recommendedAnimals = []
      this.error = ''
    },
    
    handleMatchResult(result) {
      this.matchResult = result
      this.testCompleted = true
      this.getRecommendedAnimals()
    },
    
    async getRecommendedAnimals() {
      this.loading = true
      this.error = ''
      
      try {
        console.log('🚀 开始获取推荐动物...')
        console.log('用户得分:', this.matchResult.scores)
        
        // 首先获取所有可领养的动物列表
        const animalsResponse = await this.$axios.get('/animals/?status=available')
        console.log('📡 动物列表API响应:', animalsResponse)
        
        let animals = []
        if (animalsResponse.data && animalsResponse.data.results) {
          animals = animalsResponse.data.results
        } else if (animalsResponse.results) {
          animals = animalsResponse.results
        } else if (Array.isArray(animalsResponse)) {
          animals = animalsResponse
        } else {
          console.error('❌ 动物列表响应格式不正确')
          throw new Error('获取动物列表失败')
        }
        
        console.log('获取到动物数量:', animals.length)
        
        // 对每个动物计算匹配度
        const matchPromises = animals.map(async (animal) => {
          try {
            const response = await this.$axios.post('/animals/personality-match/', {
              animal_id: animal.id,
              user_scores: this.matchResult.scores
            })
            
            if (response.code === 200 && response.data) {
              return {
                id: animal.id,
                name: animal.name,
                breed: animal.breed,
                age: animal.age,
                images: animal.images || [],
                description: animal.description,
                match_score: response.data.match_percentage,
                match_reason: '性格匹配度高'
              }
            }
            return null
          } catch (error) {
            console.warn(`计算动物 ${animal.name} 的匹配度失败:`, error)
            return null
          }
        })
        
        // 等待所有匹配计算完成
        const matchResults = await Promise.all(matchPromises)
        
        // 过滤掉null值并按匹配度排序
        this.recommendedAnimals = matchResults
          .filter(Boolean)
          .sort((a, b) => b.match_score - a.match_score)
          .slice(0, 5) // 只取前5个匹配度最高的
        
        console.log('推荐动物数量:', this.recommendedAnimals.length)
        
        // 如果没有找到匹配的动物，给出友好提示
        if (this.recommendedAnimals.length === 0) {
          console.warn('⚠️ 未找到匹配的动物')
          this.error = '暂时没有找到与您性格匹配的动物，建议您：\n\n1. 调整性格测试的答案\n2. 稍后再试\n3. 直接浏览所有可领养动物'
        } else {
          console.log('✅ 成功获取推荐动物:', this.recommendedAnimals.length, '只')
          this.recommendedAnimals.forEach((animal, index) => {
            console.log(`${index + 1}. ${animal.name} - 匹配度: ${animal.match_score}%`)
          })
        }
        
        console.log('处理后的推荐动物数据:', this.recommendedAnimals)
        console.log('推荐动物数量:', this.recommendedAnimals.length)
        
      } catch (error) {
        console.error('获取推荐动物失败:', error)
        console.error('错误详情:', {
          message: error.message,
          stack: error.stack,
          response: error.response
        })
        
        // 根据错误类型提供更具体的错误信息
        if (error.response) {
          // 服务器返回了错误响应
          const status = error.response.status
          const data = error.response.data
          if (status === 400) {
            this.error = `参数错误: ${data.message || '请求参数不正确'}`
          } else if (status === 401) {
            this.error = '请先登录后再进行推荐匹配'
          } else if (status === 404) {
            this.error = '未找到可匹配的动物，请稍后再试'
          } else if (status >= 500) {
            this.error = `服务器错误 (${status})，请稍后重试`
          } else {
            this.error = `请求失败 (${status}): ${data.message || '未知错误'}`
          }
        } else if (error.request) {
          // 请求已发出但没有收到响应
          this.error = '网络连接失败，请检查网络连接或稍后重试'
        } else {
          // 其他错误
          this.error = error.message || '获取推荐动物失败，请稍后重试'
        }
        
        // 显示详细错误信息到控制台
        console.group('🚀 推荐匹配错误详情')
        console.error('错误消息:', error.message)
        console.error('错误堆栈:', error.stack)
        if (error.response) {
          console.error('响应状态:', error.response.status)
          console.error('响应数据:', error.response.data)
          console.error('响应头:', error.response.headers)
        }
        console.groupEnd()
      } finally {
        this.loading = false
      }
    },
    
    async loadAvailableAnimals() {
      this.loading = true
      this.error = ''
      
      try {
        console.log('开始获取可领养动物列表...')
        const response = await this.$axios.get('/animals/?status=available')
        
        console.log('收到响应:', response)
        console.log('响应类型:', typeof response)
        console.log('响应结构:', Object.keys(response || {}))
        
        // 增加详细的响应内容日志
        console.log('响应详细内容:', JSON.stringify(response, null, 2))
        
        // 由于axios拦截器返回的是response.data，直接处理数据
        let animalsData = []
        
        // 处理不同的响应格式
        if (response && response.data && response.data.results && Array.isArray(response.data.results)) {
          // 标准Axios响应格式，数据在data.results中
          console.log('检测到Axios响应格式，数据在data.results中')
          animalsData = response.data.results
        } else if (response && response.results && Array.isArray(response.results)) {
          // DRF分页格式
          console.log('检测到DRF分页格式')
          animalsData = response.results
        } else if (Array.isArray(response)) {
          // 直接数组格式
          console.log('检测到直接数组格式')
          animalsData = response
        } else if (response && response.data && Array.isArray(response.data)) {
          // 包含data字段的格式
          console.log('检测到data包装格式')
          animalsData = response.data
        } else if (response && response.id) {
          // 单个对象格式
          console.log('检测到单个对象格式')
          animalsData = [response]
        } else if (response && typeof response === 'object' && Object.keys(response).length > 0) {
          // 尝试检查对象是否包含数组结构
          console.log('检测到对象格式，尝试提取数据')
          // 检查是否有任何字段包含数组
          for (const key in response) {
            console.log('检查字段:', key, '类型:', typeof response[key], '是否数组:', Array.isArray(response[key]))
            if (Array.isArray(response[key])) {
              console.log('从', key, '字段提取数组数据，长度:', response[key].length)
              animalsData = response[key]
              break
            }
          }
          // 如果没有找到数组，尝试直接使用响应对象（可能是单个动物）
          if (animalsData.length === 0 && response.id) {
            console.log('尝试将对象作为单个动物处理')
            animalsData = [response]
          }
          // 特殊处理：如果响应对象本身看起来像动物数组
          else if (animalsData.length === 0 && Object.keys(response).length > 0) {
            console.log('尝试将对象作为动物数组处理')
            // 检查对象是否有数字键（可能是数组的索引）
            const hasNumericKeys = Object.keys(response).some(key => !isNaN(Number(key)))
            if (hasNumericKeys) {
              console.log('检测到数字键，转换为数组')
              animalsData = Object.values(response).filter(item => typeof item === 'object' && item !== null)
            }
          }
        } else {
          console.log('未知响应格式:', response)
          animalsData = []
        }
        
        console.log('解析后的动物数据:', animalsData)
        console.log('解析后的动物数据长度:', animalsData.length)
        this.animals = animalsData
        
      } catch (error) {
        console.error('获取动物列表失败:', error)
        console.error('错误详情:', {
          message: error.message,
          response: error.response,
          request: error.request
        })
        
        // 根据错误类型显示不同信息
        if (error.response) {
          // 服务器返回了错误响应
          this.error = `获取动物列表失败: ${error.response.status} ${error.response.statusText || ''}`
        } else if (error.request) {
          // 请求已发出但没有收到响应
          this.error = '网络连接失败，请检查网络连接或稍后重试'
        } else {
          // 其他错误
          this.error = error.message || '获取动物列表失败，请稍后重试'
        }
      } finally {
        this.loading = false
      }
    },
    
    skipToBrowse() {
      this.selectedOption = 'browse'
    },
    
    resetTest() {
      this.testCompleted = false
      this.matchResult = null
      this.recommendedAnimals = []
    }
  }
}
</script>

<style scoped>
.smart-recommend {
  padding: 40px 0;
  background: linear-gradient(135deg, #fff8f0 0%, #ffeaa7 100%);
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

h2 {
  text-align: center;
  margin-bottom: 40px;
  color: #333;
  font-size: 32px;
}

.recommend-guide {
  background: white;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.guide-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.guide-icon {
  font-size: 32px;
}

.guide-header h3 {
  margin: 0;
  color: #333;
  font-size: 24px;
}

.options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 25px;
  margin-top: 20px;
}

.option-card {
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fafafa;
}

.option-card:hover {
  border-color: #ff9a3d;
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(255, 154, 61, 0.2);
}

.option-card.selected {
  border-color: #ff9a3d;
  background: linear-gradient(135deg, #fff5e6 0%, #ffe0b2 100%);
  box-shadow: 0 8px 25px rgba(255, 154, 61, 0.3);
}

.option-icon {
  font-size: 40px;
  text-align: center;
  margin-bottom: 15px;
}

.option-card h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 20px;
  text-align: center;
}

.option-card p {
  margin: 0 0 20px 0;
  color: #666;
  line-height: 1.5;
  text-align: center;
}

.benefits {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.benefit-tag {
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
}

.section-header {
  text-align: center;
  margin-bottom: 30px;
}

.section-header h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 28px;
}

.section-header p {
  margin: 0;
  color: #666;
  font-size: 16px;
}

.personality-test-container {
  background: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.test-actions {
  text-align: center;
  margin-top: 20px;
}

.recommendation-results {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.match-summary {
  text-align: center;
  margin-bottom: 30px;
}

.score-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4caf50 0%, #8bc34a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.score-number {
  font-size: 32px;
  font-weight: bold;
  color: white;
}

.match-summary h4 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 24px;
}

.match-summary p {
  margin: 0;
  color: #666;
  font-size: 16px;
}

.recommended-animals h4 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 22px;
  text-align: center;
}

.animals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
  margin-bottom: 30px;
}

.animal-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
}

.animal-card:hover {
  transform: translateY(-5px);
}

.animal-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.animal-info {
  padding: 20px;
}

.animal-info h5 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 18px;
}

.animal-breed {
  margin: 0 0 10px 0;
  color: #666;
  font-size: 14px;
}

.animal-description {
  margin: 0 0 15px 0;
  color: #777;
  font-size: 14px;
  line-height: 1.4;
}

.match-indicator {
  margin: 0 0 15px 0;
  color: #4caf50;
  font-weight: 500;
  font-size: 14px;
}

.additional-options {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.browse-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.no-animals {
  text-align: center;
  padding: 40px;
  color: #666;
}

.back-to-options {
  text-align: center;
  margin-top: 30px;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #ff9a3d;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
  color: #c62828;
  padding: 20px;
  border-radius: 12px;
  text-align: left;
  margin: 20px 0;
  border-left: 4px solid #f44336;
  box-shadow: 0 4px 12px rgba(244, 67, 54, 0.2);
  white-space: pre-line;
}

.error-message:before {
  content: '⚠️ ';
  font-size: 18px;
  margin-right: 8px;
  vertical-align: middle;
}

.btn {
  padding: 12px 24px;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  border: none;
  font-weight: 500;
}

.btn-icon {
  font-size: 18px;
  line-height: 1;
}

.btn-primary {
  background: linear-gradient(135deg, #ff9a3d 0%, #ff6b6b 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(255, 154, 61, 0.3);
}

.btn-primary:hover {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff9a3d 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
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

.btn-outline {
  background: transparent;
  color: #ff9a3d;
  border: 2px solid #ff9a3d;
}

.btn-outline:hover {
  background: #ff9a3d;
  color: white;
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .options {
    grid-template-columns: 1fr;
  }
  
  .animals-grid {
    grid-template-columns: 1fr;
  }
  
  .additional-options {
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    width: 100%;
    text-align: center;
  }
}
</style>