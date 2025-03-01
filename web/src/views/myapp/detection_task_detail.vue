<template>
  <div class="container">
    <!-- Basic Config Module -->
    <el-card class="module-card" :body-style="{ padding: '0px' }" :class="{ 'active-module': true }">
      <div class="module-header">
        <div class="module-title">
          <el-icon class="module-icon"><Setting /></el-icon>
          <span>Basic Config</span>
        </div>
        <div :class="getStatusClass('active')">
          <span v-if="isCompleted('active')" class="check-icon">
            <el-icon><Check /></el-icon>
          </span>
          <span v-else class="dot"></span>
        </div>
      </div>
      <div class="module-content">
        <div class="module-actions">
          <router-link :to="'/myapp/basic_edit/'+this.$route.params.id" class="link-type">
            <el-button type="success" size="small">Edit Basic Config</el-button>
          </router-link>
        </div>
      </div>
    </el-card>

    <!-- Arrow -->
    <div class="arrow-container">
      <div class="arrow"></div>
    </div>

    <!-- API Discovery Module -->
    <el-card class="module-card" :body-style="{ padding: '0px' }" :class="{ 'active-module': true }">
      <div class="module-header">
        <div class="module-title">
          <el-icon class="module-icon"><Document /></el-icon>
          <span>API Discovery</span>
        </div>
        <div :class="getStatusClass('active')">
          <span v-if="isCompleted('active')" class="check-icon">
            <el-icon><Check /></el-icon>
          </span>
          <span v-else class="dot"></span>
        </div>
      </div>
      <div class="module-content">
        <div class="module-actions">
          <el-button
            type="primary"
            size="small"
            :loading="apiDiscoveryLoading"
            @click="startApiDiscovery"
          >
            Start API Discovery
          </el-button>
          <router-link :to="'/myapp/api_discovery_result/'+this.$route.params.id" class="link-type">
            <el-button
              v-if="apiDiscoveryCompleted"
              type="warning"
              size="small"
              @click="showDiscoveryResults"
            >
              API Discovery Results
            </el-button>
          </router-link>
        </div>
        <div class="module-info">
          <p v-if="apiDiscoveryCompleted" class="success-message">
            Basic API discovery completed, please improve your API List.
          </p>
          <p v-else class="placeholder-message">
            {{ apiDiscoveryLoading ? 'API discovery in progress...' : 'Waiting to start API discovery' }}
          </p>
        </div>
      </div>
    </el-card>

    <!-- Arrow -->
    <div class="arrow-container">
      <div class="arrow"></div>
    </div>

    <!-- Model Construction Module -->
    <el-card class="module-card" :body-style="{ padding: '0px' }" :class="{ 'active-module': true }">
      <div class="module-header">
        <div class="module-title">
          <el-icon class="module-icon"><Connection /></el-icon>
          <span>Model Construction</span>
        </div>
        <div :class="getStatusClass('completed')">
          <span v-if="isCompleted('completed')" class="check-icon">
            <el-icon><Check /></el-icon>
          </span>
          <span v-else class="dot"></span>
        </div>
      </div>
      <div class="module-content">
        <div class="module-actions">
          <el-button
            type="primary"
            size="small"
            :loading="modelLoading"
            @click="startModelConstruction"
          >
            Start Model Construction
          </el-button>

          <router-link
            v-if="modelCompleted"
            :to="'/myapp/model_report/'+this.$route.params.id"
            class="link-type"
          >
            <el-button type="warning" size="small">Model Report</el-button>
          </router-link>
          <router-link :to="'/myapp/edit_feature_list/'+this.$route.params.id" class="link-type">
            <el-button type="success" size="small">Edit Feature List</el-button>
          </router-link>

        </div>
      </div>
    </el-card>

    <!-- Arrow -->
    <div class="arrow-container">
      <div class="arrow"></div>
    </div>

    <!-- Start Detection Module -->
    <el-card class="module-card" :body-style="{ padding: '0px' }" :class="{ 'active-module': true }">
      <div class="module-header">
        <div class="module-title">
          <el-icon class="module-icon"><Aim /></el-icon>
          <span>Start Detection</span>
        </div>
        <div :class="getStatusClass('waiting')">
          <span v-if="isCompleted('waiting')" class="check-icon">
            <el-icon><Check /></el-icon>
          </span>
          <span v-else class="dot"></span>
        </div>
      </div>
      <div class="module-content">
        <div class="module-actions">
          <router-link :to="'/myapp/detection_config_edit/'+this.$route.params.id" class="link-type">
            <el-button type="success" size="small">Edit Detection Config</el-button>
          </router-link>
          <el-button
            :type="detectionLoading ? 'danger' : 'primary'"
            size="small"
            :loading="detectionLoading"
            @click="detectionLoading ? stopDetection() : startDetection()"
          >
            {{ detectionLoading ? 'Stop Detection' : 'Start Detection' }}
          </el-button>
          <el-button
            v-if="detectionCompleted"
            type="warning"
            size="small"
          >
            View Detection Report
          </el-button>
        </div>
      </div>
    </el-card>

  </div>
</template>

<script>
export default {
  name: 'DetectionDetail',
  data() {
    return {
      //API发现状态
      apiDiscoveryLoading: false,
      apiDiscoveryCompleted: false,
      apiDiscoveryTimer: null,
      //模型构建
      modelLoading: false,
      modelCompleted: false,
      //Detection
      detectionLoading: false,
      detectionCompleted: false,
      timer: null,
      detectionStatus: null
    }
  },
  methods: {
    async startApiDiscovery() {
      try {
        this.apiDiscoveryLoading = true
        await this.startApiDiscoveryRequest()
        this.startApiDiscoveryPolling()
      } catch (error) {
        console.error('API discovery failed:', error)
        this.$message.error('Failed to start API discovery')
        this.apiDiscoveryLoading = false
      }
    },

    // 模拟API发现请求
    async startApiDiscoveryRequest() {
      await new Promise(resolve => setTimeout(resolve, 1000))
    },

    // 开始轮询API发现状态
    startApiDiscoveryPolling() {
      this.apiDiscoveryTimer = setInterval(async () => {
        try {
          const status = await this.checkApiDiscoveryStatus()
          if (status === 'completed') {
            this.stopApiDiscoveryPolling()
            this.apiDiscoveryCompleted = true
            this.$message.success('API discovery completed')
          } else if (status === 'failed') {
            this.stopApiDiscoveryPolling()
            this.$message.error('API discovery failed')
          }
        } catch (error) {
          console.error('Status check failed:', error)
          this.stopApiDiscoveryPolling()
        }
      }, 2000) // 每2秒检查一次
    },

    // 检查API发现状态
    async checkApiDiscoveryStatus() {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve('completed') // 模拟成功状态
        }, 3000)
      })
    },

    // 停止轮询
    stopApiDiscoveryPolling() {
      if (this.apiDiscoveryTimer) {
        clearInterval(this.apiDiscoveryTimer)
        this.apiDiscoveryTimer = null
      }
      this.apiDiscoveryLoading = false
    },

    // 显示结果方法
    showDiscoveryResults() {
      // 这里添加实际的结果展示逻辑
      console.log('Showing API discovery results...')
    },

    // 模型构建请求
    async startModelConstruction() {
      try {
        this.modelLoading = true
        await this.startModelConstructionRequest()
        this.modelCompleted = true
        this.$message.success('Model construction completed')
      } catch (error) {
        console.error('Model construction failed:', error)
        this.$message.error('Model construction failed')
      } finally {
        this.modelLoading = false
      }
    },

    // 模拟模型构建请求
    async startModelConstructionRequest() {
      await new Promise(resolve => setTimeout(resolve, 1000))
    },


    // 开始检测
    async startDetection() {
      try {
        this.detectionLoading = true
        this.detectionCompleted = false
        // 发起检测请求
        await this.startDetectionRequest()
        // 开始轮询检测状态
        this.startPolling()
      } catch (error) {
        console.error('Detection failed:', error)
        this.$message.error('Failed to start detection')
        this.detectionLoading = false
      }
    },

    // 发起检测请求
    async startDetectionRequest() {
      // 这里替换为实际的 API 调用
      await new Promise(resolve => setTimeout(resolve, 1000))
    },

    // 开始轮询
    startPolling() {
      this.timer = setInterval(async () => {
        try {
          // 这里替换为实际的状态检查 API
          const status = await this.checkDetectionStatus()

          if (status === 'completed') {
            this.stopPolling()
            this.detectionCompleted = true
            this.$message.success('Detection completed successfully')
          } else if (status === 'failed') {
            this.stopPolling()
            this.$message.error('Detection failed')
          }
          // 继续轮询其他状态
        } catch (error) {
          console.error('Status check failed:', error)
          this.stopPolling()
          this.$message.error('Failed to check detection status')
        }
      }, 5000) // 每5秒检查一次
    },

    // 检查检测状态
    async checkDetectionStatus() {
      // 这里替换为实际的状态检查逻辑
      return new Promise(resolve => {
        setTimeout(() => {
          resolve('completed')
        }, 2000)
      })
    },

    // 停止轮询
    stopPolling() {
      if (this.timer) {
        clearInterval(this.timer)
        this.timer = null
      }
      this.detectionLoading = false
    },

    // 状态样式控制函数
    getStatusClass(status){
      return {
        'status-indicator': true,
        'status-waiting': status === 'waiting',
        'status-active': status === 'active',
        'status-completed': status === 'completed'
      }
    },

    // 判断是否显示完成图标
    isCompleted(status){
      return status === 'completed'
    }
  },
  // 组件销毁时清理定时器
  beforeDestroy() {
    this.stopPolling()
    this.stopApiDiscoveryPolling()
  }

}

</script>

<style scoped>
  /* Container styles */
  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
  }

  /* Module card styles */
  .module-card {
    margin-bottom: 10px;
    border-radius: 8px;
    overflow: hidden;
  }

  .active-module {
    border: 1px solid #67c23a;
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

  /* Arrow styles */
  .arrow-container {
    display: flex;
    justify-content: center;
    height: 30px;
    position: relative;
  }

  .arrow {
    width: 2px;
    height: 100%;
    background-color: #67c23a;
    position: relative;
  }

  .arrow:after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 8px solid #67c23a;
  }

  /* Status indicator styles */
  .status-indicator {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  }

  .status-waiting {
    border: 2px solid #dcdfe6;
  }

  .status-waiting .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: transparent;
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

  /* 非激活模块样式 */
  .module-card:not(.active-module) {
    border: 1px solid #dcdfe6;
    opacity: 0.8;
  }

  /* 非激活模块中的按钮样式 */
  .module-card:not(.active-module) .el-button {
    background-color: #909399 !important;
    border-color: #909399 !important;
    color: #fff !important;
    cursor: not-allowed !important;
  }

  /* 禁用非激活模块中的链接点击 */
  .module-card:not(.active-module) .link-type {
    pointer-events: none;
  }

  /* 可选：添加过渡效果 */
  .module-card {
    transition: all 0.3s ease;
  }

  .module-info p {
    min-height: 24px; /* 保持高度一致避免跳动 */
    margin: 8px 0 0;
    padding: 6px 12px;
    border-radius: 4px;
  }

  .success-message {
    color: #67c23a;
    background-color: #f0f9eb;
    border: 1px solid #e1f3d8;
  }

  .placeholder-message {
    color: #909399;
    background-color: #f4f4f5;
    border: 1px solid #e9e9eb;
  }
</style>


