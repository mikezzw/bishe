<template>
  <div class="app">
    <header class="header" v-if="!$route.meta.hideLayout">
      <div class="container">
        <h1 class="logo">流浪动物云领养系统</h1>
        <nav class="nav" v-if="!user || user.user_type !== 'shelter'">
          <router-link to="/" class="nav-item">首页</router-link>
          <router-link to="/animals" class="nav-item">动物列表</router-link>
          <router-link to="/adoptions" class="nav-item">领养申请</router-link>
          <router-link to="/cloud-pets" class="nav-item">我的云养</router-link>
          <router-link to="/shelters" class="nav-item">动物基地</router-link>
          <router-link to="/community" class="nav-item">社区</router-link>
          <template v-if="user">
            <router-link to="/profile" class="nav-item">{{ user.username }}</router-link>
            <a href="#" class="nav-item" @click="logout">退出登录</a>
          </template>
          <template v-else>
            <router-link to="/login" class="nav-item">登录</router-link>
            <router-link to="/register" class="nav-item">注册</router-link>
          </template>
        </nav>
        <nav class="nav" v-else>
          <router-link to="/shelter/dashboard" class="nav-item">基地概览</router-link>
          <router-link to="/profile" class="nav-item">{{ user.username }}</router-link>
          <a href="#" class="nav-item" @click="logout">退出登录</a>
        </nav>
      </div>
    </header>
    <main class="main" :class="{ 'full-screen': $route.meta.hideLayout }">
      <div class="container" v-if="!$route.meta.hideLayout">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
      <router-view v-else />
    </main>
    <footer class="footer" v-if="!$route.meta.hideLayout">
      <div class="container">
        <p>© 2026 流浪动物云领养系统</p>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user'))
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.user = null
      this.$router.push('/')
    }
  },
  watch: {
    $route(to, from) {
      // 页面切换时更新用户信息
      this.user = JSON.parse(localStorage.getItem('user'))
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Arial, sans-serif;
  line-height: 1.6;
  color: #333;
  background: linear-gradient(135deg, #fff8f0 0%, #ffeaa7 100%);
  background-attachment: fixed;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.header {
  background: linear-gradient(rgba(255, 154, 61, 0.5), rgba(255, 107, 107, 0.5)),
              url('@/image/R-C.jpg') center/cover no-repeat;
  color: white;
  padding: 40px 0;
  box-shadow: 0 4px 15px rgba(255, 154, 61, 0.3);
  text-align: center;
}


.logo {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 10px;
  text-align: center;
}

.nav {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.nav-item {
  color: white;
  text-decoration: none;
  font-size: 16px;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.nav-item:hover {
  background: linear-gradient(135deg, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0.1) 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.main {
  padding: 40px 0;
  min-height: 600px;
}

.main.full-screen {
  padding: 0;
  min-height: 100vh;
}

.footer {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff9a3d 100%);
  color: white;
  padding: 20px 0;
  text-align: center;
  margin-top: 40px;
  box-shadow: 0 -4px 15px rgba(255, 107, 107, 0.2);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
