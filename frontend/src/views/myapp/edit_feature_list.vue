<template>
  <div class="app-container">
    <!-- Confirm 按钮 -->
    <div class="confirm-button">
      <el-button type="primary" @click="handleConfirm">
        Save Features
      </el-button>
    </div>

    <!-- DetectFeature 部分 -->
    <div class="detect-feature-section">
      <h3>DetectFeature</h3>
      <el-table v-loading="listLoading" :data="detectFeatureList" border fit highlight-current-row style="width: 100%">
        <el-table-column align="center" label="ID" width="80">
          <template slot-scope="{row}">
            <span>{{ row.id }}</span>
          </template>
        </el-table-column>

        <el-table-column width="120px" align="center" label="Feature Name">
          <template slot-scope="{row}">
            <span>{{ row.name }}</span>
          </template>
        </el-table-column>

        <el-table-column min-width="300px" label="Description">
          <template slot-scope="{row}">
            <span>{{ row.description }}</span>
          </template>
        </el-table-column>

        <el-table-column align="center" label="Select" width="120">
          <template slot-scope="{row}">
            <el-checkbox v-model="row.selected" />
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- SeqOccurTimeFeature 部分 -->
    <div class="seq-feature-section">
      <h3>SeqOccurTimeFeature       <el-button type="primary" size="small" @click="addSeqFeatureRow">+</el-button></h3>
      <el-table v-loading="listLoading" :data="seqOccurTimeFeatureList" border fit highlight-current-row style="width: 100%">
        <el-table-column align="center" label="Feature Name" width="120px">
          <template slot-scope="{row}">
            <el-input v-model="row.name" size="small" />
          </template>
        </el-table-column>

        <el-table-column min-width="300px" label="Description">
          <template slot-scope="{row}">
            <el-input v-model="row.description" size="small" />
          </template>
        </el-table-column>

        <el-table-column min-width="300px" label="String List">
          <template slot-scope="{row}">
            <div v-for="(item, index) in row.string_list" :key="index" class="string-item">
              <el-input v-model="row.string_list[index]" size="small" />
              <el-button
                type="danger"
                size="small"
                icon="el-icon-delete"
                @click="removeString(row, index)"
              />
            </div>
            <div class="add-string">
              <el-input v-model="row.newString" placeholder="Enter a new string" size="small" />
              <el-button
                type="primary"
                size="small"
                icon="el-icon-plus"
                @click="addString(row)"
              >
                Add
              </el-button>
            </div>
          </template>
        </el-table-column>

        <el-table-column align="center" label="Actions" width="120">
          <template slot-scope="{row, $index}">
            <el-button
              type="danger"
              size="small"
              icon="el-icon-delete"
              @click="removeSeqFeatureRow($index)"
            />
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script>
import { getFeatureList, saveFeatureList } from '@/api/myapp'

// 预置的 6 个 DetectFeature 选项
const PRESET_DETECT_FEATURES = [
  { id: 1, name: 'MeanUrlParamsCount', description: 'MeanUrlParamsCount', type: 'DetectFeature' },
  { id: 2, name: 'RepeatUrlVisitCount', description: 'RepeatUrlVisitCount', type: 'DetectFeature' },
  { id: 3, name: 'DeepPageVisitRate', description: 'DeepPageVisitRate', type: 'DetectFeature' },
  { id: 4, name: 'MeanUrlPathDepth', description: 'MeanUrlPathDepth', type: 'DetectFeature' },
  { id: 5, name: 'MeanUrlLength', description: 'MeanUrlLength', type: 'DetectFeature' },
  { id: 6, name: 'UniquePageVisitCount', description: 'UniquePageVisitCount', type: 'DetectFeature' }
]

export default {
  name: 'EditFeatureList',
  data() {
    return {
      listLoading: true,
      detectFeatureList: [], // DetectFeature 列表
      seqOccurTimeFeatureList: [] // SeqOccurTimeFeature 列表
    }
  },
  created() {
    this.getList()
  },
  methods: {
    async getList() {
      this.listLoading = true
      try {
        const response = await getFeatureList({ app_id: this.$route.params.id })
        const featureList = response.data.detect_feature_list

        // 初始化 DetectFeature 列表
        this.detectFeatureList = PRESET_DETECT_FEATURES.map(presetItem => {
          const matchedItem = featureList.find(item => item.id === presetItem.id)
          return {
            ...presetItem,
            selected: !!matchedItem // 根据返回值是否存在决定 selected 属性
          }
        })

        // 初始化 SeqOccurTimeFeature 列表
        this.seqOccurTimeFeatureList = featureList
          .filter(item => item.type === 'SeqOccurTimeFeature')
          .map(item => ({
            ...item,
            newString: '' // 用于添加新字符串
          }))
      } catch (error) {
        console.error('Failed to fetch feature list:', error)
      } finally {
        this.listLoading = false
      }
    },
    // 添加字符串
    addString(row) {
      if (row.newString.trim() !== '') {
        row.string_list.push(row.newString.trim())
        row.newString = ''
      }
    },
    // 删除字符串
    removeString(row, index) {
      row.string_list.splice(index, 1)
    },
    // 添加 SeqOccurTimeFeature 行
    addSeqFeatureRow() {
      this.seqOccurTimeFeatureList.push({
        name: '',
        description: '',
        type: 'SeqOccurTimeFeature',
        string_list: [],
        newString: ''
      })
    },
    // 删除 SeqOccurTimeFeature 行
    removeSeqFeatureRow(index) {
      this.seqOccurTimeFeatureList.splice(index, 1)
    },
    // 提交表单
    async handleConfirm() {
      const id = this.$route.params.id // 获取当前页面的 ID

      // 构造提交数据
      const payload = {
        detect_feature_list: [
          ...this.detectFeatureList
            .filter(item => item.selected) // 只提交选中的 DetectFeature
            .map(item => ({
              id: item.id,
              name: item.name,
              description: item.description,
              type: item.type
            })),
          ...this.seqOccurTimeFeatureList
            .filter(item => item.string_list.length > 0) // 只提交有字符串的 SeqOccurTimeFeature
            .map(item => ({
              name: item.name,
              description: item.description,
              type: item.type,
              string_list: item.string_list // 提交所有字符串
            }))
        ]
      }

      try {
        // 调用保存接口
        await saveFeatureList(id, payload)

        // 提交成功后返回上级页面
        this.$message({
          message: '提交成功',
          type: 'success'
        })
        this.$router.go(-1) // 返回上级页面
      } catch (error) {
        console.error('提交失败:', error)
        this.$message({
          message: '提交失败',
          type: 'error'
        })
      }
    }
  }
}
</script>

<style scoped>
  .app-container {
    padding: 20px;
  }

  .confirm-button {
    margin-bottom: 20px;
  }

  .detect-feature-section,
  .seq-feature-section {
    margin-bottom: 40px;
  }

  h3 {
    margin-bottom: 20px;
    color: #409EFF;
  }

  .string-item {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
  }

  .string-item .el-input {
    flex: 1;
    margin-right: 10px;
  }

  .add-string {
    display: flex;
    align-items: center;
    margin-top: 10px;
  }

  .add-string .el-input {
    flex: 1;
    margin-right: 10px;
  }
</style>
