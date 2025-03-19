<template>
  <div class="app-container">
    <!-- 提交按钮 -->
    <div class="submit-button">
      <el-button type="primary" @click="showConfigDialog">提交</el-button>
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
          <el-table-column label="Sample Url" min-width="150px">
            <template slot-scope="{row}">
              <span class="link-type">{{ row.sample_url }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Sample Data" min-width="150px">
            <template slot-scope="{row}">
              <span>{{ row.sample_request_data }}</span>
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
                :disabled="row.isAdded"
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
          <el-table-column label="Sample Url" min-width="150px">
            <template slot-scope="{row}">
              <span class="link-type">{{ row.sample_url }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Sample Data" min-width="150px">
            <template slot-scope="{row}">
              <span>{{ row.sample_request_data }}</span>
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

    <!-- 提交前弹框 -->
    <el-dialog
      :visible.sync="configDialogVisible"
      title="配置API序列"
      width="80%"
      @close="handleConfigClose"
    >
      <div class="seq-config-container">
        <!-- 正常序列 -->
        <div class="seq-type">
          <h3>正常序列 (Normal Sequences)</h3>
          <div
            v-for="(seq, index) in seqConfig.normal_seqs"
            :key="'normal'+index"
            class="seq-item"
          >
            <el-input
              v-model="seq.role"
              placeholder="输入角色名称"
              style="width: 200px; margin-right: 20px;"
            />
            <el-select
              v-model="seq.selectedIds"
              placeholder="选择API"
              style="width: 400px; margin-right: 20px;"
              @change="handleSelectionChange('normal_seqs', index)"
            >
              <el-option
                v-for="api in userApiList"
                :key="api.id"
                :label="`${api.id} - ${api.request_method} ${api.sample_url}`"
                :value="api.id"
              />
            </el-select>
            <el-button @click="removeSeq('normal_seqs', index)">删除</el-button>

            <div class="seq-descriptions">
              <div
                v-for="(item, itemIndex) in seq.seq"
                :key="itemIndex"
                class="desc-item"
              >
                <span class="api-info">ID: {{ item.id }} - {{ getApiInfo(item.id) }}</span>
                <el-input
                  v-model="item.description"
                  placeholder="输入描述"
                  style="width: 300px;"
                />
                <el-button type="danger" size="mini" @click="removeSeqItem('normal_seqs', index, itemIndex)">
                  删除
                </el-button>
              </div>
            </div>
          </div>
          <el-button @click="addSeq('normal_seqs')">+ 添加正常序列</el-button>
        </div>

        <!-- 恶意序列 -->
        <div class="seq-type" style="margin-top: 40px;">
          <h3>恶意序列 (Malicious Sequences)</h3>
          <div
            v-for="(seq, index) in seqConfig.malicious_seqs"
            :key="'normal'+index"
            class="seq-item"
          >
            <el-input
              v-model="seq.role"
              placeholder="输入角色名称"
              style="width: 200px; margin-right: 20px;"
            />
            <el-select
              v-model="seq.selectedIds"
              placeholder="选择API"
              style="width: 400px; margin-right: 20px;"
              @change="handleSelectionChange('malicious_seqs', index)"
            >
              <el-option
                v-for="api in userApiList"
                :key="api.id"
                :label="`${api.id} - ${api.request_method} ${api.sample_url}`"
                :value="api.id"
              />
            </el-select>
            <el-button @click="removeSeq('malicious_seqs', index)">删除</el-button>

            <div class="seq-descriptions">
              <div
                v-for="(item, itemIndex) in seq.seq"
                :key="itemIndex"
                class="desc-item"
              >
                <span class="api-info">ID: {{ item.id }} - {{ getApiInfo(item.id) }}</span>
                <el-input
                  v-model="item.description"
                  placeholder="输入描述"
                  style="width: 300px;"
                />
                <el-button type="danger" size="mini" @click="removeSeqItem('malicious_seqs', index, itemIndex)">
                  删除
                </el-button>
              </div>
            </div>
          </div>
          <el-button @click="addSeq('malicious_seqs')">+ 添加恶意序列</el-button>
        </div>
      </div>

      <span slot="footer" class="dialog-footer">
        <el-button @click="configDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确认提交</el-button>
      </span>
    </el-dialog>

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
      selectedApi: null,
      configDialogVisible: false,
      seqConfig: {
        normal_seqs: [],
        malicious_seqs: []
      }
    }
  },
  created() {
    this.getApiListData()
  },
  methods: {
    removeSeqItem(type, seqIndex, itemIndex) {
      this.seqConfig[type][seqIndex].seq.splice(itemIndex, 1)
    },

    showConfigDialog() {
      // 初始化配置数据
      this.seqConfig = {
        normal_seqs: [],
        malicious_seqs: []
      }
      this.configDialogVisible = true
    },

    addSeq(type) {
      this.seqConfig[type].push({
        role: '',
        selectedIds: [],
        seq: []
      })
    },

    removeSeq(type, index) {
      this.seqConfig[type].splice(index, 1)
    },
    getApiInfo(id) {
      const api = this.userApiList.find(a => a.id === id)
      return api ? `${api.request_method} ${api.sample_url}` : '未知API'
    },
    handleSelectionChange(type, index) {
      const currentSeq = this.seqConfig[type][index]
      // 每次选择时新增一行
      currentSeq.seq.push({
        id: currentSeq.selectedIds,
        description: ''
      })
      currentSeq.selectedIds = ''
    },

    processSeqs(seqType) {
      return this.seqConfig[seqType].map(config => ({
        role: config.role,
        seq: config.seq.map(item => ({
          id: item.id,
          description: item.description
        }))
      }))
    },

    async handleSubmit() {
      // 转换数据结构
      const example_API_seqs = {
        normal_seqs: this.processSeqs('normal_seqs'),
        malicious_seqs: this.processSeqs('malicious_seqs')
      }

      try {
        const cleanList = this.userApiList.map(({ isAdded, ...rest }) => rest)
        await putUserApiList(this.$route.params.id, {
          user_API_list: cleanList,
          example_API_seqs
        })
        this.$notify.success({ title: '成功', message: 'API列表已提交', duration: 2000 })
        this.configDialogVisible = false
      } catch (error) {
        console.error('提交失败:', error)
        this.$notify.error({ title: '错误', message: '提交失败', duration: 2000 })
      }
    },

    handleConfigClose() {
      // 关闭时清空临时数据
      this.seqConfig = { normal_seqs: [], malicious_seqs: [] }
    },

    async getApiListData() {
      this.listLoading = true
      try {
        const response = await getApiList({ app_id: this.$route.params.id })

        // 初始化发现列表并添加isAdded属性
        this.discoveredApiList = response.data.discovered_API_list.map(item => ({
          ...item,
          isAdded: false
        }))

        this.userApiList = response.data.user_API_list
      } catch (error) {
        console.error('Failed to fetch API list:', error)
      } finally {
        this.listLoading = false
      }
    },
    moveToUserApiList(row) {
      if (row.isAdded) return
      const newItem = { ...row }
      delete newItem.isAdded // 移除临时状态属性
      this.userApiList.push(newItem)
      row.isAdded = true // 更新发现列表项的状态
    },
    removeFromUserApiList(index) {
      const removedItem = this.userApiList[index]
      this.userApiList.splice(index, 1)

      // 更新发现列表对应的项状态
      const foundItem = this.discoveredApiList.find(item => item.id === removedItem.id)
      if (foundItem) foundItem.isAdded = false
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
        // 提交时移除临时状态属性
        const cleanList = this.userApiList.map(({ isAdded, ...rest }) => rest)
        await putUserApiList(this.$route.params.id, {
          user_API_list: cleanList,
          example_API_seqs: []
        })
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
  .seq-config-container {
    max-height: 60vh;
    overflow-y: auto;
    padding: 10px;
  }

  .seq-type {
    margin-bottom: 30px;
    padding: 15px;
    border: 1px solid #ebeef5;
    border-radius: 4px;
  }

  .seq-item {
    margin: 15px 0;
    padding: 15px;
    border: 1px dashed #ddd;
    border-radius: 4px;
  }

  .seq-descriptions {
    margin-top: 10px;
    padding-left: 20px;
  }

  .desc-item {
    display: flex;
    align-items: center;
    margin: 8px 0;
  }

  .api-info {
    min-width: 400px;
    margin-right: 20px;
    color: #409EFF;
    font-weight: 500;
  }

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

  .header-cell {
    max-height: 100px; /* 固定高度 */
    overflow-y: auto; /* 添加垂直滚动条 */
    white-space: pre-wrap; /* 保留换行符 */
    word-break: break-all; /* 长文本自动换行 */
  }

</style>
