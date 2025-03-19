<template>
  <div class="dashboard">
    <h2>record_percentages</h2>
    <!-- 时间窗口饼图 -->
    <div class="charts">
      <div v-for="(windowData, windowName) in recordPercentages" :key="windowName" class="chart-container">
        <h3>{{ windowName }}</h3>
        <div v-if="windowData.total > 0" :ref="'chart_' + windowName" class="chart" />
        <div v-else class="no-data">没有数据</div>
      </div>
    </div>

    <!-- 间隔 -->
    <div class="table-gap" />

    <!-- traffic_data_percentages 饼图 -->
    <h2>traffic_data_percentages</h2>
    <div class="charts">
      <div v-for="(windowData, windowName) in trafficDataPercentages" :key="windowName" class="chart-container">
        <h3>{{ windowName }}</h3>
        <div v-if="windowData.total > 0" :ref="'traffic_chart_' + windowName" class="chart" />
        <div v-else class="no-data">没有数据</div>
      </div>
    </div>

    <!-- API检测报告列表 -->
    <div class="api-reports">
      <h2>API检测报告</h2>
      <el-table :data="apiReports" style="width: 100%">
        <el-table-column prop="API_id" label="API ID" width="100" />
        <el-table-column prop="method" label="方法" width="120" />
        <el-table-column prop="sample_url" label="URL" />
        <el-table-column label="操作" width="150">
          <template slot-scope="scope">
            <el-button type="primary" size="small" @click="showApiChartModal(scope.row)">
              查看检测分布
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 检测记录列表 -->
    <div ref="detectionTaskTitle" class="detection-records">
      <h2>检测记录</h2>
      <el-table :data="detectionRecords" style="width: 100%">
        <el-table-column prop="id" label="ID" width="100" />
        <el-table-column prop="detection_result" label="检测结果" width="150" />
        <el-table-column prop="started_at" label="开始时间" />
        <el-table-column prop="ended_at" label="结束时间" />
        <el-table-column prop="traffic_data_size" label="流量数据大小" />
        <el-table-column label="操作" width="150">
          <template slot-scope="scope">
            <el-button type="primary" size="mini" @click="showDetailedRecords(scope.row)">
              全部检测记录
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <pagination v-show="totalRecords > 0" :auto-scroll="false" :total="totalRecords" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="fetchDetectionRecords" />
    </div>

    <!-- 弹窗 -->
    <el-dialog :visible.sync="chartModalVisible" :title="chartModalTitle" width="80%">
      <div v-if="chartModalVisible" class="chart-modal-content">
        <div v-for="(data, timeWindow) in chartModalData" :key="timeWindow" class="chart-modal-item">
          <h4>{{ timeWindow }}</h4>
          <div v-if="data.total > 0" :ref="'api_chart_' + timeWindow" class="chart" />
          <div v-else class="no-data">没有数据</div>
        </div>
      </div>
    </el-dialog>

    <!-- 弹窗：详细检测记录 -->
    <el-dialog :visible.sync="detailedRecordsModalVisible" title="详细检测记录" width="80%">
      <el-table :data="detailedRecords" style="width: 100%">
        <el-table-column prop="accessed_at" label="访问时间" />
        <el-table-column prop="method" label="方法" width="120" />
        <el-table-column prop="url" label="URL" />
        <el-table-column label="请求头" width="300">
          <template slot-scope="{ row }">
            <div class="header-cell">
              {{ row.header }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="data" label="请求数据" />
        <el-table-column prop="status_code" label="状态码" width="100" />
        <el-table-column prop="detection_result" label="检测结果" width="120" />
      </el-table>
      <pagination v-show="detailedTotalRecords > 0" :auto-scroll="false" :total="detailedTotalRecords" :page.sync="detailedListQuery.page" :limit.sync="detailedListQuery.limit" @pagination="fetchDetailedDetectionRecords" />
    </el-dialog>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import { getDetectionReport, getDetectionRecords, getDetailedDetectionRecords } from '@/api/myapp'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination

export default {
  name: 'Report',
  components: { Pagination },
  data() {
    return {
      report: {
        record_percentages: {},
        traffic_data_percentages: {},
        API_report: []
      },
      chartModalVisible: false, // 控制弹窗显示
      chartModalTitle: '', // 弹窗标题
      chartModalData: null, // 弹窗数据
      apiCharts: [], // api弹窗实例
      detectionRecords: [], // 检测记录数据
      totalRecords: 0, // 总记录数
      listQuery: {
        page: 1,
        page_size: 20
      },
      detailedRecordsModalVisible: false, // 控制详细检测记录弹窗显示
      detailedRecords: [], // 详细检测记录数据
      detailedTotalRecords: 0, // 详细检测记录总数
      detailedListQuery: {
        page: 1,
        page_size: 10,
        detection_record_id: null // 当前选中的检测记录ID
      }
    }
  },
  computed: {
    recordPercentages() {
      return this.report.record_percentages
    },
    trafficDataPercentages() {
      return this.report.traffic_data_percentages
    },
    apiReports() {
      return this.report.API_report
    }
  },
  mounted() {
    this.fetchDetectionRecords()
  },
  async created() {
    this.apiCharts = []
    const originalData = await getDetectionReport(this.$route.params.id)
    this.report = originalData.data.report

    this.$nextTick(() => {
      this.initCharts()
      this.initTrafficCharts()
    })
  },
  methods: {
    initCharts() {
      Object.keys(this.recordPercentages).forEach(windowName => {
        if (this.$refs[`chart_${windowName}`] === undefined) return
        const chartDom = this.$refs[`chart_${windowName}`][0]
        const myChart = echarts.init(chartDom)
        const windowData = this.recordPercentages[windowName]

        const option = {
          tooltip: {
            trigger: 'item'
          },
          series: [
            {
              name: '检测结果',
              type: 'pie',
              radius: '50%',
              data: Object.keys(windowData.percentages || {}).map(key => ({
                name: key,
                value: windowData.counts[key]
              })),
              emphasis: {
                itemStyle: {
                  shadowBlur: 10,
                  shadowOffsetX: 0,
                  shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
              }
            }
          ]
        }

        myChart.setOption(option)
      })
    },
    initTrafficCharts() {
      Object.keys(this.trafficDataPercentages).forEach(windowName => {
        if (this.$refs[`traffic_chart_${windowName}`] === undefined) return
        const chartDom = this.$refs[`traffic_chart_${windowName}`][0]
        const myChart = echarts.init(chartDom)
        const windowData = this.trafficDataPercentages[windowName]

        const option = {
          tooltip: {
            trigger: 'item'
          },
          series: [
            {
              name: '流量检测结果',
              type: 'pie',
              radius: '50%',
              data: Object.keys(windowData.percentages || {}).map(key => ({
                name: key,
                value: windowData.counts[key]
              })),
              emphasis: {
                itemStyle: {
                  shadowBlur: 10,
                  shadowOffsetX: 0,
                  shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
              }
            }
          ]
        }

        myChart.setOption(option)
      })
    },
    initApiCharts() {
      this.$nextTick(() => {
        Object.keys(this.chartModalData).forEach(windowName => {
          if (this.$refs[`api_chart_${windowName}`] === undefined || this.$refs[`api_chart_${windowName}`].length === 0) return
          const chartDom = this.$refs[`api_chart_${windowName}`][0]
          const myChart = echarts.init(chartDom)
          const windowData = this.chartModalData[windowName]
          const option = {
            tooltip: {
              trigger: 'item'
            },
            series: [
              {
                name: '检测结果',
                type: 'pie',
                radius: '50%',
                data: Object.keys(windowData.percentages || {}).map(key => ({
                  name: key,
                  value: windowData.counts[key]
                })),
                emphasis: {
                  itemStyle: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                  }
                }
              }
            ]
          }

          myChart.setOption(option)
          this.apiCharts[windowName] = myChart
        })
      })
    },
    showApiChartModal(api) {
      this.chartModalTitle = `API ${api.API_id} - ${api.method} ${api.sample_url} 检测分布`
      this.chartModalData = api.traffic_data_percentages
      this.chartModalVisible = true
      this.initApiCharts()
    },
    async fetchDetectionRecords() {
      try {
        const response = await getDetectionRecords({
          app_id: this.$route.params.id,
          page: this.listQuery.page,
          page_size: this.listQuery.page_size
        })
        if (response.code === 200) {
          this.detectionRecords = response.data.detection_records
          this.totalRecords = response.data.total
        }
      } catch (error) {
        console.error('获取检测记录失败:', error)
      }
      if (this.listQuery.page !== 1) {
        this.$nextTick(() => {
          // 滚动到标题位置
          this.$refs.detectionTaskTitle.scrollIntoView({ behavior: 'smooth' })
        })
      }
    },
    // 显示详细检测记录弹窗
    showDetailedRecords(record) {
      this.detailedListQuery.detection_record_id = record.id
      this.detailedRecordsModalVisible = true
      this.fetchDetailedDetectionRecords()
    },
    // 获取详细检测记录
    async fetchDetailedDetectionRecords() {
      try {
        const response = await getDetailedDetectionRecords({
          app_id: this.$route.params.id,
          detection_record_id: this.detailedListQuery.detection_record_id,
          page: this.detailedListQuery.page,
          page_size: this.detailedListQuery.page_size
        })
        if (response.code === 200) {
          this.detailedRecords = response.data.traffic_data_list
          this.detailedTotalRecords = response.data.total
        }
      } catch (error) {
        console.error('获取详细检测记录失败:', error)
      }
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.charts {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.chart-container {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.chart {
  width: 100%;
  height: 300px;
}

.api-reports {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-modal-content {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.chart-modal-item {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.no-data {
  text-align: center;
  font-size: 16px;
  color: #999;
}

h2,
h3,
h4 {
  color: #2c3e50;
  margin-bottom: 15px;
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

.detection-records {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-top: 30px;
}

.header-cell {
  max-height: 100px; /* 固定高度 */
  overflow-y: auto; /* 添加垂直滚动条 */
  white-space: pre-wrap; /* 保留换行符 */
  word-break: break-all; /* 长文本自动换行 */
}
</style>
