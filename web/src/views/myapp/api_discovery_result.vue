<template>
  <div class="app-container">
    <!-- Discovered API 表格 -->
    <div class="table-section">
      <h2 class="table-title">Discovered API</h2>
      <div class="table-wrapper">
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
          <el-table-column label="Method" width="150px" align="center">
            <template slot-scope="{row}">
              <span>{{ row.timestamp | parseTime('{y}-{m}-{d} {h}:{i}') }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Path" min-width="150px">
            <template slot-scope="{row}">
              <span class="link-type">{{ row.title }}</span>
              <el-tag>{{ row.type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Discription" width="110px" align="center">
            <template slot-scope="{row}">
              <span>{{ row.author }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 间隔 -->
    <div class="table-gap"></div>

    <!-- User Api List 表格 -->
    <div class="table-section">
      <h2 class="table-title">User Api List</h2>
      <div class="table-wrapper">
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
          <el-table-column label="Method" width="150px" align="center">
            <template slot-scope="{row}">
              <span>{{ row.timestamp | parseTime('{y}-{m}-{d} {h}:{i}') }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Path" min-width="150px">
            <template slot-scope="{row}">
              <span class="link-type">{{ row.title }}</span>
              <el-tag>{{ row.type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Description" width="110px" align="center">
            <template slot-scope="{row}">
              <span>{{ row.author }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="210px" align="center">
            <template slot-scope="{row,$index}">
              <router-link :to="'/myapp/api_edit/'+row.id" class="link-type">
                <el-button type="primary" size="mini">
                  Edit
                </el-button>
              </router-link>
              <el-button type="dang er" size="mini">
                Delete
              </el-button>

            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<style scoped>
  .app-container {
    padding: 20px;
    background: #fff;
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
<script>
import { fetchList, fetchPv, createArticle, updateArticle } from '@/api/article'
import waves from '@/directive/waves' // waves directive
import { parseTime } from '@/utils'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination

const calendarTypeOptions = [
  { key: 'CN', display_name: 'China' },
  { key: 'US', display_name: 'USA' },
  { key: 'JP', display_name: 'Japan' },
  { key: 'EU', display_name: 'Eurozone' }
]

// arr to obj, such as { CN : "China", US : "USA" }
const calendarTypeKeyValue = calendarTypeOptions.reduce((acc, cur) => {
  acc[cur.key] = cur.display_name
  return acc
}, {})

export default {
  name: 'ComplexTable',
  components: { Pagination },
  directives: { waves },
  data() {
    return {
      tableKey: 0,
      list: null,
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 20,
        importance: undefined,
        title: undefined,
        type: undefined,
        sort: '+id'
      },
      importanceOptions: [1, 2, 3],
      calendarTypeOptions,
      showReviewer: false,
      temp: {
        id: undefined,
        importance: 1,
        remark: '',
        timestamp: new Date(),
        title: '',
        type: '',
        status: 'published'
      },
      pvData: []
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      fetchList(this.listQuery).then(response => {
        this.list = response.data.items
        this.total = response.data.total

        // Just to simulate the time of the request
        setTimeout(() => {
          this.listLoading = false
        }, 1.5 * 1000)
      })
    }
  }
}
</script>
