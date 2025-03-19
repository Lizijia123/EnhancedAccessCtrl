<template>
  <base-module
    :id="id"
    title="Start Detection"
    icon="Aim"
    :state="state"
    :data="data"
    :dstate="dstate"
  >
    <template #actions="{ disabled }">
      <router-link :to="'/myapp/detection_config_edit/' + id" class="link-type">
        <el-button type="success" size="small" :disabled="disabled">Edit Detection Config</el-button>
      </router-link>
      <el-button
        :type="dstate === 'STARTED' ? 'danger' : 'primary'"
        size="small"
        :loading="data.isLoading"
        :disabled="disabled"
        @click="handleDetectionAction"
      >
        {{ dstate === 'STARTED' ? 'Pause Detection' : 'Start Detection' }}
      </el-button>
      <el-button
        v-if="data.isCompleted"
        type="warning"
        size="small"
      >
        View Detection Report
      </el-button>
    </template>
  </base-module>
</template>

<script>
import BaseModule from './BaseModule.vue'
import { detectionStart, detectionPause } from '../../../api/myapp'

export default {
  name: 'StartDetectionModule',
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
      default: () => ({ isCompleted: false, isLoading: false })
    },
    dstate: {
      type: String,
      default: 'PAUSED' // 默认状态为 PAUSE
    }
  },
  methods: {
    async handleDetectionAction() {
      try {
        this.data.isLoading = true
        if (this.dstate === 'PAUSED') {
          await detectionStart({ app_id: this.id })
          // 调用成功后，切换状态为 STARTED
          this.dstate = 'STARTED'
        } else if (this.dstate === 'STARTED') {
          await detectionPause({ app_id: this.id })
          // 调用成功后，切换状态为 PAUSED
          this.dstate = 'PAUSED'
        }
      } catch (error) {
        console.error('Detection action failed:', error)
        this.$message.error('Failed to perform detection action')
      } finally {
        this.data.isLoading = false
      }
    }
  }
}
</script>
