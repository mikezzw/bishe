<template>
  <div class="community">
    <div class="container">
      <div class="community-header">
        <h2>社区交流</h2>
        <div class="header-buttons">
          <button class="btn btn-secondary" @click="loadPosts(true)">
            <i class="btn-icon">🔄</i>
            刷新
          </button>
          <button class="btn btn-primary" @click="openPostModal">
            <i class="btn-icon">📝</i>
            发布帖子
          </button>
        </div>
      </div>
      
      <!-- 分类筛选 -->
      <div class="category-filter">
        <button 
          v-for="category in categories" 
          :key="category.id"
          class="category-btn" 
          :class="{ active: selectedCategory === category.id }"
          @click="selectCategory(category.id)"
        >
          {{ category.name }}
        </button>
      </div>
      
      <!-- 帖子列表 -->
      <div class="posts-list">
        <div v-if="posts.length === 0 && !loading" class="no-posts">
          <p>暂无帖子数据</p>
          <p>错误信息: {{ error }}</p>
        </div>
        
        <div class="post-card" v-for="post in filteredPosts" :key="post.id">
          <div class="post-header">
            <div class="user-info">
              <div class="user-avatar">{{ post.author.charAt(0) }}</div>
              <div>
                <h3>{{ post.title }}</h3>
                <p class="post-meta">
                  {{ post.author }} · {{ formatDate(post.created_at) }} · {{ getCategoryName(post.category_id) }}
                </p>
              </div>
            </div>
            <div class="post-stats">
              <span class="stat-item" @click="toggleLike(post.id)">
                <i class="stat-icon" :class="{ 'liked': post.liked }">❤️</i>
                {{ post.likes }}
              </span>
              <span class="stat-item">
                <i class="stat-icon">💬</i>
                {{ post.comments_count }}
              </span>
            </div>
          </div>
          <div class="post-content">
            <p>{{ post.content.substring(0, 150) }}{{ post.content.length > 150 ? '...' : '' }}</p>
            <img v-if="post.image" :src="post.image" :alt="post.title" class="post-image">
          </div>
          <div class="post-actions">
            <button class="btn btn-secondary" @click="viewPostDetails(post)">
              查看详情
            </button>
          </div>
        </div>
      </div>
      
      <!-- 帖子详情模态框 -->
      <div class="modal" v-if="showPostModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>{{ editingPost ? '编辑帖子' : '发布帖子' }}</h2>
            <button class="btn-close" @click="closePostModal">×</button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitPost">
              <div class="form-group">
                <label for="post-title">标题</label>
                <input type="text" id="post-title" v-model="currentPost.title" required>
              </div>
              <div class="form-group">
                <label for="post-category">分类</label>
                <select id="post-category" v-model="currentPost.category_id" required>
                  <option v-for="category in categories" :key="category.id" :value="category.id">
                    {{ category.name }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label for="post-content">内容</label>
                <textarea id="post-content" v-model="currentPost.content" rows="5" required></textarea>
              </div>
              <div class="form-group">
                <label for="post-image">图片链接（可选）</label>
                <input type="text" id="post-image" v-model="currentPost.image" placeholder="输入图片URL">
              </div>
              <div class="form-actions">
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  {{ loading ? '提交中...' : '发布' }}
                </button>
                <button type="button" class="btn btn-secondary" @click="closePostModal">取消</button>
              </div>
            </form>
          </div>
        </div>
      </div>
      
      <!-- 帖子详情查看模态框 -->
      <div class="modal" v-if="showPostDetailModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>{{ selectedPost.title }}</h2>
            <button class="btn-close" @click="closePostDetailModal">×</button>
          </div>
          <div class="modal-body">
            <div class="post-detail">
              <div class="post-detail-header">
                <div class="user-info">
                  <div class="user-avatar">{{ selectedPost.author.charAt(0) }}</div>
                  <div>
                    <p class="post-meta">
                      {{ selectedPost.author }} · {{ formatDate(selectedPost.created_at) }} · {{ getCategoryName(selectedPost.category_id) }}
                    </p>
                  </div>
                </div>
                <div class="post-stats">
                  <span class="stat-item" @click="toggleLike(selectedPost.id)">
                    <i class="stat-icon" :class="{ 'liked': selectedPost.liked }">❤️</i>
                    {{ selectedPost.likes }}
                  </span>
                  <span class="stat-item">
                    <i class="stat-icon">💬</i>
                    {{ selectedPost.comments_count }}
                  </span>
                </div>
              </div>
              <div class="post-detail-content">
                <p>{{ selectedPost.content }}</p>
                <img v-if="selectedPost.image" :src="selectedPost.image" :alt="selectedPost.title" class="post-detail-image">
              </div>
              
              <!-- 评论区 -->
              <div class="comments-section">
                <h3>评论 ({{ selectedPost.comments.length }})</h3>
                
                <!-- 评论列表 -->
                <div class="comments-list">
                  <div v-if="selectedPost.comments.length === 0" class="no-comments">
                    暂无评论，快来发表第一条评论吧！
                  </div>
                  <div v-else v-for="comment in selectedPost.comments" :key="comment.id" class="comment-item">
                    <div class="comment-header">
                      <div class="user-avatar small">{{ comment.author.charAt(0) }}</div>
                      <div>
                        <p class="comment-author">{{ comment.author }}</p>
                        <p class="comment-time">{{ formatDate(comment.created_at) }}</p>
                      </div>
                    </div>
                    <div class="comment-content">
                      {{ comment.content }}
                    </div>
                  </div>
                </div>
                
                <!-- 发表评论 -->
                <div class="comment-form">
                  <h4>发表评论</h4>
                  <form @submit.prevent="submitComment">
                    <div class="form-group">
                      <textarea v-model="newComment" rows="3" placeholder="写下你的评论..." required></textarea>
                    </div>
                    <div class="form-actions">
                      <button type="submit" class="btn btn-primary" :disabled="loading">
                        {{ loading ? '提交中...' : '发表评论' }}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
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
import { communityApi } from '@/api'

export default {
  name: 'Community',
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user') || '{}'),
      websocket: null,
      isConnected: false,
      posts: [],
      categories: [
        { id: 1, name: '领养分享' },
        { id: 2, name: '志愿活动' },
        { id: 3, name: '宠物护理' },
        { id: 4, name: '基地动态' },
        { id: 5, name: '其他' }
      ],
      selectedCategory: null,
      showPostModal: false,
      showPostDetailModal: false,
      editingPost: false,
      currentPost: {
        title: '',
        content: '',
        category_id: 1,
        image: ''
      },
      selectedPost: {
        id: '',
        title: '',
        content: '',
        author: '',
        category_id: 1,
        likes: 0,
        liked: false,
        comments_count: 0,
        created_at: '',
        comments: [],
        image: ''
      },
      newComment: '',
      loading: false,
      error: '',
      success: ''
    }
  },
  created() {
    // 确保用户信息是最新的
    this.user = JSON.parse(localStorage.getItem('user') || '{}');
    console.log('组件创建时的用户信息:', this.user);
  },
  mounted() {
    console.log('组件挂载，开始加载数据');
    this.loadPosts();
    this.connectWebSocket();
  },
  beforeUnmount() {
    this.disconnectWebSocket();
  },
  computed: {
    filteredPosts() {
      if (!this.selectedCategory) {
        return this.posts
      }
      return this.posts.filter(post => post.category_id === this.selectedCategory)
    }
  },
  methods: {
    connectWebSocket() {
      // 连接到WebSocket服务器
      const wsUrl = `ws://localhost:8000/ws/community/`;
      this.websocket = new WebSocket(wsUrl);
      
      this.websocket.onopen = () => {
        console.log('WebSocket连接已建立');
        this.isConnected = true;
        
        // 发送加入房间消息
        if (this.user.id) {
          this.websocket.send(JSON.stringify({
            type: 'join_room',
            user_id: this.user.id
          }));
        }
      };
      
      this.websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.handleWebSocketMessage(data);
      };
      
      this.websocket.onclose = () => {
        console.log('WebSocket连接已关闭');
        this.isConnected = false;
        // 5秒后尝试重新连接
        setTimeout(() => {
          if (this.$route.name === 'Community') {
            this.connectWebSocket();
          }
        }, 5000);
      };
      
      this.websocket.onerror = (error) => {
        console.error('WebSocket错误:', error);
        this.isConnected = false;
      };
    },
    
    disconnectWebSocket() {
      if (this.websocket) {
        this.websocket.close();
        this.websocket = null;
        this.isConnected = false;
      }
    },
    
    handleWebSocketMessage(data) {
      switch (data.type) {
        case 'new_post':
          this.addNewPost(data.post);
          break;
        case 'new_comment':
          this.addNewComment(data.comment);
          break;
        case 'post_like':
          this.updatePostLikes(data.post_id, data.likes);
          break;
        case 'user_joined':
          this.showNotification(data.message);
          break;
      }
    },
    
    addNewPost(post) {
      // 将新帖子添加到列表顶部
      this.posts.unshift({
        id: post.id,
        title: post.title,
        content: post.content,
        author: post.author,
        category_id: this.getCategoryIdByName(post.category),
        likes: post.likes,
        liked: false,
        comments_count: 0,
        created_at: post.created_at,
        showComments: false,
        comments: []
      });
      
      this.showNotification(`新帖子：${post.title}`);
    },
    
    addNewComment(comment) {
      const post = this.posts.find(p => p.id === comment.post_id);
      if (post) {
        post.comments.push({
          id: comment.id,
          content: comment.content,
          author: comment.author,
          created_at: comment.created_at
        });
        post.comments_count++;
        this.showNotification(`${comment.author} 评论了帖子`);
      }
    },
    
    updatePostLikes(postId, likes) {
      const post = this.posts.find(p => p.id === postId);
      if (post) {
        post.likes = likes;
      }
    },
    
    getCategoryNameById(categoryId) {
      const category = this.categories.find(c => c.id === categoryId);
      return category ? category.name : '其他';
    },
    
    getCategoryIdByName(categoryName) {
      // 处理中英文分类名称到ID的映射
      const categoryMap = {
        'adoption': 1,      // 领养分享
        '领养分享': 1,
        'experience': 2,    // 志愿活动
        '志愿活动': 2,
        'knowledge': 3,     // 宠物护理
        '宠物护理': 3,
        'help': 4,          // 基地动态
        '基地动态': 4,
        'other': 5,         // 其他
        '其他': 5,
        'test': 5           // 测试分类
      };
      
      // 如果是字符串，直接查找映射
      if (typeof categoryName === 'string') {
        const categoryId = categoryMap[categoryName.trim()];
        if (categoryId !== undefined) {
          console.log(`分类映射: '${categoryName}' -> ${categoryId}`);
          return categoryId;
        }
      }
      
      console.log(`未找到分类映射: '${categoryName}', 使用默认分类5`);
      // 默认返回其他分类
      return 5;
    },
    
    showNotification(message) {
      // 显示通知
      this.success = message;
      setTimeout(() => {
        this.success = '';
      }, 3000);
    },
    
    sendWebSocketMessage(message) {
      if (this.websocket && this.isConnected) {
        this.websocket.send(JSON.stringify(message));
      }
    },
    
    async loadPosts(force = false) {
      try {
        // 强制刷新时重新获取用户信息
        if (force) {
          this.user = JSON.parse(localStorage.getItem('user') || '{}');
        }
        
        // 检查用户认证
        const token = localStorage.getItem('token');
        console.log('用户认证信息:', {
          user: this.user,
          hasToken: !!token,
          tokenPreview: token ? token.substring(0, 20) + '...' : '无'
        });
        
        const response = await communityApi.getPosts()
        console.log('API响应完整结构:', response)
        console.log('response类型:', typeof response)
        console.log('response是否为对象:', typeof response === 'object')
        if (response && typeof response === 'object') {
          console.log('response的keys:', Object.keys(response))
        }
        
        // 由于axios拦截器已经提取了response.data，所以直接使用response
        let postsData = [];
        
        // 情况1: DRF分页格式 {count: 17, results: [...], next: ..., previous: ...}
        if (response && typeof response === 'object' && response.results) {
          postsData = response.results;
          console.log('✅ 从分页响应获取数据，共', postsData.length, '条');
          console.log('总记录数:', response.count);
        }
        // 情况2: 直接数组格式
        else if (Array.isArray(response)) {
          postsData = response;
          console.log('✅ 从数组响应获取数据，共', postsData.length, '条');
        } else {
          console.warn('⚠️ 未知的数据格式:', response);
          console.log('response内容:', response);
          postsData = [];
        }
        
        console.log('提取的帖子数据:', postsData);
        
        if (postsData && postsData.length > 0) {
          this.posts = postsData.map((post, index) => {
            console.log(`处理第${index + 1}个帖子:`, {
              id: post.id,
              title: post.title,
              category: post.category,
              author: post.author?.username
            });
            
            const categoryId = this.getCategoryIdByName(post.category);
            console.log(`分类映射结果: ${post.category} -> ${categoryId}`);
            
            return {
              id: post.id,
              title: post.title,
              content: post.content,
              author: post.author?.username || '未知用户',
              category_id: categoryId,
              likes: post.likes || 0,
              liked: false,
              comments_count: 0,
              created_at: post.created_at,
              showComments: false,
              comments: [],
              image: post.images && post.images.length > 0 ? post.images[0] : ''
            };
          });
          console.log('成功加载帖子数量:', this.posts.length);
          console.log('处理后的帖子数据:', this.posts);
        } else {
          console.log('没有获取到帖子数据，清空列表');
          this.posts = [];
        }
      } catch (error) {
        console.error('加载帖子失败:', error)
        console.error('错误详情:', {
          message: error.message,
          response: error.response,
          status: error.response?.status,
          data: error.response?.data
        })
        this.error = `加载帖子失败: ${error.response?.data?.message || error.message || '请稍后重试'}`
      }
    },
    
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    getCategoryName(categoryId) {
      const category = this.categories.find(c => c.id === categoryId)
      return category ? category.name : '未分类'
    },
    
    selectCategory(categoryId) {
      this.selectedCategory = this.selectedCategory === categoryId ? null : categoryId
    },
    
    openPostModal() {
      this.editingPost = false
      this.currentPost = {
        title: '',
        content: '',
        category_id: 1,
        image: ''
      }
      this.showPostModal = true
      this.error = ''
      this.success = ''
    },
    
    closePostModal() {
      this.showPostModal = false
    },
    
    async submitPost() {
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        // 首先通过REST API保存到数据库
        const postData = {
          title: this.currentPost.title,
          content: this.currentPost.content,
          category: this.getCategoryName(this.currentPost.category_id),
          images: this.currentPost.image ? [this.currentPost.image] : []
        };
        
        const apiResponse = await communityApi.createPost(postData);
        
        if (apiResponse.code === 200 || apiResponse.code === 201) {
          console.log('帖子已保存到数据库:', apiResponse.data);
          
          // 通过WebSocket发送新帖子消息给其他用户
          const postMessage = {
            type: 'new_post',
            post: {
              id: apiResponse.data.id,
              title: this.currentPost.title,
              content: this.currentPost.content,
              author: this.user.username || '匿名用户',
              category: this.getCategoryName(this.currentPost.category_id),
              likes: 0,
              created_at: new Date().toISOString()
            }
          };
          
          this.sendWebSocketMessage(postMessage);
        
          // 本地也添加帖子（用于立即显示）
          const newPost = {
            id: apiResponse.data.id,
            title: this.currentPost.title,
            content: this.currentPost.content,
            author: this.user.username || '匿名用户',
            category_id: this.currentPost.category_id,
            image: this.currentPost.image,
            likes: 0,
            liked: false,
            comments_count: 0,
            created_at: new Date().toISOString(),
            showComments: false,
            comments: []
          };
          
          this.posts.unshift(newPost);
          this.showPostModal = false;
          this.success = '帖子发布成功';
          
          // 重新加载帖子列表确保数据同步
          await this.loadPosts();
        } else {
          throw new Error(apiResponse.message || '发布失败');
        }
      } catch (error) {
        this.error = error.response?.data?.message || '发布失败，请检查网络连接';
      } finally {
        this.loading = false;
      }
    },
    
    toggleLike(postId) {
      const post = this.posts.find(p => p.id === postId);
      if (post) {
        post.liked = !post.liked;
        const newLikes = post.likes + (post.liked ? 1 : -1);
        
        // 通过WebSocket发送点赞消息
        const likeMessage = {
          type: 'like_post',
          post_id: postId,
          user_id: this.user.id
        };
        
        this.sendWebSocketMessage(likeMessage);
        
        // 本地更新（用于立即显示）
        post.likes = newLikes;
      }
    },
    
    viewPostDetails(post) {
      // 打开帖子详情模态框
      this.selectedPost = { ...post };
      this.showPostDetailModal = true;
      // 加载帖子评论
      this.loadComments(post.id);
    },
    
    closePostDetailModal() {
      // 关闭帖子详情模态框
      this.showPostDetailModal = false;
      this.newComment = '';
    },
    
    async loadComments(postId) {
      try {
        const response = await communityApi.getComments(postId);
        if (response.results && Array.isArray(response.results)) {
          this.selectedPost.comments = response.results.map(comment => ({
            id: comment.id,
            content: comment.content,
            author: comment.author?.username || '未知用户',
            created_at: comment.created_at
          }));
        } else if (Array.isArray(response)) {
          this.selectedPost.comments = response.map(comment => ({
            id: comment.id,
            content: comment.content,
            author: comment.author?.username || '未知用户',
            created_at: comment.created_at
          }));
        } else {
          this.selectedPost.comments = [];
        }
      } catch (error) {
        console.error('加载评论失败:', error);
        // 401错误时，不显示错误信息，只显示空评论列表
        if (error.response?.status === 401) {
          console.log('未登录，显示空评论列表');
        } else {
          this.error = '加载评论失败，请稍后重试';
        }
        this.selectedPost.comments = [];
      }
    },
    
    async submitComment() {
      if (!this.newComment.trim()) return;
      
      // 检查用户是否登录
      if (!this.user.id) {
        this.error = '请先登录后再发表评论';
        setTimeout(() => {
          this.error = '';
        }, 3000);
        return;
      }
      
      this.loading = true;
      this.error = '';
      this.success = '';
      
      try {
        const commentData = {
          content: this.newComment,
          post: this.selectedPost.id
        };
        
        const response = await communityApi.createComment(commentData);
        
        if (response.code === 200 || response.code === 201) {
          // 添加新评论到列表
          const newComment = {
            id: response.data.id,
            content: this.newComment,
            author: this.user.username || '匿名用户',
            created_at: new Date().toISOString()
          };
          
          this.selectedPost.comments.push(newComment);
          this.selectedPost.comments_count++;
          
          // 更新帖子列表中的评论数
          const post = this.posts.find(p => p.id === this.selectedPost.id);
          if (post) {
            post.comments_count++;
          }
          
          // 通过WebSocket发送新评论消息
          const commentMessage = {
            type: 'new_comment',
            comment: {
              id: response.data.id,
              content: this.newComment,
              author: this.user.username || '匿名用户',
              post_id: this.selectedPost.id,
              created_at: new Date().toISOString()
            }
          };
          
          this.sendWebSocketMessage(commentMessage);
          
          this.newComment = '';
          this.success = '评论发布成功';
          
          setTimeout(() => {
            this.success = '';
          }, 3000);
        } else {
          throw new Error(response.message || '评论失败');
        }
      } catch (error) {
        console.error('发表评论失败:', error);
        if (error.response?.status === 401) {
          this.error = '请先登录后再发表评论';
        } else {
          this.error = error.response?.data?.message || '评论失败，请检查网络连接';
        }
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
.community {
  padding: 40px 0;
  background: linear-gradient(135deg, #fff8f0 0%, #ffeaa7 100%);
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.community-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header-buttons {
  display: flex;
  gap: 10px;
}

.community-header h2 {
  margin: 0;
  font-size: 28px;
  color: #333;
}

.category-filter {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.category-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 20px;
  background-color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.category-btn:hover {
  background-color: #f5f5f5;
}

.category-btn.active {
  background: linear-gradient(135deg, #ff9a3d 0%, #ff6b6b 100%);
  color: white;
  border-color: #ff9a3d;
  box-shadow: 0 4px 10px rgba(255, 154, 61, 0.3);
}

.posts-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.no-posts {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.no-posts p {
  margin: 10px 0;
  color: #666;
}

.post-card {
  background: linear-gradient(135deg, #ffffff 0%, #fff5e6 100%);
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(255, 154, 61, 0.2);
  padding: 20px;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 154, 61, 0.1);
}

.post-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 15px 40px rgba(255, 154, 61, 0.4);
  border-color: rgba(255, 154, 61, 0.3);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.user-info {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  flex: 1;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff9a3d 0%, #ff6b6b 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
  flex-shrink: 0;
  box-shadow: 0 4px 10px rgba(255, 154, 61, 0.3);
}

.post-header h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
  color: #ff6b6b;
  background: linear-gradient(135deg, #ff6b6b 0%, #ff9a3d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.post-meta {
  margin: 0;
  font-size: 12px;
  color: #666;
}

.post-stats {
  display: flex;
  gap: 15px;
  align-items: center;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
  transition: all 0.3s ease;
}

.stat-item:hover {
  color: #ff6b6b;
  transform: scale(1.1);
}

.stat-icon {
  font-size: 16px;
}

.stat-icon.liked {
  color: #f44336;
}

.post-content {
  margin-bottom: 20px;
  line-height: 1.5;
  color: #333;
}

.post-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 4px;
  margin-top: 15px;
}

.post-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

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

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-size: 14px;
  font-weight: bold;
  color: #555;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
}

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

.btn-icon {
  font-size: 16px;
}

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

/* 帖子详情样式 */
.post-detail {
  padding: 20px 0;
}

.post-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.post-detail-content {
  margin-bottom: 30px;
  line-height: 1.6;
  color: #333;
}

.post-detail-image {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
  border-radius: 8px;
  margin-top: 15px;
}

/* 评论区样式 */
.comments-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.comments-section h3 {
  margin-bottom: 20px;
  color: #333;
}

.comments-list {
  margin-bottom: 30px;
}

.no-comments {
  text-align: center;
  padding: 30px;
  background-color: #f9f9f9;
  border-radius: 8px;
  color: #666;
}

.comment-item {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.user-avatar.small {
  width: 30px;
  height: 30px;
  font-size: 12px;
}

.comment-author {
  margin: 0;
  font-weight: bold;
  color: #333;
  font-size: 14px;
}

.comment-time {
  margin: 0;
  font-size: 12px;
  color: #999;
}

.comment-content {
  color: #333;
  line-height: 1.5;
}

/* 评论表单样式 */
.comment-form {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.comment-form h4 {
  margin-bottom: 15px;
  color: #333;
}

.comment-form textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  resize: vertical;
  min-height: 100px;
}

@media (max-width: 768px) {
  .community-header {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .category-filter {
    justify-content: center;
  }
  
  .posts-list {
    grid-template-columns: 1fr;
  }
  
  .post-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .post-stats {
    justify-content: flex-end;
  }
  
  .modal-content {
    width: 95%;
    max-height: 95vh;
  }
  
  .post-detail-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .post-stats {
    justify-content: flex-end;
  }
}
</style>