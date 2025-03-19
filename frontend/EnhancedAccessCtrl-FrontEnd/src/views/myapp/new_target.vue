<template>
  <div class="app-form-container">
    <el-form ref="appForm" :model="appForm" :rules="rules" class="form-container">
      <sticky :z-index="10" :class-name="'sub-navbar ' + appForm.status">
        <el-button v-loading="loading" style="margin-left: 10px;" type="primary" @click="confirmForm">
          Confirm
        </el-button>
        <el-button style="margin-left: 10px;" type="danger" @click="deleteForm">
          Delete
        </el-button>
      </sticky>

      <div class="app-form-main-container">
        <div class="form-header">
          <div class="home-icon">
            <i class="el-icon-s-home" />
          </div>
          <h2 class="form-title">{{ title }}</h2>
        </div>

        <div class="section-header">
          <h3>Basic Information</h3>
          <div class="lock-icon">
            <i class="el-icon-lock" />
          </div>
        </div>

        <el-row>
          <el-col :span="24">
            <el-form-item label="APP Name" prop="appName">
              <el-input v-model="appForm.appName" placeholder="The application name of the target application. Eg. Humhub." />
            </el-form-item>

            <el-form-item label="APP URL" prop="appUrl">
              <el-input v-model="appForm.appUrl" placeholder="The URL of the target application's home page. Eg. http://111.229.33.190:8081/" />
            </el-form-item>

            <el-form-item label="User Behavior Cycle" prop="userBehaviorCycle">
              <el-input-number v-model="appForm.userBehaviorCycle" :min="1" :max="100" controls-position="right" />
              <span class="input-description">The total number of API calls in a common business process within this APP, generally between 10 and 30.</span>
            </el-form-item>

            <el-form-item label="SFWAP Address" prop="sfwapAddress">
              <el-input v-model="appForm.sfwapAddress" placeholder="Deployment address (IP address and port number) of the SWAFP - Access Control" />
              <el-button
                type="primary"
                size="mini"
                style="margin-left: 10px;"
                @click="checkUrlDeployment"
              >
                Check Deployment
              </el-button>
            </el-form-item>

            <el-form-item label="Description" prop="description">
              <el-input
                v-model="appForm.description"
                type="textarea"
                :rows="6"
                placeholder="Description of APP functions, permission management mechanisms and system status."
              />
            </el-form-item>
          </el-col>
        </el-row>

        <div class="credentials-section">
          <h3>User Login Credentials List</h3>
          <div class="credentials-container">
            <div class="credentials-header">
              <div class="credential-column">User Role</div>
              <div class="credential-column">Username</div>
              <div class="credential-column">Password</div>
              <div class="credential-column action-column" />
            </div>
            <div class="credentials-body">
              <div v-for="(credential, index) in appForm.credentials" :key="index" class="credential-row">
                <div class="credential-column">
                  <el-input v-model="credential.role" placeholder="User Role" />
                </div>
                <div class="credential-column">
                  <el-input v-model="credential.username" placeholder="Username" />
                </div>
                <div class="credential-column">
                  <el-input v-model="credential.password" placeholder="Password" />
                </div>
                <div class="credential-column action-column">
                  <el-button type="danger" icon="el-icon-delete" circle @click="removeCredential(index)" />
                </div>
              </div>
            </div>
          </div>
          <div class="add-credential">
            <el-button type="primary" icon="el-icon-plus" circle @click="addCredential" />
          </div>
        </div>
      </div>
    </el-form>
  </div>
</template>

<script>
import Sticky from '@/components/Sticky'
import { validURL } from '@/utils/validate'
import { getAppDetail, putAppBasicInfo, postAppBasicInfo, checkUrlDeployment } from '@/api/myapp'

const defaultForm = {
  status: 'draft',
  appName: '',
  appUrl: '',
  userBehaviorCycle: 10,
  sfwapAddress: '',
  description: '',
  credentials: []
}

export default {
  name: 'TargetAppForm',
  components: { Sticky },
  props: {
    isEdit: {
      type: Boolean,
      default: false
    }
  },
  data() {
    const validateRequire = (rule, value, callback) => {
      if (value === '') {
        this.$message({
          message: rule.field + ' is required',
          type: 'error'
        })
        callback(new Error(rule.field + ' is required'))
      } else {
        callback()
      }
    }
    const validateUrl = (rule, value, callback) => {
      if (value) {
        if (validURL(value)) {
          callback()
        } else {
          this.$message({
            message: 'URL format is incorrect',
            type: 'error'
          })
          callback(new Error('URL format is incorrect'))
        }
      } else {
        callback()
      }
    }
    return {
      appForm: Object.assign({}, defaultForm),
      loading: false,
      rules: {
        appName: [{ validator: validateRequire }],
        appUrl: [{ validator: validateUrl, trigger: 'blur' }],
        sfwapAddress: [{ validator: validateRequire }]
      },
      title: ''
    }
  },
  created() {
    const id = this.$route.params && this.$route.params.id
    if (id !== undefined) {
      this.title = 'Edit Target APP'
      this.fetchData(id)
    } else {
      this.title = 'New Target APP'
    }
  },
  methods: {
    async fetchData(id) {
      this.loading = true
      try {
        const response = await getAppDetail({ id })
        const data = response.data
        this.appForm = {
          status: data.is_draft ? 'draft' : 'published',
          appName: data.APP_name,
          appUrl: data.APP_url,
          userBehaviorCycle: data.user_behavior_cycle,
          sfwapAddress: data.SFWAP_address,
          description: data.description,
          credentials: data.login_credentials.map(cred => ({
            role: cred.user_role,
            username: cred.username,
            password: cred.password
          }))
        }
      } catch (error) {
        console.error('Failed to fetch app details:', error)
      } finally {
        this.loading = false
      }
    },
    addCredential() {
      this.appForm.credentials.push({ role: '', username: '', password: '' })
    },
    removeCredential(index) {
      this.appForm.credentials.splice(index, 1)
    },
    async confirmForm() {
      this.$refs.appForm.validate(async valid => {
        if (valid) {
          this.loading = true
          try {
            const id = this.$route.params && this.$route.params.id
            const payload = {
              APP_name: this.appForm.appName,
              APP_url: this.appForm.appUrl,
              user_behavior_cycle: this.appForm.userBehaviorCycle,
              SFWAP_address: this.appForm.sfwapAddress,
              description: this.appForm.description,
              login_credentials: this.appForm.credentials.map(cred => ({
                user_role: cred.role,
                username: cred.username,
                password: cred.password
              }))
            }

            if (id === undefined) {
              await postAppBasicInfo(payload)
            } else {
              await putAppBasicInfo(id, payload)
            }

            this.$notify({
              title: 'Success',
              message: 'Form submitted successfully',
              type: 'success',
              duration: 2000
            })

            // 返回上一个页面
            this.$router.go(-1)
          } catch (error) {
            console.error('Failed to submit form:', error)
            this.$notify({
              title: 'Error',
              message: 'Failed to submit form',
              type: 'error',
              duration: 2000
            })
          } finally {
            this.loading = false
          }
        } else {
          console.log('error submit!!')
          return false
        }
      })
    },
    deleteForm() {
      this.$confirm('Are you sure you want to delete this form?', 'Warning', {
        confirmButtonText: 'OK',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }).then(() => {
        this.$message({
          type: 'success',
          message: 'Delete completed'
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: 'Delete canceled'
        })
      })
    },
    async checkUrlDeployment() {
      if (!this.appForm.sfwapAddress) {
        this.$message({
          message: '请先输入 SFWAP Address',
          type: 'warning'
        })
        return
      }

      try {
        const response = await checkUrlDeployment(this.appForm.sfwapAddress)
        if (response.code === 200 && response.data.status === 'SUCCESS') {
          this.$message({
            message: response.message,
            type: 'success'
          })
        } else {
          this.$message({
            message: response.message,
            type: 'error'
          })
        }
      } catch (error) {
        console.error('检查部署失败:', error)
        this.$message({
          message: '检查部署失败，请稍后重试',
          type: 'error'
        })
      }
    }
  }
}
</script>

<style lang="scss" scoped>
  .app-form-container {
    position: relative;

    .app-form-main-container {
      padding: 20px 45px 20px 50px;
      background-color: #f5f7fa;
      min-height: calc(100vh - 100px);
    }

    .form-header {
      display: flex;
      align-items: center;
      margin-bottom: 20px;

      .home-icon {
        color: #409EFF;
        font-size: 24px;
        margin-right: 10px;
      }

      .form-title {
        color: #409EFF;
        margin: 0;
        font-weight: 500;
      }
    }

    .section-header {
      display: flex;
      align-items: center;
      margin-bottom: 20px;

      h3 {
        margin: 0;
        font-weight: 500;
      }

      .lock-icon {
        margin-left: 10px;
        color: #909399;
      }
    }

    .el-form-item {
      margin-bottom: 22px;
    }

    .input-description {
      font-size: 12px;
      color: #909399;
      margin-left: 10px;
    }

    .credentials-section {
      margin-top: 30px;

      h3 {
        margin-bottom: 15px;
      }
    }

    .credentials-container {
      border: 1px solid #dcdfe6;
      border-radius: 4px;
      background-color: #fff;
      max-height: 300px;
      overflow-y: auto;
    }

    .credentials-header {
      display: flex;
      background-color: #f5f7fa;
      padding: 10px 0;
      border-bottom: 1px solid #dcdfe6;
      position: sticky;
      top: 0;
      z-index: 1;
    }

    .credentials-body {
      max-height: 250px;
      overflow-y: auto;
    }

    .credential-row {
      display: flex;
      padding: 10px 0;
      border-bottom: 1px solid #ebeef5;

      &:last-child {
        border-bottom: none;
      }
    }

    .credential-column {
      flex: 1;
      padding: 0 10px;

      &.action-column {
        flex: 0 0 80px;
        display: flex;
        justify-content: center;
        align-items: center;
      }
    }

    .add-credential {
      margin-top: 15px;
      display: flex;
      justify-content: flex-end;

      .el-button {
        margin-left: 10px;
      }
    }
  }
</style>
