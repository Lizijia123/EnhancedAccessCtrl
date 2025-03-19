<template>
  <base-module
    :id="id"
    title="Model Construction"
    icon="Connection"
    :state="state"
    :data="data"
  >
    <template #actions="{ disabled }">
      <div v-if="data.last_model_construction_at !== null">
        Last model construction at: {{ data.last_model_construction_at }}
      </div>
      <div class="button-row">
        <el-button
          type="primary"
          size="small"
          :loading="data.isLoading"
          :disabled="disabled || !isStartButtonEnabled"
          @click="startModelConstruction"
        >
          {{ data.isLoading ? 'Data Collecting' : 'Start Model Construction' }}
        </el-button>
        <router-link
          v-if="data.modelDone"
          :to="'/myapp/model_report/' + id"
          class="link-type"
        >
          <el-button type="warning" size="small" :disabled="disabled">Model Report</el-button>
        </router-link>
        <router-link :to="'/myapp/edit_feature_list/' + id" class="link-type">
          <el-button type="success" size="small" :disabled="disabled">Edit Feature List</el-button>
        </router-link>
      </div>
    </template>
  </base-module>
</template>

<script>
import BaseModule from './BaseModule.vue'
import { modelConstruct, getModelConstructStatus } from '../../../api/myapp'

export default {
  name: 'ModelConstructionModule',
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
      default: () => ({ isCompleted: false, isLoading: false, last_model_construction_at: null, modelDone: false })
    }
  },
  data() {
    return {
      isStartButtonEnabled: false,
      modelConstructionTimer: null
    }
  },
  async created() {
    await this.initializeModelConstructionStatus()
  },
  beforeDestroy() {
    this.stopModelConstructionPolling()
  },
  methods: {
    async initializeModelConstructionStatus() {
      try {
        const statusResponse = await getModelConstructStatus({ app_id: this.id })
        this.isStartButtonEnabled = this.data.last_model_construction_at === null || statusResponse.data.status === 'COMPLETED'
        if (statusResponse.data.status !== 'COMPLETED') {
          this.data.isLoading = true
          this.startModelConstructionPolling()
        } else if (this.data.last_model_construction_at !== null) {
          this.data.modelDone = true
        }
      } catch (error) {
        console.error('Failed to initialize model construction status:', error)
      }
    },
    async startModelConstruction() {
      try {
        this.data.isLoading = true
        await this.startModelConstructionRequest()
        await this.startModelConstructionPolling()
      } catch (error) {
        console.error('Model construction failed:', error)
        this.$message.error('Failed to start model construction')
        this.data.isLoading = false
      }
    },
    async startModelConstructionRequest() {
      await modelConstruct({ app_id: this.id })
    },
    async startModelConstructionPolling() {
      // 立即执行一次状态检查
      if (await this.checkModelConstructionStatus(this.id)) {
        return
      }

      // 启动定时器，每5秒检查一次
      this.modelConstructionTimer = setInterval(async() => {
        await this.checkModelConstructionStatus(this.id)
      }, 5000) // 每5秒检查一次
    },
    async checkModelConstructionStatus(id) {
      try {
        const statusResponse = await getModelConstructStatus({ app_id: id })
        if (statusResponse.data.status === 'COMPLETED') {
          this.stopModelConstructionPolling()
          this.data.modelDone = true
          this.data.isLoading = false
          this.$message.success('Data Collection Completed')
          return true
        }
      } catch (error) {
        console.error('Status check failed:', error)
        this.stopModelConstructionPolling()
      }
      return false
    },
    stopModelConstructionPolling() {
      if (this.modelConstructionTimer) {
        clearInterval(this.modelConstructionTimer)
        this.modelConstructionTimer = null
      }
      this.data.isLoading = false
    }
  }
}
</script>
<style>
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
