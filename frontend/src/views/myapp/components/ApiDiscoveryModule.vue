<template>
  <base-module
    :id="id"
    title="API Discovery"
    icon="Document"
    :state="state"
    :data="data"
  >
    <template #actions="{ disabled }">
      <div v-if="data.last_API_discovery_at !== null">
        Last API discovery at: {{ data.last_API_discovery_at }}
      </div>
      <div class="button-row">
        <el-button
          type="primary"
          size="small"
          :loading="data.isLoading"
          :disabled="disabled || !isStartButtonEnabled"
          @click="startApiDiscovery"
        >
          Start API Discovery
        </el-button>
        <router-link :to="'/myapp/api_discovery_result/' + id" class="link-type">
          <el-button
            v-if="data.apiDiscoveried"
            type="warning"
            size="small"
            :disabled="disabled"
            @click="showDiscoveryResults"
          >
            API Discovery Results
          </el-button>
        </router-link>
      </div>
      <div class="button-row">
        <!-- 动态显示/隐藏手动 API 发现按钮 -->
        <el-button
          v-if="data.apiDiscoveried && isManualStartVisible"
          type="primary"
          size="small"
          :disabled="disabled || !isManualStartEnabled"
          @click="startManualApiDiscovery"
        >
          Start Manual API Discovery
        </el-button>
        <el-button
          v-if="data.apiDiscoveried && isManualCancelVisible"
          type="danger"
          size="small"
          :disabled="disabled || !isManualCancelEnabled"
          @click="cancelManualApiDiscovery"
        >
          Cancel Manual API Discovery
        </el-button>
        <el-button
          v-if="data.apiDiscoveried && isManualFinishVisible"
          type="success"
          size="small"
          :disabled="disabled || !isManualFinishEnabled"
          @click="finishManualApiDiscovery"
        >
          Finish Manual API Discovery
        </el-button>
      </div>
    </template>
    <template #info>
      <p v-if="data.apiDiscoveried" class="success-message">
        Basic API discovery completed, please improve your API List.
      </p>
      <p v-else class="placeholder-message">
        {{ data.isLoading ? 'API discovery in progress...' : 'Waiting to start API discovery' }}
      </p>
    </template>
  </base-module>
</template>

<script>
import BaseModule from './BaseModule.vue'
import { getApiDiscoveryStatus, apiDiscoveryStart, apiManualDiscoveryCancel, apiManualDiscoveryFinish, getApiManualDiscoveryStatus } from '../../../api/myapp'

export default {
  name: 'ApiDiscoveryModule',
  components: {
    BaseModule
  },
  props: {
    id: {
      type: String,
      required: true
    },
    state: {
      type: String,
      default: 'active'
    },
    data: {
      type: Object,
      default: () => ({
        isCompleted: false,
        isLoading: false,
        last_API_discovery_at: null,
        apiDiscoveried: false
      })
    }
  },
  data() {
    return {
      isStartButtonEnabled: false,
      isManualStartEnabled: false,
      isManualCancelEnabled: false,
      isManualFinishEnabled: false,
      isManualStartVisible: false, // 控制 Start Manual API Discovery 按钮的显示/隐藏
      isManualCancelVisible: false, // 控制 Cancel Manual API Discovery 按钮的显示/隐藏
      isManualFinishVisible: false, // 控制 Finish Manual API Discovery 按钮的显示/隐藏
      apiDiscoveryTimer: null
    }
  },
  async created() {
    await this.initializeApiDiscoveryStatus()
    await this.initializeManualApiDiscoveryStatus()
  },
  beforeDestroy() {
    this.stopApiDiscoveryPolling()
  },
  methods: {
    async initializeApiDiscoveryStatus() {
      try {
        const statusResponse = await getApiDiscoveryStatus({ app_id: this.id })
        this.isStartButtonEnabled = this.data.last_API_discovery_at === null || statusResponse.data.api_discovery_status === 'AVAILABLE'
        if (statusResponse.data.api_discovery_status !== 'AVAILABLE') {
          this.data.isLoading = true
          this.startApiDiscoveryPolling()
        } else if (this.data.last_API_discovery_at !== null) {
          this.data.apiDiscoveried = true
        }
      } catch (error) {
        console.error('Failed to initialize API discovery status:', error)
      }
    },
    async initializeManualApiDiscoveryStatus() {
      try {
        const statusResponse = await getApiManualDiscoveryStatus({ app_id: this.id })
        // 根据 api_manual_discovery_status 动态设置按钮的显示/隐藏
        this.isManualStartVisible = this.data.apiDiscoveried
        this.isManualCancelVisible = statusResponse.data.status === 'ON_GOING'
        this.isManualFinishVisible = statusResponse.data.status === 'ON_GOING'

        // 设置按钮的可用性
        this.isManualStartEnabled = statusResponse.data.status === 'AVAILABLE'
        this.isManualCancelEnabled = statusResponse.data.status === 'ON_GOING'
        this.isManualFinishEnabled = statusResponse.data.status === 'ON_GOING'
      } catch (error) {
        console.error('Failed to initialize manual API discovery status:', error)
      }
    },
    async startApiDiscovery() {
      try {
        this.data.isLoading = true
        await apiDiscoveryStart({
          app_id: this.id,
          mode: 'AUTO'
        })
        this.startApiDiscoveryPolling()
      } catch (error) {
        console.error('API discovery failed:', error)
        this.$message.error('Failed to start API discovery')
        this.data.isLoading = false
      }
    },
    async startManualApiDiscovery() {
      try {
        await apiDiscoveryStart({
          app_id: this.id,
          mode: 'MANUAL'
        })
        await this.initializeManualApiDiscoveryStatus() // 重新初始化状态
      } catch (error) {
        console.error('Manual API discovery failed:', error)
        this.$message.error('Failed to start manual API discovery')
      }
    },
    async cancelManualApiDiscovery() {
      try {
        await apiManualDiscoveryCancel({ app_id: this.id })
        await this.initializeManualApiDiscoveryStatus() // 重新初始化状态
      } catch (error) {
        console.error('Failed to cancel manual API discovery:', error)
        this.$message.error('Failed to cancel manual API discovery')
      }
    },
    async finishManualApiDiscovery() {
      try {
        await apiManualDiscoveryFinish({ app_id: this.id })
        await this.initializeManualApiDiscoveryStatus() // 重新初始化状态
      } catch (error) {
        console.error('Failed to finish manual API discovery:', error)
        this.$message.error('Failed to finish manual API discovery')
      }
    },
    startApiDiscoveryPolling() {
      if (this.checkApiDiscoveryStatus(this.id)) {
        return
      }
      this.apiDiscoveryTimer = setInterval(async() => {
        await this.checkApiDiscoveryStatus(this.id)
      }, 5000)
    },
    async checkApiDiscoveryStatus(id) {
      try {
        const statusResponse = await getApiDiscoveryStatus({ app_id: id })
        if (statusResponse.data.api_discovery_status === 'AVAILABLE') {
          this.stopApiDiscoveryPolling()
          this.data.apiDiscoveried = true
          this.data.isLoading = false
          this.$message.success('API discovery completed')
        }
      } catch (error) {
        console.error('Status check failed:', error)
        this.stopApiDiscoveryPolling()
      }
      return true
    },
    stopApiDiscoveryPolling() {
      if (this.apiDiscoveryTimer) {
        clearInterval(this.apiDiscoveryTimer)
        this.apiDiscoveryTimer = null
      }
      this.data.isLoading = false
    },
    showDiscoveryResults() {
      console.log('Showing API discovery results...')
    }
  }
}
</script>

<style scoped>
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

  .el-button{
    margin-left: 0px;
  }
  .button-row {
    width: 100%;
    display: flex;
    gap: 10px;
    margin-bottom: 10px;
  }
</style>
