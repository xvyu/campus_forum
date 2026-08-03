<template>
  <el-config-provider>
    <div id="campus-forum-app">
      <AppHeader />
      <main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
      <footer class="app-footer">
        <span>Campus Forum · 匿名分享，畅所欲言</span>
      </footer>
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
</script>

<style lang="scss" scoped>
#campus-forum-app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.main-content {
  flex: 1;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 16px;
}

.app-footer {
  text-align: center;
  padding: 24px 16px;
  font-size: 12px;
  color: #b4b2a9;
  border-top: 0.5px solid #e0e0e0;
  margin-top: 20px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
