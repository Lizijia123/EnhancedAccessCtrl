<template>
  <div class="app-container">
    <el-table
      :key="tableKey"
      v-loading="listLoading"
      :data="tableData"
      border
      fit
      highlight-current-row
      style="width: 100%;"
    >
      <el-table-column label="" prop="class" align="center" width="120">
        <template slot-scope="{row}">
          <span>{{ row.class }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Precision" width="150px" align="center">
        <template slot-scope="{row}">
          <span>{{ row.precision }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Recall" width="150px" align="center">
        <template slot-scope="{row}">
          <span>{{ row.recall }}</span>
        </template>
      </el-table-column>
      <el-table-column label="F1-Score" width="150px" align="center">
        <template slot-scope="{row}">
          <span>{{ row.f1Score }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Support" width="150px" align="center">
        <template slot-scope="{row}">
          <span>{{ row.support }}</span>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import { getAppDetail } from '@/api/myapp'

export default {
  name: 'ModelReportTable',
  data() {
    return {
      tableKey: 0,
      tableData: [], // 表格数据
      listLoading: true // 加载状态
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      this.listLoading = true
      try {
        const id = this.$route.params.id
        const response = await getAppDetail({ id })
        const modelReport = response.data.model_report

        // 解析 model_report
        this.tableData = this.parseModelReport(modelReport)
      } catch (error) {
        console.error('Failed to fetch app details:', error)
      } finally {
        this.listLoading = false
      }
    },
    parseModelReport(modelReport) {
      // 定义行标题和对应的数据索引
      const structure = [
        { class: '0', indexes: [0, 1, 2, 3] },
        { class: '1', indexes: [4, 5, 6, 7] },
        { class: 'accuracy', indexes: [-1, -1, 8, 9] },
        { class: 'macro avg', indexes: [10, 11, 12, 13] },
        { class: 'weighted avg', indexes: [14, 15, 16, 17] }
      ]

      return structure.map(item => {
        const values = item.indexes.map(idx => {
          const num = modelReport[idx]
          return Number.isFinite(num) ? num.toFixed(2) : null
        })
        return {
          class: item.class,
          precision: values[0] ?? null,
          recall: values[1] ?? null,
          f1Score: values[2] ?? null,
          support: values[3] ? Number(values[3]) : null
        }
      })
    }
  }
}
</script>

<style scoped>
  .app-container {
    padding: 20px;
  }
</style>
