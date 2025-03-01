<template>
  <div class="api-info-container">
    <el-form ref="apiForm" :model="apiForm" :rules="rules" label-width="160px">

      <!-- 固定操作栏 -->
      <sticky :z-index="10" class-name="sub-navbar">
        <el-button type="success" @click="submitForm" :loading="loading">保存配置</el-button>
      </sticky>

      <div class="form-content">
        <!-- 基础信息 -->
        <el-card class="form-section">
          <div slot="header">API基础信息</div>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Sample URL:" prop="sampleUrl">
                <el-input v-model="apiForm.sampleUrl" placeholder="https://api.example.com/v1/resource/{id}"></el-input>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Request Method:" prop="requestMethod">
                <el-select v-model="apiForm.requestMethod" style="width:100%">
                  <el-option v-for="m in methods" :key="m" :value="m"></el-option>
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </el-card>

        <!-- 路径参数 -->
        <el-card class="form-section">
          <div slot="header">路径参数 (Path Segments)</div>
          <div v-for="(segment, index) in apiForm.pathSegments" :key="index" class="dynamic-item">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item
                  :label="`参数${index+1}名称:`"
                  :prop="`pathSegments.${index}.name`"
                  :rules="rules.pathSegmentName"
                >
                  <el-input v-model="segment.name"></el-input>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="是否为路径变量:">
                  <el-switch
                    v-model="segment.isPathVariable"
                    active-text="是"
                    inactive-text="否"
                  ></el-switch>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-button
                  v-if="index > 0"
                  type="danger"
                  icon="el-icon-delete"
                  @click="removePathSegment(index)"
                ></el-button>
              </el-col>
            </el-row>
          </div>
          <el-button type="primary" icon="el-icon-plus" @click="addPathSegment">添加路径参数</el-button>
        </el-card>

        <!-- 请求参数 -->
        <el-card class="form-section">
          <div slot="header">请求参数 (Request Params)</div>
          <div v-for="(param, index) in apiForm.requestParams" :key="index" class="dynamic-item">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-form-item
                  :label="`参数${index+1}名称:`"
                  :prop="`requestParams.${index}.name`"
                  :rules="rules.paramName"
                >
                  <el-input v-model="param.name"></el-input>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="是否必需:">
                  <el-switch
                    v-model="param.required"
                    active-text="是"
                    inactive-text="否"
                  ></el-switch>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="参数类型:">
                  <el-select v-model="param.type">
                    <el-option v-for="t in types" :key="t" :value="t"></el-option>
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-button
                  v-if="index > 0"
                  type="danger"
                  icon="el-icon-delete"
                  @click="removeRequestParam(index)"
                ></el-button>
              </el-col>
            </el-row>
          </div>
          <el-button type="primary" icon="el-icon-plus" @click="addRequestParam">添加请求参数</el-button>
        </el-card>

        <!-- 功能描述 -->
        <el-card class="form-section">
          <div slot="header">功能描述</div>
          <el-form-item prop="functionDesc">
            <el-input
              v-model="apiForm.functionDesc"
              type="textarea"
              :rows="3"
              placeholder="简要功能描述（示例：用户访问自己账户的邮件编辑页面）"
            ></el-input>
          </el-form-item>
        </el-card>

        <!-- 权限信息 -->
        <el-card class="form-section">
          <div slot="header">权限信息</div>
          <el-form-item prop="permissionInfo">
            <el-input
              v-model="apiForm.permissionInfo"
              type="textarea"
              :rows="3"
              placeholder="描述正常授权情况及未授权场景（示例：已登录用户可访问，未登录用户访问属于未授权）"
            ></el-input>
          </el-form-item>
        </el-card>
      </div>
    </el-form>
  </div>
</template>

<script>
  import Sticky from '@/components/Sticky'
  import { validURL } from '@/utils/validate'

  export default {
    name: 'ApiInfoForm',
    components: { Sticky },
    data() {
      return {
        methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
        types: ['String', 'Number', 'Boolean', 'Object', 'Array'],
        apiForm: {
          sampleUrl: '',
          requestMethod: 'GET',
          pathSegments: [{
            name: '',
            isPathVariable: false
          }],
          requestParams: [{
            name: '',
            required: true,
            type: 'String'
          }],
          functionDesc: '',
          permissionInfo: ''
        },
        loading: false,
        rules: {
          sampleUrl: [
            { required: true, message: '示例URL不能为空', trigger: 'blur' },
            { validator: (_, v, cb) => validURL(v) ? cb() : cb(new Error('URL格式不正确')), trigger: 'blur' }
          ],
          requestMethod: { required: true, message: '请选择请求方法', trigger: 'change' },
          pathSegmentName: { required: true, message: '参数名称不能为空', trigger: 'blur' },
          paramName: { required: true, message: '参数名称不能为空', trigger: 'blur' },
          functionDesc: { required: true, message: '功能描述不能为空', trigger: 'blur' },
          permissionInfo: { required: true, message: '权限信息不能为空', trigger: 'blur' }
        }
      }
    },
    methods: {
      submitForm() {
        this.$refs.apiForm.validate(valid => {
          if (valid) {
            this.loading = true
            // 模拟提交过程
            setTimeout(() => {
              this.$notify.success({ title: '成功', message: '配置已保存', duration: 2000 })
              this.loading = false
            }, 1500)
          }
        })
      },
      addPathSegment() {
        this.apiForm.pathSegments.push({ name: '', isPathVariable: false })
      },
      removePathSegment(index) {
        if (this.apiForm.pathSegments.length > 1) {
          this.apiForm.pathSegments.splice(index, 1)
        }
      },
      addRequestParam() {
        this.apiForm.requestParams.push({ name: '', required: true, type: 'String' })
      },
      removeRequestParam(index) {
        if (this.apiForm.requestParams.length > 1) {
          this.apiForm.requestParams.splice(index, 1)
        }
      }
    }
  }
</script>

<style lang="scss" scoped>
  .api-info-container {
    padding: 20px;

    .form-section {
      margin-bottom: 20px;

      ::v-deep .el-card__header {
        background: #f5f7fa;
        font-weight: bold;
      }
    }

    .dynamic-item {
      margin-bottom: 15px;
      padding: 15px;
      border: 1px solid #ebeef5;
      border-radius: 4px;

      &:hover {
        background-color: #f8f9fa;
      }
    }

    .el-button--primary {
      margin-top: 10px;
    }
  }
</style>
