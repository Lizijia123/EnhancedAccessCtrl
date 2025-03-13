<template>
  <div class="app-container">
    <el-table
      :key="tableKey"
      v-loading="listLoading"
      :data="list"
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
      <el-table-column label="项目名称" min-width="150">
        <template slot-scope="{row}">
          <el-tag>{{ row.APP_name }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="更新时间" width="150" align="center">
        <template slot-scope="{row}">
          <span>{{ row.updated_at | parseTime('{y}-{m}-{d} {h}:{i}') }}</span>
        </template>
      </el-table-column>
      <el-table-column label="执行阶段" class-name="status-col" width="200">
        <template slot-scope="{row}">
          <el-tag :type="row.detect_state">
            {{ row.detect_state }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Actions" align="center" width="230" class-name="small-padding fixed-width">
        <template slot-scope="{row}">
          <router-link :to="'/myapp/detail/'+row.id" class="link-type">
            <el-button type="primary" size="mini">
              详情
            </el-button>
          </router-link>
          <router-link :to="'/myapp/report/'+row.id" class="link-type">
            <el-button type="primary" size="mini">
              检测报告
            </el-button>
          </router-link>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />
  </div>
</template>

<script>
import { fetchAppList } from '@/api/myapp'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination

export default {
  name: 'DetectionTask',
  components: { Pagination },
  data() {
    return {
      tableKey: 0,
      list: null,
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 20
      }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      fetchAppList(this.listQuery).then(response => {
        this.list = response.data.target_app_list
        this.total = response.data.total
        this.listLoading = false
      })
    }
  }
}
</script>

<style scoped>
  .app-container {
    padding: 20px;
  }
  .el-button{
    margin-left: 10px;
  }
</style>
