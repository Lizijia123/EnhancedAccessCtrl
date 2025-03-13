<template>
  <div class="createPost-container">
    <el-form ref="postForm" :model="postForm" :rules="rules" class="form-container">
      <!-- 粘性头部 -->
      <sticky :z-index="10" :class-name="'sub-navbar ' + postForm.status">
        <el-button v-loading="loading" style="margin-left: 10px;" type="success" @click="submitForm">
          保存配置
        </el-button>
      </sticky>

      <div class="createPost-main-container">
        <el-row>
          <el-col :span="24">
            <div class="postInfo-container">
              <!-- 增强检测开关 -->
              <el-row>
                <el-col :span="12">
                  <el-form-item label="增强检测开关" label-width="120px" class="postInfo-container-item">
                    <el-switch v-model="postForm.enhanced_detection_enabled" active-text="开启" inactive-text="关闭" />
                  </el-form-item>
                </el-col>
              </el-row>

              <!-- 组合流量检测时长 -->
              <el-row>
                <el-col :span="12">
                  <el-form-item label="组合流量检测时长" label-width="120px" class="postInfo-container-item">
                    <el-input-number
                      v-model="postForm.combined_data_duration"
                      :min="1"
                      :max="30"
                      controls-position="right"
                    />
                    <span class="input-description">单位：秒</span>
                  </el-form-item>
                </el-col>
              </el-row>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-form>
  </div>
</template>

<script>
import Sticky from '@/components/Sticky' // 粘性header组件
import { getAppDetail, saveDetectionConfig } from '@/api/myapp'

const defaultForm = {
  enhanced_detection_enabled: false, // 增强检测开关
  combined_data_duration: 10 // 组合流量检测时长
}

export default {
  name: 'DetectionConfigEdit',
  components: { Sticky },
  props: {
    isEdit: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      postForm: Object.assign({}, defaultForm), // 表单数据
      loading: false, // 加载状态
      rules: {} // 表单校验规则
    }
  },
  created() {
    if (this.isEdit) {
      const id = this.$route.params && this.$route.params.id
      this.fetchData(id)
    }
  },
  methods: {
    // 获取数据
    async fetchData(id) {
      this.loading = true
      try {
        const response = await getAppDetail({ id })
        const data = response.data

        // 填充表单数据
        this.postForm = {
          enhanced_detection_enabled: data.enhanced_detection_enabled,
          combined_data_duration: data.combined_data_duration
        }
      } catch (error) {
        console.error('Failed to fetch app details:', error)
      } finally {
        this.loading = false
      }
    },
    // 提交表单
    async submitForm() {
      this.$refs.postForm.validate(async valid => {
        if (valid) {
          this.loading = true
          try {
            const id = this.$route.params && this.$route.params.id

            // 构造提交数据
            const payload = {
              enhanced_detection_enabled: this.postForm.enhanced_detection_enabled,
              combined_data_duration: this.postForm.combined_data_duration
            }

            // 调用保存接口
            await saveDetectionConfig(id, payload)

            this.$notify({
              title: '成功',
              message: '保存成功',
              type: 'success',
              duration: 2000
            })

            // 返回上级页面
            this.$router.back()
          } catch (error) {
            console.error('提交失败:', error)
            this.$notify({
              title: '错误',
              message: '保存失败',
              type: 'error',
              duration: 2000
            })
          } finally {
            this.loading = false
          }
        } else {
          console.log('表单校验失败')
          return false
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
  .createPost-container {
    position: relative;

    .createPost-main-container {
      padding: 40px 45px 20px 50px;

      .postInfo-container {
        position: relative;
        margin-bottom: 10px;

        .postInfo-container-item {
          margin-bottom: 20px;
        }
      }
    }

    .input-description {
      margin-left: 10px;
      font-size: 12px;
      color: #909399;
    }
  }
</style>
