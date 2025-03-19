<template>
  <el-card class="module-card" :body-style="{ padding: '0px' }" :class="cardClass">
    <div class="module-header">
      <div class="module-title">
        <el-icon class="module-icon"><component :is="icon" /></el-icon>
        <span>{{ title }}</span>
      </div>
      <div :class="statusClass">
        <span v-if="isCompleted" class="check-icon">
          <el-icon><Check /></el-icon>
        </span>
        <span v-else class="dot" />
      </div>
    </div>
    <div class="module-content">
      <div class="module-actions">
        <slot name="actions" :disabled="isInactive" />
      </div>
      <div class="module-info">
        <slot name="info" />
      </div>
    </div>
  </el-card>
</template>

<script>
export default {
  name: 'BaseModule',
  props: {
    title: {
      type: String,
      required: true
    },
    icon: {
      type: String,
      required: true
    },
    state: {
      type: String,
      default: 'active',
      validator: (value) => ['active', 'inactive'].includes(value)
    },
    data: {
      type: Object,
      default: () => ({ isCompleted: false })
    }
  },
  computed: {
    cardClass() {
      return {
        'active-module': this.state === 'active',
        'inactive-module': this.state === 'inactive'
      }
    },
    statusClass() {
      return {
        'status-indicator': true,
        'status-active': this.state === 'active',
        'status-completed': this.data.isCompleted
      }
    },
    isCompleted() {
      return this.data.isCompleted
    },
    isInactive() {
      return this.state === 'inactive' // 判断是否为 inactive 状态
    }
  }
}
</script>

<style scoped>
  /* 通用模块样式 */
  .module-card {
    margin-bottom: 10px;
    border-radius: 8px;
    overflow: hidden;
  }

  .active-module {
    border: 1px solid #67c23a;
  }

  .inactive-module {
    border: 1px solid #dcdfe6;
    opacity: 0.8;
  }

  .module-header {
    background-color: #f5f7fa;
    padding: 12px 15px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #ebeef5;
  }

  .module-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: bold;
  }

  .module-icon {
    color: #409eff;
  }

  .module-content {
    padding: 15px;
  }

  .module-actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 10px;
  }

  .module-info {
    color: #67c23a;
    font-size: 14px;
  }

  .status-indicator {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  }

  .status-active {
    border: 2px solid #67c23a;
  }

  .status-active .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: #67c23a;
  }

  .status-completed {
    border: 2px solid #67c23a;
    background-color: #67c23a;
  }

  .check-icon {
    color: white;
    font-size: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .inactive-module .el-button {
    background-color: #f5f7fa !important;
    border-color: #dcdfe6 !important;
    color: #c0c4cc !important;
    cursor: not-allowed !important;
  }
</style>
