<!-- frontend/src/components/PersonalityTest.vue -->
<template>
  <div class="personality-test">
    <h3>性格测试</h3>
    <p>请根据您的实际情况回答以下问题：</p>

    <div v-for="(question, index) in questions" :key="index" class="question">
      <p>{{ question.text }}</p>
      <div class="rating">
        <span v-for="score in [1,2,3,4,5]" :key="score"
              @click="setScore(index, score)"
              :class="{active: scores[questions[index].id] === score}">
          {{ score }}
        </span>
      </div>
    </div>

    <button @click="calculateMatch" :disabled="!isComplete">计算匹配度</button>
    
    <div v-if="loading" class="loading">正在计算匹配度...</div>
    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<script>
export default {
  name: 'PersonalityTest',
  props: {
    animalId: {
      type: [String, Number],
      default: null
    }
  },
  emits: ['match-calculated'],
  data() {
    return {
      questions: [
        {
          id: 'openness',
          text: '我喜欢尝试新的事物和体验'
        },
        {
          id: 'conscientiousness',
          text: '我做事很有条理和责任心'
        },
        {
          id: 'extraversion',
          text: '我喜欢社交活动，善于与人交往'
        },
        {
          id: 'agreeableness',
          text: '我对他人友善、富有同情心'
        },
        {
          id: 'neuroticism',
          text: '我容易感到焦虑和情绪波动'
        }
      ],
      scores: {},
      loading: false,
      error: ''
    }
  },
  computed: {
    isComplete() {
      return this.questions.length === Object.keys(this.scores).length
    }
  },
  methods: {
    setScore(questionIndex, score) {
      const questionId = this.questions[questionIndex].id
      // Vue 3中直接赋值即可触发响应式更新
      this.scores[questionId] = score
      this.error = ''
    },
    async calculateMatch() {
      if (!this.isComplete) return
      
      this.loading = true
      this.error = ''
      
      try {
        // 获取动物ID（优先使用传入的prop，否则从路由参数获取）
        const animalId = this.animalId || this.$route.params.id
        
        // 计算匹配度逻辑
        
        let response;
        if (animalId) {
          // 单个动物匹配
          response = await this.$axios.post(`/animals/${animalId}/personality_match/`, {
            user_scores: this.scores
          })
        } else {
          // 整体匹配（用于智能推荐）
          response = await this.$axios.post('/adoptions/matches/calculate-match/', {
            user_scores: this.scores
          })
        }
        
        // 处理API响应
        
        // 处理不同的响应格式
        let matchPercentage = 0
        let matchReason = ''
        
        if (animalId) {
          // 单个动物匹配响应格式
          if (response.code === 200 && response.data) {
            matchPercentage = response.data.match_percentage
            matchReason = response.data.animal_traits ? 
              `基于性格特征匹配: 开放性${response.data.animal_traits.openness}, 尽责性${response.data.animal_traits.conscientiousness}` : 
              '性格匹配成功'
          } else if (response.match_percentage) {
            matchPercentage = response.match_percentage
            matchReason = response.animal_traits ? 
              `基于性格特征匹配: 开放性${response.animal_traits.openness}, 尽责性${response.animal_traits.conscientiousness}` : 
              '性格匹配成功'
          } else {
            this.error = '匹配数据格式不正确'
            return
          }
        } else {
          // 整体匹配响应格式
          if (response.code === 200 && response.data && response.data.length > 0) {
            // 取第一个匹配结果作为代表
            const bestMatch = response.data[0]
            matchPercentage = Math.round(bestMatch.match_score * 100)
            matchReason = bestMatch.match_reason || '基于OCEAN人格模型的综合匹配'
          } else {
            this.error = '未找到匹配的动物'
            return
          }
        }
        
        const matchData = {
          match_percentage: Math.round(matchPercentage),
          match_reason: matchReason,
          scores: this.scores
        }
        this.$emit('match-calculated', matchData)
      } catch (error) {
        // 错误处理逻辑
        this.error = `匹配计算失败: ${error.response?.status || '网络错误'} - ${error.message}`
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.personality-test {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-top: 20px;
}

.question {
  margin-bottom: 20px;
}

.question p {
  margin-bottom: 10px;
  font-weight: bold;
}

.rating {
  display: flex;
  gap: 10px;
}

.rating span {
  width: 40px;
  height: 40px;
  border: 2px solid #ddd;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: bold;
}

.rating span:hover {
  border-color: #ff9a3d;
  background-color: #e8f5e8;
}

.rating span.active {
  border-color: #ff9a3d;
  background-color: #ff9a3d;
  color: white;
}

button {
  background-color: #ff9a3d;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 20px;
  transition: background-color 0.3s;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  background-color: #45a049;
}

.loading, .error {
  margin-top: 15px;
  padding: 10px;
  border-radius: 4px;
}

.loading {
  background-color: #e3f2fd;
  color: #1976d2;
}

.error {
  background-color: #ffebee;
  color: #c62828;
}
</style>
