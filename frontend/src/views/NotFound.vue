<script setup lang="ts">
// 404 页面占位
</script>

<template>
  <div class="not-found">
    <el-result icon="warning" title="404" sub-title="页面未找到">
      <template #extra>
        <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
      </template>
    </el-result>
  </div>
</template>

<style lang="scss" scoped>
.not-found {
  max-width: 600px;
  margin: 60px auto;
  text-align: center;
}
</style>
