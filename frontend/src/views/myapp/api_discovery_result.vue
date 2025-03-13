<template>
  <div class="app-container">
    <!-- 提交按钮 -->
    <div class="submit-button">
      <el-button type="primary" @click="submitUserApiList">提交</el-button>
    </div>

    <!-- Discovered API 表格 -->
    <div class="table-section">
      <h2 class="table-title">Discovered API</h2>
      <div class="table-wrapper">
        <el-table
          :key="tableKey"
          v-loading="listLoading"
          :data="discoveredApiList"
          border
          fit
          highlight-current-row
          style="width: 100%;"
        >
          <el-table-column label="ID" prop="id" align="center" width="80">
            <template slot-scope="{row}">
              <span>{{ row.id }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Method" width="150px" align="center">
            <template slot-scope="{row}">
              <span>{{ row.request_method }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Path" min-width="150px">
            <template slot-scope="{row}">
              <span class="link-type">{{ row.sample_url }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Description" width="310px" align="center">
            <template slot-scope="{row}">
              <span>{{ row.function_description }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="110px" align="center">
            <template slot-scope="{row}">
              <el-button
                type="primary"
                size="mini"
                @click="moveToUserApiList(row)"
              >add</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 间隔 -->
    <div class="table-gap" />

    <!-- User Api List 表格 -->
    <div class="table-section">
      <h2 class="table-title">User Api List</h2>
      <div class="table-wrapper">
        <el-table
          :key="tableKey"
          v-loading="listLoading"
          :data="userApiList"
          border
          fit
          highlight-current-row
          style="width: 100%;"
        >
          <el-table-column label="ID" prop="id" align="center" width="80">
            <template slot-scope="{row}">
              <span>{{ row.id }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Method" width="150px" align="center">
            <template slot-scope="{row}">
              <span>{{ row.request_method }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Path" min-width="150px">
            <template slot-scope="{row}">
              <span class="link-type">{{ row.sample_url }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Description" width="310px" align="center">
            <template slot-scope="{row}">
              <span>{{ row.function_description }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="210px" align="center">
            <template slot-scope="{row, $index}">
              <el-button type="primary" size="mini" @click="editApi(row)">
                Edit
              </el-button>
              <el-button type="danger" size="mini" @click="removeFromUserApiList($index)">
                Delete
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 编辑弹框 -->
    <el-dialog :visible.sync="editDialogVisible" width="80%" title="Edit API">
      <api-edit :api-data="selectedApi" @save="handleSaveApi" @cancel="editDialogVisible = false" />
    </el-dialog>
  </div>
</template>

<script>
import { getApiList, putUserApiList } from '../../api/myapp'
import ApiEdit from './api_edit.vue'

export default {
  name: 'ApiDiscoveryResult',
  components: { ApiEdit },
  data() {
    return {
      tableKey: 0,
      discoveredApiList: [],
      userApiList: [],
      listLoading: true,
      editDialogVisible: false,
      selectedApi: null
    }
  },
  created() {
    this.getApiListData()
  },
  methods: {
    async getApiListData() {
      this.listLoading = true
      try {
        const response = await getApiList({ app_id: this.$route.params.id })
        this.discoveredApiList = response.data.discovered_API_list
        this.userApiList = response.data.user_API_list
      } catch (error) {
        console.error('Failed to fetch API list:', error)
      } finally {
        this.listLoading = false
      }
    },
    moveToUserApiList(row) {
      const index = this.discoveredApiList.findIndex(item => item.id === row.id)
      if (index !== -1) {
        this.userApiList.push(this.discoveredApiList[index])
        this.discoveredApiList.splice(index, 1)
      }
    },
    removeFromUserApiList(index) {
      this.discoveredApiList.push(this.userApiList[index])
      this.userApiList.splice(index, 1)
    },
    editApi(row) {
      this.selectedApi = row
      this.editDialogVisible = true
    },
    handleSaveApi(updatedApi) {
      const index = this.userApiList.findIndex(item => item.id === updatedApi.id)
      if (index !== -1) {
        this.userApiList.splice(index, 1, updatedApi) // 更新数据
      }
      this.editDialogVisible = false // 关闭弹框
    },
    async submitUserApiList() {
      try {
        await putUserApiList(this.$route.params.id, { user_API_list: this.userApiList, example_API_seqs: [] })
        this.$notify.success({ title: '成功', message: 'API列表已提交', duration: 2000 })
      } catch (error) {
        console.error('Failed to submit user API list:', error)
        this.$notify.error({ title: '错误', message: '提交失败', duration: 2000 })
      }
    }
  }
}
</script>

<style scoped>
  .app-container {
    padding: 20px;
    background: #fff;
  }

  .submit-button {
    margin-bottom: 20px;
  }

  .table-section {
    margin-bottom: 30px;
  }

  .table-title {
    color: #606266;
    font-size: 18px;
    margin-bottom: 15px;
    padding-left: 10px;
    border-left: 4px solid #409EFF;
  }

  .table-wrapper {
    height: 400px; /* 固定高度触发滚动条 */
    overflow-y: auto;
    border: 1px solid #EBEEF5;
    border-radius: 4px;
    box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
  }

  .table-gap {
    height: 30px;
    background: linear-gradient(
      to right,
      transparent 0%,
      #f8f9fa 50%,
      transparent 100%
    );
    margin: 20px 0;
  }

  /* 优化滚动条样式 */
  ::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  ::-webkit-scrollbar-thumb {
    background-color: #c1c1c1;
    border-radius: 4px;
  }
</style>
