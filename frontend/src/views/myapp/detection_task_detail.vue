<template>
  <div class="container">
    <!-- Basic Config Module -->
    <basic-config-module
      :id="$route.params.id"
      :state="basicConfigState"
      :data="basicConfigData"
    />

    <!-- Arrow -->
    <div class="arrow-container">
      <div class="arrow" />
    </div>

    <!-- API Discovery Module -->
    <api-discovery-module
      :id="$route.params.id"
      :state="apiDiscoveryState"
      :data="apiDiscoveryData"
    />

    <!-- Arrow -->
    <div class="arrow-container">
      <div class="arrow" />
    </div>

    <!-- Model Construction Module -->
    <model-construction-module
      :id="$route.params.id"
      :state="modelConstructionState"
      :data="modelConstructionData"
    />

    <!-- Arrow -->
    <div class="arrow-container">
      <div class="arrow" />
    </div>

    <!-- Start Detection Module -->
    <start-detection-module
      :id="$route.params.id"
      :state="startDetectionState"
      :data="startDetectionData"
    />
  </div>
</template>

<script>
import BasicConfigModule from './components/BasicConfigModule.vue'
import ApiDiscoveryModule from './components/ApiDiscoveryModule.vue'
import ModelConstructionModule from './components/ModelConstructionModule.vue'
import StartDetectionModule from './components/StartDetectionModule.vue'
import { getAppDetail } from '@/api/myapp'

export default {
  name: 'DetectionDetail',
  components: {
    BasicConfigModule,
    ApiDiscoveryModule,
    ModelConstructionModule,
    StartDetectionModule
  },
  data() {
    return {
      // 定义每个模块的 state 和 data
      basicConfigState: 'active',
      basicConfigData: { isCompleted: false },

      apiDiscoveryState: 'inactive',
      apiDiscoveryData: { isCompleted: false, isLoading: false, last_API_discovery_at: null },

      modelConstructionState: 'inactive',
      modelConstructionData: { isCompleted: false, isLoading: false, last_model_construction_at: null, modelDone: false },

      startDetectionState: 'inactive',
      startDetectionData: { isCompleted: false, isLoading: false, detect_state: 'PAUSE' }
    }
  },
  async created() {
    await this.fetchData()
  },
  methods: {
    async fetchData() {
      const id = this.$route.params.id
      try {
        const response = await getAppDetail({ id })
        const data = response.data

        // 设置API discovery参数
        this.apiDiscoveryData.last_API_discovery_at = data.last_API_discovery_at

        // 设置model
        this.modelConstructionData.last_model_construction_at = data.last_model_construction_at
        if (data.model_report !== null) {
          this.modelConstructionData.modelDone = true
        }

        // 设置Start Detection
        this.startDetectionData.detect_state = data.detect_state

        // 根据 detect_state 设置模块状态
        this.setModuleStates(data.detect_state)

        // 设置 isCompleted 状态
        this.setCompletionStatus(data)
      } catch (error) {
        console.error('Failed to fetch app details:', error)
      }
    },
    setModuleStates(detectState) {
      // 根据 detect_state 设置模块的 state
      switch (detectState) {
        case 'API_LIST_TO_DISCOVER':
          this.apiDiscoveryState = 'active'
          break
        case 'API_LIST_TO_IMPROVE':
          this.apiDiscoveryState = 'active'
          break
        case 'MODEL_FEATURES_TO_CONFIGURE':
          this.apiDiscoveryState = 'active'
          this.modelConstructionState = 'active'
          break
        case 'STARTED':
        case 'PAUSED':
          this.apiDiscoveryState = 'active'
          this.modelConstructionState = 'active'
          this.startDetectionState = 'active'
          break
        default:
          // 默认情况下，只有第一个模块是 active
          break
      }
    },
    setCompletionStatus(data) {
      // 根据 detect_state 设置 isCompleted 状态
      switch (data.detect_state) {
        case 'API_LIST_TO_DISCOVER':
          this.basicConfigData.isCompleted = true
          break
        case 'API_LIST_TO_IMPROVE':
          this.basicConfigData.isCompleted = true
          // this.apiDiscoveryData.isCompleted = true;
          break
        case 'MODEL_FEATURES_TO_CONFIGURE':
          this.basicConfigData.isCompleted = true
          this.apiDiscoveryData.isCompleted = true
          // this.modelConstructionData.isCompleted = true;
          break
        case 'STARTED':
        case 'PAUSED':
          this.basicConfigData.isCompleted = true
          this.apiDiscoveryData.isCompleted = true
          this.modelConstructionData.isCompleted = true
          // this.startDetectionData.isCompleted = true;
          break
        default:
          // 默认情况下，所有模块的 isCompleted 为 false
          break
      }
    }
  }
}
</script>

<style scoped>
  /* 总页面样式 */
  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
  }

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
</style>
