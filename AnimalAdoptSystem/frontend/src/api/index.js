import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    // 不再直接跳转，让组件自己处理401错误
    return Promise.reject(error)
  }
)

// 动物相关API
export const animalApi = {
  // 获取动物列表
  getAnimals: (params) => api.get('/animals/', { params }),
  
  // 获取可领养动物列表
  getAvailableAnimals: () => api.get('/animals/available/'),
  
  // 获取动物详情
  getAnimalDetail: (id) => api.get(`/animals/${id}/`),
  
  // 搜索动物
  searchAnimals: (query) => api.get('/animals/search/', { params: query })
}

// 用户相关API
export const userApi = {
  // 登录
  login: (data) => api.post('/users/login/', data),
  
  // 注册
  register: (data) => api.post('/users/register/', data),
  
  // 获取用户信息
  getUserInfo: () => api.get('/users/profile/'),
  
  // 修改密码
  changePassword: (data) => api.post('/users/change-password/', data)
}

// 领养相关API
export const adoptionApi = {
  // 申请领养
  applyAdoption: (data) => api.post('/adoptions/applications/', data),
  
  // 获取我的领养申请
  getMyApplications: () => api.get('/adoptions/applications/my-applications/'),
  
  // 获取领养详情
  getAdoptionDetail: (id) => api.get(`/adoptions/applications/${id}/`)
}

// 基地相关API
export const shelterApi = {
  // 获取基地列表
  getShelters: (params) => api.get('/shelters/', { params }),
  
  // 获取基地详情
  getShelterDetail: (id) => api.get(`/shelters/${id}/`),
  
  // 搜索基地
  searchShelters: (query) => api.get('/shelters/', { params: query }),
  
  // 提交互动申请
  submitInteraction: (data) => api.post('/shelters/interactions/', data),
  
  // 获取互动申请列表
  getInteractions: () => api.get('/shelters/interactions/'),
  
  // 获取基地的互动申请
  getShelterInteractions: (shelterId) => api.get(`/shelters/${shelterId}/interactions/`),
  
  // 基地活动相关API
  getShelterActivities: (shelterId) => api.get(`/shelters/${shelterId}/activities/`),
  createShelterActivity: (shelterId, data) => api.post(`/shelters/${shelterId}/activities/`, data),
  updateShelterActivity: (shelterId, activityId, data) => api.put(`/shelters/${shelterId}/activities/${activityId}/`, data),
  deleteShelterActivity: (shelterId, activityId) => api.delete(`/shelters/${shelterId}/activities/${activityId}/`)
}

// 社区相关API
export const communityApi = {
  // 获取帖子列表
  getPosts: (params) => api.get('/community/posts/', { params }),
  
  // 创建帖子
  createPost: (data) => api.post('/community/posts/', data),
  
  // 获取帖子详情
  getPostDetail: (id) => api.get(`/community/posts/${id}/`),
  
  // 点赞帖子
  likePost: (postId) => api.post(`/community/posts/${postId}/like/`),
  
  // 取消点赞
  unlikePost: (postId) => api.post(`/community/posts/${postId}/unlike/`),
  
  // 获取评论列表
  getComments: (postId) => api.get(`/community/comments/`, { params: { post: postId } }),
  
  // 创建评论
  createComment: (data) => api.post('/community/comments/', data),
  
  // 删除评论
  deleteComment: (id) => api.delete(`/community/comments/${id}/`),
  
  // 获取通知
  getNotifications: () => api.get('/community/notifications/'),
  
  // 标记通知为已读
  markNotificationRead: (id) => api.patch(`/community/notifications/${id}/`, { is_read: true })
}

// 志愿者相关API
export const volunteerApi = {
  // 获取志愿者活动列表
  getActivities: (params) => api.get('/volunteers/activities/', { params }),
  
  // 报名志愿者活动
  registerActivity: (activityId) => api.post(`/volunteers/activities/${activityId}/register/`),
  
  // 取消报名
  cancelRegistration: (activityId) => api.post(`/volunteers/activities/${activityId}/cancel/`),
  
  // 获取我的参与记录
  getMyParticipations: () => api.get('/volunteers/participations/my-participations/')
}

export default api