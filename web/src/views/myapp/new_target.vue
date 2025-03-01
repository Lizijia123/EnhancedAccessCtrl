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
            <i class="el-icon-s-home"></i>
          </div>
          <h2 class="form-title">New Target APP</h2>
        </div>

        <div class="section-header">
          <h3>Basic Information</h3>
          <div class="lock-icon">
            <i class="el-icon-lock"></i>
          </div>
        </div>

        <el-row>
          <el-col :span="24">
            <el-form-item label="APP Name" prop="appName">
              <el-input v-model="appForm.appName" placeholder="The application name of the target application. Eg. Humhub."></el-input>
            </el-form-item>

            <el-form-item label="APP URL" prop="appUrl">
              <el-input v-model="appForm.appUrl" placeholder="The URL of the target application's home page. Eg. http://111.229.33.190:8081/"></el-input>
            </el-form-item>

            <el-form-item label="User Behavior Cycle" prop="userBehaviorCycle">
              <el-input-number v-model="appForm.userBehaviorCycle" :min="1" :max="100" controls-position="right"></el-input-number>
              <span class="input-description">The total number of API calls in a common business process within this APP, generally between 10 and 30.</span>
            </el-form-item>

            <el-form-item label="SFWAP Address" prop="sfwapAddress">
              <el-input v-model="appForm.sfwapAddress" placeholder="Deployment address (IP address and port number) of the SWAFP - Access Control"></el-input>
            </el-form-item>

            <el-form-item label="Description" prop="description">
              <el-input
                v-model="appForm.description"
                type="textarea"
                :rows="6"
                placeholder="Description of APP functions, permission management mechanisms and system status. Eg. Humhub is a social networking platform. Its main functions include user management, space management, content management, etc. Users can create spaces, post comments in spaces, follow certain spaces, and manage their personal profiles, and so on. System administrators can perform various management configurations on the platform. The main access control model of the platform is RBAC. Unauthorized API calls include vertical privilege escalation (invoking illegal APIs) and horizontal privilege escalation (invoking legal APIs with illegal parameters). There is one registered administrator user and several ordinary users in the system, and there are also some spaces, comments, etc."
              ></el-input>
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
              <div class="credential-column action-column"></div>
            </div>
            <div class="credentials-body">
              <div v-for="(credential, index) in appForm.credentials" :key="index" class="credential-row">
                <div class="credential-column">
                  <el-input v-model="credential.role" placeholder="User Role"></el-input>
                </div>
                <div class="credential-column">
                  <el-input v-model="credential.username" placeholder="Username"></el-input>
                </div>
                <div class="credential-column">
                  <el-input v-model="credential.password" placeholder="Password"></el-input>
                </div>
                <div class="credential-column action-column">
                  <el-button type="danger" icon="el-icon-delete" circle @click="removeCredential(index)"></el-button>
                </div>
              </div>
            </div>
          </div>
          <div class="add-credential">
            <el-button type="primary" icon="el-icon-plus" circle @click="addCredential"></el-button>
            <el-button type="info" icon="el-icon-refresh" circle></el-button>
          </div>
        </div>
      </div>
    </el-form>
  </div>
</template>

<script>
  import Sticky from '@/components/Sticky'
  import { validURL } from '@/utils/validate'

  const defaultForm = {
    status: 'draft',
    appName: '',
    appUrl: '',
    userBehaviorCycle: 10,
    sfwapAddress: '',
    description: '',
    credentials: [
      { role: '', username: '', password: '' },
      { role: '', username: '', password: '' },
      { role: '', username: '', password: '' },
      { role: '', username: '', password: '' }
    ]
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
        tempRoute: {}
      }
    },
    created() {
      if (this.isEdit) {
        const id = this.$route.params && this.$route.params.id
        this.fetchData(id)
      }
      this.tempRoute = Object.assign({}, this.$route)
    },
    methods: {
      fetchData(id) {
        // Replace with your actual API call
        console.log('Fetching data for ID:', id)
        // Mock data fetch
        setTimeout(() => {
          this.appForm = Object.assign({}, defaultForm)
          this.setPageTitle()
        }, 300)
      },
      setPageTitle() {
        const title = this.isEdit ? 'Edit Target APP' : 'New Target APP'
        document.title = title
      },
      addCredential() {
        this.appForm.credentials.push({ role: '', username: '', password: '' })
      },
      removeCredential(index) {
        this.appForm.credentials.splice(index, 1)
      },
      confirmForm() {
        this.$refs.appForm.validate(valid => {
          if (valid) {
            this.loading = true
            this.$notify({
              title: 'Success',
              message: 'Form submitted successfully',
              type: 'success',
              duration: 2000
            })
            this.appForm.status = 'published'
            this.loading = false
          } else {
            console.log('error submit!!')
            return false
          }
        })
      },
      temporarySave() {
        this.$message({
          message: 'Form saved temporarily',
          type: 'success',
          showClose: true,
          duration: 1000
        })
        this.appForm.status = 'draft'
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
