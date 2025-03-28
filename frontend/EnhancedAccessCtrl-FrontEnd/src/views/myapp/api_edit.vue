<template>
  <div class="api-info-container">
    <el-form ref="apiForm" :model="apiForm" :rules="rules" label-width="160px">
      <!-- 基础信息 -->
      <el-card class="form-section">
        <div slot="header">API 基础信息</div>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Sample URL:" prop="sample_url">
              <el-input v-model="apiForm.sample_url" placeholder="https://api.example.com/v1/resource/{id}" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Request Method:" prop="request_method">
              <el-select v-model="apiForm.request_method" style="width:100%">
                <el-option v-for="m in methods" :key="m" :value="m" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Sample RequestData:" prop="sample_request_data">
              <el-input v-model="apiForm.sample_request_data" type="textarea" :rows="2" disabled />
            </el-form-item>
          </el-col>
        </el-row>
      </el-card>

      <!-- 路径参数 -->
      <el-card class="form-section">
        <div slot="header">路径参数 (Path Segments)</div>
        <div v-for="(segment, index) in apiForm.path_segment_list" :key="index" class="dynamic-item">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item
                :label="`参数${index+1}名称:`"
                :prop="`path_segment_list.${index}.name`"
                :rules="rules.path_segment_name"
              >
                <el-input v-model="segment.name" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="是否为路径变量:">
                <el-switch
                  v-model="segment.is_path_variable"
                  active-text="是"
                  inactive-text="否"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-button
                v-if="index >= 0"
                type="danger"
                icon="el-icon-delete"
                @click="removePathSegment(index)"
              />
            </el-col>
          </el-row>
        </div>
        <el-button type="primary" icon="el-icon-plus" @click="addPathSegment">添加路径参数</el-button>
      </el-card>

      <!-- 查询参数 -->
      <el-card class="form-section">
        <div slot="header">查询参数 (Query Params)</div>
        <div v-for="(param, index) in apiForm.request_param_list" :key="index" class="dynamic-item">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item
                :label="`参数${index+1}名称:`"
                :prop="`request_param_list.${index}.name`"
                :rules="rules.param_name"
              >
                <el-input v-model="param.name" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="是否必需:">
                <el-switch
                  v-model="param.is_necessary"
                  active-text="是"
                  inactive-text="否"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-button
                v-if="index > 0"
                type="danger"
                icon="el-icon-delete"
                @click="removeQueryParam(index)"
              />
            </el-col>
          </el-row>
        </div>
        <el-button type="primary" icon="el-icon-plus" @click="addQueryParam">添加查询参数</el-button>
      </el-card>

      <!-- 请求体字段 -->
      <el-card class="form-section">
        <div slot="header">请求体字段 (Request Body Fields)</div>
        <div v-for="(field, index) in apiForm.request_data_fields" :key="index" class="dynamic-item">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item
                :label="`字段${index+1}名称:`"
                :prop="`request_data_fields.${index}.name`"
                :rules="rules.field_name"
              >
                <el-input v-model="field.name" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="字段类型:">
                <el-select v-model="field.type">
                  <el-option v-for="t in types" :key="t" :value="t" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-button
                v-if="index > 0"
                type="danger"
                icon="el-icon-delete"
                @click="removeRequestDataField(index)"
              />
            </el-col>
          </el-row>
        </div>
        <el-button type="primary" icon="el-icon-plus" @click="addRequestDataField">添加请求体字段</el-button>
      </el-card>

      <!-- 功能描述 -->
      <el-card class="form-section">
        <div slot="header">功能描述</div>
        <el-form-item prop="function_description">
          <el-input
            v-model="apiForm.function_description"
            type="textarea"
            :rows="3"
            placeholder="简要功能描述（示例：用户访问自己账户的邮件编辑页面）"
          />
        </el-form-item>
      </el-card>

      <!-- 权限信息 -->
      <el-card class="form-section">
        <div slot="header">权限信息</div>
        <el-form-item prop="permission_info">
          <el-input
            v-model="apiForm.permission_info"
            type="textarea"
            :rows="3"
            placeholder="描述正常授权情况及未授权场景（示例：已登录用户可访问，未登录用户访问属于未授权）"
          />
        </el-form-item>
      </el-card>

      <!-- 配置角色 -->
      <el-card class="form-section">
        <div slot="header">角色列表 (Role List)</div>
        <el-form-item label="关联角色:">
          <div class="role-list-editor">
            <el-tag
              v-for="(role, index) in apiForm.role_list"
              :key="index"
              closable
              @close="removeRole(index)"
            >
              {{ role }}
            </el-tag>
            <el-input
              v-if="inputVisible"
              ref="newRoleInput"
              v-model="newRole"
              size="small"
              class="input-new-role"
              @keyup.enter.native="addRole"
              @blur="addRole"
            />
            <el-button
              v-else
              size="small"
              type="primary"
              plain
              @click="showInput"
            >+ 添加角色</el-button>
          </div>
          <div class="tip-text">输入后按回车确认</div>
        </el-form-item>
      </el-card>

      <!-- 操作按钮 -->
      <div class="form-actions">
        <el-button type="primary" @click="submitForm">保存</el-button>
        <el-button @click="cancelForm">取消</el-button>
      </div>
    </el-form>
  </div>
</template>

<script>
import { validURL } from '@/utils/validate'

export default {
  name: 'ApiInfoForm',
  props: {
    apiData: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
      types: ['String', 'Number', 'Boolean', 'Object', 'Array'],
      inputVisible: false,
      newRole: '',
      apiForm: {
        sample_url: '',
        request_method: 'GET',
        path_segment_list: [{ name: '', is_path_variable: false }],
        request_param_list: [{ name: '', is_necessary: false }],
        request_data_fields: [{ name: '', type: 'String' }],
        function_description: '',
        permission_info: '',
        role_list: []
      },
      rules: {
        sample_url: [
          { required: true, message: '示例URL不能为空', trigger: 'blur' },
          { validator: (_, v, cb) => validURL(v) ? cb() : cb(new Error('URL格式不正确')), trigger: 'blur' }
        ],
        request_method: { required: true, message: '请选择请求方法', trigger: 'change' },
        path_segment_name: { required: true, message: '参数名称不能为空', trigger: 'blur' },
        param_name: { required: true, message: '参数名称不能为空', trigger: 'blur' },
        function_description: { required: true, message: '功能描述不能为空', trigger: 'blur' },
        permission_info: { required: true, message: '权限信息不能为空', trigger: 'blur' }
      }
    }
  },
  watch: {
    apiData: {
      immediate: true,
      handler(newVal) {
        if (newVal && Object.keys(newVal).length > 0) {
          this.apiForm = {
            ...newVal,
            path_segment_list: newVal.path_segment_list || [{ name: '', is_path_variable: false }],
            request_param_list: newVal.request_param_list || [{ name: '', is_necessary: false }],
            request_data_fields: newVal.request_data_fields || [{ name: '', type: 'String' }],
            role_list: newVal.role_list ? [...newVal.role_list] : []
          }
        }
      }
    }
  },
  methods: {
    removeRole(index) {
      this.apiForm.role_list.splice(index, 1)
    },
    showInput() {
      this.inputVisible = true
      this.$nextTick(() => {
        this.$refs.newRoleInput.focus()
      })
    },
    addRole() {
      if (this.newRole) {
        const formattedRole = this.newRole.trim()
        if (formattedRole && !this.apiForm.role_list.includes(formattedRole)) {
          this.apiForm.role_list.push(formattedRole)
        }
      }
      this.inputVisible = false
      this.newRole = ''
    },
    submitForm() {
      this.$refs.apiForm.validate(valid => {
        if (valid) {
          const submitData = {
            ...this.apiForm,
            role_list: this.apiForm.role_list || []
          }
          this.$emit('save', submitData) // 将数据保存回上级
        }
      })
    },
    cancelForm() {
      this.$emit('cancel') // 取消操作
    },
    addPathSegment() {
      this.apiForm.path_segment_list.push({ name: '', is_path_variable: false })
    },
    removePathSegment(index) {
      if (this.apiForm.path_segment_list.length >= 1) {
        this.apiForm.path_segment_list.splice(index, 1)
      }
    },
    addQueryParam() {
      this.apiForm.request_param_list.push({ name: '', is_necessary: false })
    },
    removeQueryParam(index) {
      if (this.apiForm.request_param_list.length > 1) {
        this.apiForm.request_param_list.splice(index, 1)
      }
    },
    addRequestDataField() {
      this.apiForm.request_data_fields.push({ name: '', type: 'String' })
    },
    removeRequestDataField(index) {
      if (this.apiForm.request_data_fields.length > 1) {
        this.apiForm.request_data_fields.splice(index, 1)
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
        padding: 12px 20px;
      }

      .dynamic-item {
        margin-bottom: 15px;
        padding: 15px;
        border: 1px solid #ebeef5;
        border-radius: 4px;
        background-color: #fafafa;

        &:hover {
          background-color: #f0f2f5;
        }
      }

      .el-button--primary {
        margin-top: 10px;
      }
    }

    .form-actions {
      text-align: right;
      margin-top: 20px;
    }
  }
</style>
