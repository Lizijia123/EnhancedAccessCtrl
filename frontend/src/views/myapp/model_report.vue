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
      <el-table-column label="Class" prop="class" align="center" width="120">
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
      const lines = modelReport.split('\n')
      const data = []

      // 解析每一行数据
      lines.forEach(line => {
        if (line.trim() === '' || line.includes('precision')) {
          return // 跳过表头和空行
        }

        const parts = line.split(/\s+/).filter(part => part !== '')
        if (parts.length >= 5) {
          data.push({
            class: parts[0],
            precision: parseFloat(parts[1]),
            recall: parseFloat(parts[2]),
            f1Score: parseFloat(parts[3]),
            support: parseInt(parts[4], 10)
          })
        }
      })

      return data
    }
  }
}
</script>

<style scoped>
  .app-container {
    padding: 20px;
  }
</style>
