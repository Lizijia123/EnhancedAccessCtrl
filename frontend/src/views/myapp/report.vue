<template>
  <div class="dashboard">
    <!-- 总体统计 -->
    <div class="stats">
      <h2>安全检测统计</h2>
      <p>总检测记录：{{ report.total_detection_record_count }}</p>
      <p>总流量数据：{{ report.total_traffic_data_count }}</p>
    </div>

    <!-- 时间窗口饼图 -->
    <div class="charts">
      <div v-for="(windowData, windowName) in timeWindows" :key="windowName" class="chart-container">
        <h3>{{ windowName }} 检测分布</h3>
        <div :ref="'chart_' + windowName" class="chart" />
      </div>
    </div>

    <!-- API检测报告列表 -->
    <div class="api-reports">
      <h2>API检测报告</h2>
      <div v-for="api in apiReports" :key="api.API_id" class="api-item">
        <h3>{{ api.method }} {{ api.sample_url }}</h3>
        <p>API ID: {{ api.API_id }}</p>
        <div v-for="(data, timeWindow) in api.time_window" :key="timeWindow">
          <p>{{ timeWindow }} 总请求: {{ data.total }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'Report',
  data() {
    return {
      report: {
        // 原始数据结构
        time_window_record_result_percentages: {},
        time_window_traffic_data_result_percentages: {},
        API_report: []
      }
    }
  },
  computed: {
    timeWindows() {
      return this.report.time_window_record_result_percentages
    },
    apiReports() {
      return this.report.API_report.map(api => ({
        ...api,
        time_window: api.time_window_API_traffic_data_result_percentages
      }))
    }
  },
  mounted() {
    this.initCharts()
  },
  async created() {
    // 这里模拟数据加载，实际应从API获取
    const originalData = {
      'code': 200,
      'data': {
        'report': {
          'total_detection_record_count': 33,
          'history_record_result_percentages': {
            'ALLOW': 100.0
          },
          'time_window_record_result_percentages': {
            'Ten Minutes': {
              'total': 0
            },
            'An Hour': {
              'total': 0
            },
            'Six Hours': {
              'total': 0
            },
            'One Day': {
              'total': 0
            },
            'Three Days': {
              'total': 0
            },
            'One Week': {
              'total': 27,
              'percentages': {
                'ALLOW': 100.0
              },
              'counts': {
                'ALLOW': 27
              }
            },
            'One Month': {
              'total': 33,
              'percentages': {
                'ALLOW': 100.0
              },
              'counts': {
                'ALLOW': 33
              }
            }
          },
          'total_traffic_data_count': 233,
          'history_traffic_data_result_percentages': {
            'NORMAL': 100.0
          },
          'time_window_traffic_data_result_percentages': {
            'Ten Minutes': {
              'total': 0
            },
            'An Hour': {
              'total': 0
            },
            'Six Hours': {
              'total': 0
            },
            'One Day': {
              'total': 0
            },
            'Three Days': {
              'total': 0
            },
            'One Week': {
              'total': 155,
              'percentages': {
                'NORMAL': 100.0
              },
              'counts': {
                'NORMAL': 155
              }
            },
            'One Month': {
              'total': 233,
              'percentages': {
                'NORMAL': 100.0
              },
              'counts': {
                'NORMAL': 233
              }
            }
          },
          'API_report': [
            {
              'API_id': 1953,
              'method': 'DELETE',
              'sample_url': 'http://47.97.114.24:5230/api/v1/resource/16',
              'time_window_API_traffic_data_result_percentages': {
                'Ten Minutes': {
                  'total': 0
                },
                'An Hour': {
                  'total': 0
                },
                'Six Hours': {
                  'total': 0
                },
                'One Day': {
                  'total': 0
                },
                'Three Days': {
                  'total': 0
                },
                'One Week': {
                  'total': 0
                },
                'One Month': {
                  'total': 0
                }
              }
            },
            {
              'API_id': 1954,
              'method': 'DELETE',
              'sample_url': 'http://47.97.114.24:5230/api/v1/memo/30',
              'time_window_API_traffic_data_result_percentages': {
                'Ten Minutes': {
                  'total': 0
                },
                'An Hour': {
                  'total': 0
                },
                'Six Hours': {
                  'total': 0
                },
                'One Day': {
                  'total': 0
                },
                'Three Days': {
                  'total': 0
                },
                'One Week': {
                  'total': 0
                },
                'One Month': {
                  'total': 0
                }
              }
            }
          ]
        },
        'detection_records': [
          {
            'detection_result': 'ALLOW',
            'started_at': '2025-02-26T07:17:11Z',
            'ended_at': '2025-02-26T07:17:54Z',
            'traffic_data_list': [
              {
                'accessed_at': '2025-02-26T07:17:11Z',
                'method': 'POST',
                'url': 'http://49.234.6.241:5230/memos.api.v1.UserService/GetUserByUsername',
                'header': '{\'Accept\': \'*/*\', \'Accept-Encoding\': \'gzip, deflate\', \'Accept-Language\': \'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6\', \'Connection\': \'keep-alive\', \'Content-Length\': \'10\', \'Cookie\': \'memos.access-token=eyJhbGciOiJIUzI1NiIsImtpZCI6InYxIiwidHlwIjoiSldUIn0.eyJuYW1lIjoiIiwiaXNzIjoibWVtb3MiLCJzdWIiOiIyIiwiYXVkIjpbInVzZXIuYWNjZXNzLXRva2VuIl0sImV4cCI6MTc0MTE0Mjc1MiwiaWF0IjoxNzQwNTM3OTUyfQ.SpZbRip1hroiGDT1bc6WkBQlevKDAr2l3gTD5Kg7u7s\', \'Host\': \'49.234.6.241:5230\', \'Origin\': \'http://49.234.6.241:5230\', \'Referer\': \'http://49.234.6.241:5230/u/lzj\', \'User-Agent\': \'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0\', \'X-Mitmproxy-Processed\': \'true\', \'content-type\': \'application/grpc-web+proto\', \'x-grpc-web\': \'1\'}',
                'data': '{}',
                'status_code': 200,
                'detection_result': 'NORMAL'
              },
              {
                'accessed_at': '2025-02-26T07:17:12Z',
                'method': 'POST',
                'url': 'http://49.234.6.241:5230/memos.api.v1.MemoService/ListMemos',
                'header': '{\'Accept\': \'*/*\', \'Accept-Encoding\': \'gzip, deflate\', \'Accept-Language\': \'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6\', \'Connection\': \'keep-alive\', \'Content-Length\': \'20\', \'Cookie\': \'memos.access-token=eyJhbGciOiJIUzI1NiIsImtpZCI6InYxIiwidHlwIjoiSldUIn0.eyJuYW1lIjoiIiwiaXNzIjoibWVtb3MiLCJzdWIiOiIyIiwiYXVkIjpbInVzZXIuYWNjZXNzLXRva2VuIl0sImV4cCI6MTc0MTE0Mjc1MiwiaWF0IjoxNzQwNTM3OTUyfQ.SpZbRip1hroiGDT1bc6WkBQlevKDAr2l3gTD5Kg7u7s\', \'Host\': \'49.234.6.241:5230\', \'Origin\': \'http://49.234.6.241:5230\', \'Referer\': \'http://49.234.6.241:5230/u/lzj\', \'User-Agent\': \'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0\', \'X-Mitmproxy-Processed\': \'true\', \'content-type\': \'application/grpc-web+proto\', \'x-grpc-web\': \'1\'}',
                'data': '{}',
                'status_code': 200,
                'detection_result': 'NORMAL'
              },
              {
                'accessed_at': '2025-02-26T07:17:12Z',
                'method': 'POST',
                'url': 'http://49.234.6.241:5230/memos.api.v1.InboxService/ListInboxes',
                'header': '{\'Accept\': \'*/*\', \'Accept-Encoding\': \'gzip, deflate\', \'Accept-Language\': \'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6\', \'Connection\': \'keep-alive\', \'Content-Length\': \'5\', \'Cookie\': \'memos.access-token=eyJhbGciOiJIUzI1NiIsImtpZCI6InYxIiwidHlwIjoiSldUIn0.eyJuYW1lIjoiIiwiaXNzIjoibWVtb3MiLCJzdWIiOiIyIiwiYXVkIjpbInVzZXIuYWNjZXNzLXRva2VuIl0sImV4cCI6MTc0MTE0Mjc1MiwiaWF0IjoxNzQwNTM3OTUyfQ.SpZbRip1hroiGDT1bc6WkBQlevKDAr2l3gTD5Kg7u7s\', \'Host\': \'49.234.6.241:5230\', \'Origin\': \'http://49.234.6.241:5230\', \'Referer\': \'http://49.234.6.241:5230/inbox\', \'User-Agent\': \'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0\', \'X-Mitmproxy-Processed\': \'true\', \'content-type\': \'application/grpc-web+proto\', \'x-grpc-web\': \'1\'}',
                'data': '{}',
                'status_code': 200,
                'detection_result': 'NORMAL'
              },
              {
                'accessed_at': '2025-02-26T07:17:19Z',
                'method': 'POST',
                'url': 'http://49.234.6.241:5230/memos.api.v1.MemoService/ListMemos',
                'header': '{\'Accept\': \'*/*\', \'Accept-Encoding\': \'gzip, deflate\', \'Accept-Language\': \'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6\', \'Connection\': \'keep-alive\', \'Content-Length\': \'20\', \'Cookie\': \'memos.access-token=eyJhbGciOiJIUzI1NiIsImtpZCI6InYxIiwidHlwIjoiSldUIn0.eyJuYW1lIjoiIiwiaXNzIjoibWVtb3MiLCJzdWIiOiIyIiwiYXVkIjpbInVzZXIuYWNjZXNzLXRva2VuIl0sImV4cCI6MTc0MTE0Mjc1MiwiaWF0IjoxNzQwNTM3OTUyfQ.SpZbRip1hroiGDT1bc6WkBQlevKDAr2l3gTD5Kg7u7s\', \'Host\': \'49.234.6.241:5230\', \'Origin\': \'http://49.234.6.241:5230\', \'Referer\': \'http://49.234.6.241:5230/archived\', \'User-Agent\': \'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0\', \'X-Mitmproxy-Processed\': \'true\', \'content-type\': \'application/grpc-web+proto\', \'x-grpc-web\': \'1\'}',
                'data': '{}',
                'status_code': 200,
                'detection_result': 'NORMAL'
              },
              {
                'accessed_at': '2025-02-26T07:17:19Z',
                'method': 'POST',
                'url': 'http://49.234.6.241:5230/memos.api.v1.MemoService/ListMemos',
                'header': '{\'Accept\': \'*/*\', \'Accept-Encoding\': \'gzip, deflate\', \'Accept-Language\': \'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6\', \'Connection\': \'keep-alive\', \'Content-Length\': \'11\', \'Cookie\': \'memos.access-token=eyJhbGciOiJIUzI1NiIsImtpZCI6InYxIiwidHlwIjoiSldUIn0.eyJuYW1lIjoiIiwiaXNzIjoibWVtb3MiLCJzdWIiOiIyIiwiYXVkIjpbInVzZXIuYWNjZXNzLXRva2VuIl0sImV4cCI6MTc0MTE0Mjc1MiwiaWF0IjoxNzQwNTM3OTUyfQ.SpZbRip1hroiGDT1bc6WkBQlevKDAr2l3gTD5Kg7u7s\', \'Host\': \'49.234.6.241:5230\', \'Origin\': \'http://49.234.6.241:5230\', \'Referer\': \'http://49.234.6.241:5230/explore\', \'User-Agent\': \'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0\', \'X-Mitmproxy-Processed\': \'true\', \'content-type\': \'application/grpc-web+proto\', \'x-grpc-web\': \'1\'}',
                'data': '{}',
                'status_code': 200,
                'detection_result': 'NORMAL'
              },
              {
                'accessed_at': '2025-02-26T07:17:20Z',
                'method': 'POST',
                'url': 'http://49.234.6.241:5230/memos.api.v1.UserService/ListAllUserStats',
                'header': '{\'Accept\': \'*/*\', \'Accept-Encoding\': \'gzip, deflate\', \'Accept-Language\': \'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6\', \'Connection\': \'keep-alive\', \'Content-Length\': \'5\', \'Cookie\': \'memos.access-token=eyJhbGciOiJIUzI1NiIsImtpZCI6InYxIiwidHlwIjoiSldUIn0.eyJuYW1lIjoiIiwiaXNzIjoibWVtb3MiLCJzdWIiOiIyIiwiYXVkIjpbInVzZXIuYWNjZXNzLXRva2VuIl0sImV4cCI6MTc0MTE0Mjc1MiwiaWF0IjoxNzQwNTM3OTUyfQ.SpZbRip1hroiGDT1bc6WkBQlevKDAr2l3gTD5Kg7u7s\', \'Host\': \'49.234.6.241:5230\', \'Origin\': \'http://49.234.6.241:5230\', \'Referer\': \'http://49.234.6.241:5230/explore\', \'User-Agent\': \'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0\', \'X-Mitmproxy-Processed\': \'true\', \'content-type\': \'application/grpc-web+proto\', \'x-grpc-web\': \'1\'}',
                'data': '{}',
                'status_code': 200,
                'detection_result': 'NORMAL'
              },
              {
                'accessed_at': '2025-02-26T07:17:26Z',
                'method': 'POST',
                'url': 'http://49.234.6.241:5230/memos.api.v1.UserService/GetUserByUsername',
                'header': '{\'Accept\': \'*/*\', \'Accept-Encoding\': \'gzip, deflate\', \'Accept-Language\': \'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6\', \'Connection\': \'keep-alive\', \'Content-Length\': \'10\', \'Cookie\': \'memos.access-token=eyJhbGciOiJIUzI1NiIsImtpZCI6InYxIiwidHlwIjoiSldUIn0.eyJuYW1lIjoiIiwiaXNzIjoibWVtb3MiLCJzdWIiOiIyIiwiYXVkIjpbInVzZXIuYWNjZXNzLXRva2VuIl0sImV4cCI6MTc0MTE0Mjc1MiwiaWF0IjoxNzQwNTM3OTUyfQ.SpZbRip1hroiGDT1bc6WkBQlevKDAr2l3gTD5Kg7u7s\', \'Host\': \'49.234.6.241:5230\', \'Origin\': \'http://49.234.6.241:5230\', \'Referer\': \'http://49.234.6.241:5230/u/lzj\', \'User-Agent\': \'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0\', \'X-Mitmproxy-Processed\': \'true\', \'content-type\': \'application/grpc-web+proto\', \'x-grpc-web\': \'1\'}',
                'data': '{}',
                'status_code': 200,
                'detection_result': 'NORMAL'
              },
              {
                'accessed_at': '2025-02-26T07:17:26Z',
                'method': 'POST',
                'url': 'http://49.234.6.241:5230/memos.api.v1.MemoService/ListMemos',
                'header': '{\'Accept\': \'*/*\', \'Accept-Encoding\': \'gzip, deflate\', \'Accept-Language\': \'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6\', \'Connection\': \'keep-alive\', \'Content-Length\': \'20\', \'Cookie\': \'memos.access-token=eyJhbGciOiJIUzI1NiIsImtpZCI6InYxIiwidHlwIjoiSldUIn0.eyJuYW1lIjoiIiwiaXNzIjoibWVtb3MiLCJzdWIiOiIyIiwiYXVkIjpbInVzZXIuYWNjZXNzLXRva2VuIl0sImV4cCI6MTc0MTE0Mjc1MiwiaWF0IjoxNzQwNTM3OTUyfQ.SpZbRip1hroiGDT1bc6WkBQlevKDAr2l3gTD5Kg7u7s\', \'Host\': \'49.234.6.241:5230\', \'Origin\': \'http://49.234.6.241:5230\', \'Referer\': \'http://49.234.6.241:5230/u/lzj\', \'User-Agent\': \'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0\', \'X-Mitmproxy-Processed\': \'true\', \'content-type\': \'application/grpc-web+proto\', \'x-grpc-web\': \'1\'}',
                'data': '{}',
                'status_code': 200,
                'detection_result': 'NORMAL'
              },
              {
                'accessed_at': '2025-02-26T07:17:27Z',
                'method': 'POST',
                'url': 'http://49.234.6.241:5230/memos.api.v1.ResourceService/ListResources',
                'header': '{\'Accept\': \'*/*\', \'Accept-Encoding\': \'gzip, deflate\', \'Accept-Language\': \'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6\', \'Connection\': \'keep-alive\', \'Content-Length\': \'5\', \'Cookie\': \'memos.access-token=eyJhbGciOiJIUzI1NiIsImtpZCI6InYxIiwidHlwIjoiSldUIn0.eyJuYW1lIjoiIiwiaXNzIjoibWVtb3MiLCJzdWIiOiIyIiwiYXVkIjpbInVzZXIuYWNjZXNzLXRva2VuIl0sImV4cCI6MTc0MTE0Mjc1MiwiaWF0IjoxNzQwNTM3OTUyfQ.SpZbRip1hroiGDT1bc6WkBQlevKDAr2l3gTD5Kg7u7s\', \'Host\': \'49.234.6.241:5230\', \'Origin\': \'http://49.234.6.241:5230\', \'Referer\': \'http://49.234.6.241:5230/resources\', \'User-Agent\': \'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0\', \'X-Mitmproxy-Processed\': \'true\', \'content-type\': \'application/grpc-web+proto\', \'x-grpc-web\': \'1\'}',
                'data': '{}',
                'status_code': 200,
                'detection_result': 'NORMAL'
              },
              {
                'accessed_at': '2025-02-26T07:17:30Z',
                'method': 'POST',
                'url': 'http://49.234.6.241:5230/memos.api.v1.UserService/GetUserByUsername',
                'header': '{\'Accept\': \'*/*\', \'Accept-Encoding\': \'gzip, deflate\', \'Accept-Language\': \'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6\', \'Connection\': \'keep-alive\', \'Content-Length\': \'10\', \'Cookie\': \'memos.access-token=eyJhbGciOiJIUzI1NiIsImtpZCI6InYxIiwidHlwIjoiSldUIn0.eyJuYW1lIjoiIiwiaXNzIjoibWVtb3MiLCJzdWIiOiIyIiwiYXVkIjpbInVzZXIuYWNjZXNzLXRva2VuIl0sImV4cCI6MTc0MTE0Mjc1MiwiaWF0IjoxNzQwNTM3OTUyfQ.SpZbRip1hroiGDT1bc6WkBQlevKDAr2l3gTD5Kg7u7s\', \'Host\': \'49.234.6.241:5230\', \'Origin\': \'http://49.234.6.241:5230\', \'Referer\': \'http://49.234.6.241:5230/u/lzj\', \'User-Agent\': \'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0\', \'X-Mitmproxy-Processed\': \'true\', \'content-type\': \'application/grpc-web+proto\', \'x-grpc-web\': \'1\'}',
                'data': '{}',
                'status_code': 200,
                'detection_result': 'NORMAL'
              },
              {
                'accessed_at': '2025-02-26T07:17:31Z',
                'method': 'POST',
                'url': 'http://49.234.6.241:5230/memos.api.v1.MemoService/ListMemos',
                'header': '{\'Accept\': \'*/*\', \'Accept-Encoding\': \'gzip, deflate\', \'Accept-Language\': \'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6\', \'Connection\': \'keep-alive\', \'Content-Length\': \'20\', \'Cookie\': \'memos.access-token=eyJhbGciOiJIUzI1NiIsImtpZCI6InYxIiwidHlwIjoiSldUIn0.eyJuYW1lIjoiIiwiaXNzIjoibWVtb3MiLCJzdWIiOiIyIiwiYXVkIjpbInVzZXIuYWNjZXNzLXRva2VuIl0sImV4cCI6MTc0MTE0Mjc1MiwiaWF0IjoxNzQwNTM3OTUyfQ.SpZbRip1hroiGDT1bc6WkBQlevKDAr2l3gTD5Kg7u7s\', \'Host\': \'49.234.6.241:5230\', \'Origin\': \'http://49.234.6.241:5230\', \'Referer\': \'http://49.234.6.241:5230/u/lzj\', \'User-Agent\': \'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0\', \'X-Mitmproxy-Processed\': \'true\', \'content-type\': \'application/grpc-web+proto\', \'x-grpc-web\': \'1\'}',
                'data': '{}',
                'status_code': 200,
                'detection_result': 'NORMAL'
              },
              {
                'accessed_at': '2025-02-26T07:17:31Z',
                'method': 'POST',
                'url': 'http://49.234.6.241:5230/memos.api.v1.InboxService/ListInboxes',
                'header': '{\'Accept\': \'*/*\', \'Accept-Encoding\': \'gzip, deflate\', \'Accept-Language\': \'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6\', \'Connection\': \'keep-alive\', \'Content-Length\': \'5\', \'Cookie\': \'memos.access-token=eyJhbGciOiJIUzI1NiIsImtpZCI6InYxIiwidHlwIjoiSldUIn0.eyJuYW1lIjoiIiwiaXNzIjoibWVtb3MiLCJzdWIiOiIyIiwiYXVkIjpbInVzZXIuYWNjZXNzLXRva2VuIl0sImV4cCI6MTc0MTE0Mjc1MiwiaWF0IjoxNzQwNTM3OTUyfQ.SpZbRip1hroiGDT1bc6WkBQlevKDAr2l3gTD5Kg7u7s\', \'Host\': \'49.234.6.241:5230\', \'Origin\': \'http://49.234.6.241:5230\', \'Referer\': \'http://49.234.6.241:5230/inbox\', \'User-Agent\': \'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0\', \'X-Mitmproxy-Processed\': \'true\', \'content-type\': \'application/grpc-web+proto\', \'x-grpc-web\': \'1\'}',
                'data': '{}',
                'status_code': 200,
                'detection_result': 'NORMAL'
              },
              {
                'accessed_at': '2025-02-26T07:17:34Z',
                'method': 'POST',
                'url': 'http://49.234.6.241:5230/memos.api.v1.UserService/GetUserByUsername',
                'header': '{\'Accept\': \'*/*\', \'Accept-Encoding\': \'gzip, deflate\', \'Accept-Language\': \'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6\', \'Connection\': \'keep-alive\', \'Content-Length\': \'10\', \'Cookie\': \'memos.access-token=eyJhbGciOiJIUzI1NiIsImtpZCI6InYxIiwidHlwIjoiSldUIn0.eyJuYW1lIjoiIiwiaXNzIjoibWVtb3MiLCJzdWIiOiIyIiwiYXVkIjpbInVzZXIuYWNjZXNzLXRva2VuIl0sImV4cCI6MTc0MTE0Mjc1MiwiaWF0IjoxNzQwNTM3OTUyfQ.SpZbRip1hroiGDT1bc6WkBQlevKDAr2l3gTD5Kg7u7s\', \'Host\': \'49.234.6.241:5230\', \'Origin\': \'http://49.234.6.241:5230\', \'Referer\': \'http://49.234.6.241:5230/u/lzj\', \'User-Agent\': \'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0\', \'X-Mitmproxy-Processed\': \'true\', \'content-type\': \'application/grpc-web+proto\', \'x-grpc-web\': \'1\'}',
                'data': '{}',
                'status_code': 200,
                'detection_result': 'NORMAL'
              },
              {
                'accessed_at': '2025-02-26T07:17:34Z',
                'method': 'POST',
                'url': 'http://49.234.6.241:5230/memos.api.v1.MemoService/ListMemos',
                'header': '{\'Accept\': \'*/*\', \'Accept-Encoding\': \'gzip, deflate\', \'Accept-Language\': \'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6\', \'Connection\': \'keep-alive\', \'Content-Length\': \'20\', \'Cookie\': \'memos.access-token=eyJhbGciOiJIUzI1NiIsImtpZCI6InYxIiwidHlwIjoiSldUIn0.eyJuYW1lIjoiIiwiaXNzIjoibWVtb3MiLCJzdWIiOiIyIiwiYXVkIjpbInVzZXIuYWNjZXNzLXRva2VuIl0sImV4cCI6MTc0MTE0Mjc1MiwiaWF0IjoxNzQwNTM3OTUyfQ.SpZbRip1hroiGDT1bc6WkBQlevKDAr2l3gTD5Kg7u7s\', \'Host\': \'49.234.6.241:5230\', \'Origin\': \'http://49.234.6.241:5230\', \'Referer\': \'http://49.234.6.241:5230/u/lzj\', \'User-Agent\': \'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0\', \'X-Mitmproxy-Processed\': \'true\', \'content-type\': \'application/grpc-web+proto\', \'x-grpc-web\': \'1\'}',
                'data': '{}',
                'status_code': 200,
                'detection_result': 'NORMAL'
              },
              {
                'accessed_at': '2025-02-26T07:17:35Z',
                'method': 'POST',
                'url': 'http://49.234.6.241:5230/memos.api.v1.MemoService/ListMemos',
                'header': '{\'Accept\': \'*/*\', \'Accept-Encoding\': \'gzip, deflate\', \'Accept-Language\': \'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6\', \'Connection\': \'keep-alive\', \'Content-Length\': \'11\', \'Cookie\': \'memos.access-token=eyJhbGciOiJIUzI1NiIsImtpZCI6InYxIiwidHlwIjoiSldUIn0.eyJuYW1lIjoiIiwiaXNzIjoibWVtb3MiLCJzdWIiOiIyIiwiYXVkIjpbInVzZXIuYWNjZXNzLXRva2VuIl0sImV4cCI6MTc0MTE0Mjc1MiwiaWF0IjoxNzQwNTM3OTUyfQ.SpZbRip1hroiGDT1bc6WkBQlevKDAr2l3gTD5Kg7u7s\', \'Host\': \'49.234.6.241:5230\', \'Origin\': \'http://49.234.6.241:5230\', \'Referer\': \'http://49.234.6.241:5230/explore\', \'User-Agent\': \'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0\', \'X-Mitmproxy-Processed\': \'true\', \'content-type\': \'application/grpc-web+proto\', \'x-grpc-web\': \'1\'}',
                'data': '{}',
                'status_code': 200,
                'detection_result': 'NORMAL'
              },
              {
                'accessed_at': '2025-02-26T07:17:35Z',
                'method': 'POST',
                'url': 'http://49.234.6.241:5230/memos.api.v1.UserService/ListAllUserStats',
                'header': '{\'Accept\': \'*/*\', \'Accept-Encoding\': \'gzip, deflate\', \'Accept-Language\': \'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6\', \'Connection\': \'keep-alive\', \'Content-Length\': \'5\', \'Cookie\': \'memos.access-token=eyJhbGciOiJIUzI1NiIsImtpZCI6InYxIiwidHlwIjoiSldUIn0.eyJuYW1lIjoiIiwiaXNzIjoibWVtb3MiLCJzdWIiOiIyIiwiYXVkIjpbInVzZXIuYWNjZXNzLXRva2VuIl0sImV4cCI6MTc0MTE0Mjc1MiwiaWF0IjoxNzQwNTM3OTUyfQ.SpZbRip1hroiGDT1bc6WkBQlevKDAr2l3gTD5Kg7u7s\', \'Host\': \'49.234.6.241:5230\', \'Origin\': \'http://49.234.6.241:5230\', \'Referer\': \'http://49.234.6.241:5230/explore\', \'User-Agent\': \'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0\', \'X-Mitmproxy-Processed\': \'true\', \'content-type\': \'application/grpc-web+proto\', \'x-grpc-web\': \'1\'}',
                'data': '{}',
                'status_code': 200,
                'detection_result': 'NORMAL'
              },
              {
                'accessed_at': '2025-02-26T07:17:38Z',
                'method': 'POST',
                'url': 'http://49.234.6.241:5230/memos.api.v1.MemoService/ListMemos',
                'header': '{\'Accept\': \'*/*\', \'Accept-Encoding\': \'gzip, deflate\', \'Accept-Language\': \'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6\', \'Connection\': \'keep-alive\', \'Content-Length\': \'20\', \'Cookie\': \'memos.access-token=eyJhbGciOiJIUzI1NiIsImtpZCI6InYxIiwidHlwIjoiSldUIn0.eyJuYW1lIjoiIiwiaXNzIjoibWVtb3MiLCJzdWIiOiIyIiwiYXVkIjpbInVzZXIuYWNjZXNzLXRva2VuIl0sImV4cCI6MTc0MTE0Mjc1MiwiaWF0IjoxNzQwNTM3OTUyfQ.SpZbRip1hroiGDT1bc6WkBQlevKDAr2l3gTD5Kg7u7s\', \'Host\': \'49.234.6.241:5230\', \'Origin\': \'http://49.234.6.241:5230\', \'Referer\': \'http://49.234.6.241:5230/archived\', \'User-Agent\': \'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0\', \'X-Mitmproxy-Processed\': \'true\', \'content-type\': \'application/grpc-web+proto\', \'x-grpc-web\': \'1\'}',
                'data': '{}',
                'status_code': 200,
                'detection_result': 'NORMAL'
              },
              {
                'accessed_at': '2025-02-26T07:17:39Z',
                'method': 'POST',
                'url': 'http://49.234.6.241:5230/memos.api.v1.InboxService/ListInboxes',
                'header': '{\'Accept\': \'*/*\', \'Accept-Encoding\': \'gzip, deflate\', \'Accept-Language\': \'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6\', \'Connection\': \'keep-alive\', \'Content-Length\': \'5\', \'Cookie\': \'memos.access-token=eyJhbGciOiJIUzI1NiIsImtpZCI6InYxIiwidHlwIjoiSldUIn0.eyJuYW1lIjoiIiwiaXNzIjoibWVtb3MiLCJzdWIiOiIyIiwiYXVkIjpbInVzZXIuYWNjZXNzLXRva2VuIl0sImV4cCI6MTc0MTE0Mjc1MiwiaWF0IjoxNzQwNTM3OTUyfQ.SpZbRip1hroiGDT1bc6WkBQlevKDAr2l3gTD5Kg7u7s\', \'Host\': \'49.234.6.241:5230\', \'Origin\': \'http://49.234.6.241:5230\', \'Referer\': \'http://49.234.6.241:5230/inbox\', \'User-Agent\': \'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0\', \'X-Mitmproxy-Processed\': \'true\', \'content-type\': \'application/grpc-web+proto\', \'x-grpc-web\': \'1\'}',
                'data': '{}',
                'status_code': 200,
                'detection_result': 'NORMAL'
              },
              {
                'accessed_at': '2025-02-26T07:17:54Z',
                'method': 'POST',
                'url': 'http://49.234.6.241:5230/memos.api.v1.UserService/GetUserByUsername',
                'header': '{\'Accept\': \'*/*\', \'Accept-Encoding\': \'gzip, deflate\', \'Accept-Language\': \'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6\', \'Connection\': \'keep-alive\', \'Content-Length\': \'10\', \'Cookie\': \'memos.access-token=eyJhbGciOiJIUzI1NiIsImtpZCI6InYxIiwidHlwIjoiSldUIn0.eyJuYW1lIjoiIiwiaXNzIjoibWVtb3MiLCJzdWIiOiIyIiwiYXVkIjpbInVzZXIuYWNjZXNzLXRva2VuIl0sImV4cCI6MTc0MTE0Mjc1MiwiaWF0IjoxNzQwNTM3OTUyfQ.SpZbRip1hroiGDT1bc6WkBQlevKDAr2l3gTD5Kg7u7s\', \'Host\': \'49.234.6.241:5230\', \'Origin\': \'http://49.234.6.241:5230\', \'Referer\': \'http://49.234.6.241:5230/u/lzj\', \'User-Agent\': \'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0\', \'X-Mitmproxy-Processed\': \'true\', \'content-type\': \'application/grpc-web+proto\', \'x-grpc-web\': \'1\'}',
                'data': '{}',
                'status_code': 200,
                'detection_result': 'NORMAL'
              }
            ]
          },
          {
            'detection_result': 'ALLOW',
            'started_at': '2025-02-26T07:17:55Z',
            'ended_at': '2025-02-26T07:19:33Z',
            'traffic_data_list': [
              {
                'accessed_at': '2025-02-26T07:17:55Z',
                'method': 'POST',
                'url': 'http://49.234.6.241:5230/memos.api.v1.MemoService/ListMemos',
                'header': '{\'Accept\': \'*/*\', \'Accept-Encoding\': \'gzip, deflate\', \'Accept-Language\': \'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6\', \'Connection\': \'keep-alive\', \'Content-Length\': \'20\', \'Cookie\': \'memos.access-token=eyJhbGciOiJIUzI1NiIsImtpZCI6InYxIiwidHlwIjoiSldUIn0.eyJuYW1lIjoiIiwiaXNzIjoibWVtb3MiLCJzdWIiOiIyIiwiYXVkIjpbInVzZXIuYWNjZXNzLXRva2VuIl0sImV4cCI6MTc0MTE0Mjc1MiwiaWF0IjoxNzQwNTM3OTUyfQ.SpZbRip1hroiGDT1bc6WkBQlevKDAr2l3gTD5Kg7u7s\', \'Host\': \'49.234.6.241:5230\', \'Origin\': \'http://49.234.6.241:5230\', \'Referer\': \'http://49.234.6.241:5230/u/lzj\', \'User-Agent\': \'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0\', \'X-Mitmproxy-Processed\': \'true\', \'content-type\': \'application/grpc-web+proto\', \'x-grpc-web\': \'1\'}',
                'data': '{}',
                'status_code': 200,
                'detection_result': 'NORMAL'
              },
              {
                'accessed_at': '2025-02-26T07:17:55Z',
                'method': 'POST',
                'url': 'http://49.234.6.241:5230/memos.api.v1.MemoService/ListMemos',
                'header': '{\'Accept\': \'*/*\', \'Accept-Encoding\': \'gzip, deflate\', \'Accept-Language\': \'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6\', \'Connection\': \'keep-alive\', \'Content-Length\': \'11\', \'Cookie\': \'memos.access-token=eyJhbGciOiJIUzI1NiIsImtpZCI6InYxIiwidHlwIjoiSldUIn0.eyJuYW1lIjoiIiwiaXNzIjoibWVtb3MiLCJzdWIiOiIyIiwiYXVkIjpbInVzZXIuYWNjZXNzLXRva2VuIl0sImV4cCI6MTc0MTE0Mjc1MiwiaWF0IjoxNzQwNTM3OTUyfQ.SpZbRip1hroiGDT1bc6WkBQlevKDAr2l3gTD5Kg7u7s\', \'Host\': \'49.234.6.241:5230\', \'Origin\': \'http://49.234.6.241:5230\', \'Referer\': \'http://49.234.6.241:5230/explore\', \'User-Agent\': \'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0\', \'X-Mitmproxy-Processed\': \'true\', \'content-type\': \'application/grpc-web+proto\', \'x-grpc-web\': \'1\'}',
                'data': '{}',
                'status_code': 200,
                'detection_result': 'NORMAL'
              },
              {
                'accessed_at': '2025-02-26T07:17:55Z',
                'method': 'POST',
                'url': 'http://49.234.6.241:5230/memos.api.v1.UserService/ListAllUserStats',
                'header': '{\'Accept\': \'*/*\', \'Accept-Encoding\': \'gzip, deflate\', \'Accept-Language\': \'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6\', \'Connection\': \'keep-alive\', \'Content-Length\': \'5\', \'Cookie\': \'memos.access-token=eyJhbGciOiJIUzI1NiIsImtpZCI6InYxIiwidHlwIjoiSldUIn0.eyJuYW1lIjoiIiwiaXNzIjoibWVtb3MiLCJzdWIiOiIyIiwiYXVkIjpbInVzZXIuYWNjZXNzLXRva2VuIl0sImV4cCI6MTc0MTE0Mjc1MiwiaWF0IjoxNzQwNTM3OTUyfQ.SpZbRip1hroiGDT1bc6WkBQlevKDAr2l3gTD5Kg7u7s\', \'Host\': \'49.234.6.241:5230\', \'Origin\': \'http://49.234.6.241:5230\', \'Referer\': \'http://49.234.6.241:5230/explore\', \'User-Agent\': \'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0\', \'X-Mitmproxy-Processed\': \'true\', \'content-type\': \'application/grpc-web+proto\', \'x-grpc-web\': \'1\'}',
                'data': '{}',
                'status_code': 200,
                'detection_result': 'NORMAL'
              },
              {
                'accessed_at': '2025-02-26T07:19:33Z',
                'method': 'POST',
                'url': 'http://49.234.6.241:5230/memos.api.v1.InboxService/ListInboxes',
                'header': '{\'Accept\': \'*/*\', \'Accept-Encoding\': \'gzip, deflate\', \'Accept-Language\': \'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6\', \'Connection\': \'keep-alive\', \'Content-Length\': \'5\', \'Cookie\': \'memos.access-token=eyJhbGciOiJIUzI1NiIsImtpZCI6InYxIiwidHlwIjoiSldUIn0.eyJuYW1lIjoiIiwiaXNzIjoibWVtb3MiLCJzdWIiOiIyIiwiYXVkIjpbInVzZXIuYWNjZXNzLXRva2VuIl0sImV4cCI6MTc0MTE0Mjc1MiwiaWF0IjoxNzQwNTM3OTUyfQ.SpZbRip1hroiGDT1bc6WkBQlevKDAr2l3gTD5Kg7u7s\', \'Host\': \'49.234.6.241:5230\', \'Origin\': \'http://49.234.6.241:5230\', \'Referer\': \'http://49.234.6.241:5230/explore\', \'User-Agent\': \'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0\', \'X-Mitmproxy-Processed\': \'true\', \'content-type\': \'application/grpc-web+proto\', \'x-grpc-web\': \'1\'}',
                'data': '{}',
                'status_code': 200,
                'detection_result': 'NORMAL'
              }
            ]
          }
        ],
        'total': 2
      }
    }
    this.report = originalData.data.report
    await this.$nextTick()
    this.initCharts()
  },
  methods: {
    initCharts() {
      Object.keys(this.timeWindows).forEach(windowName => {
        const chartDom = this.$refs[`chart_${windowName}`][0]
        const myChart = echarts.init(chartDom)
        const windowData = this.timeWindows[windowName]

        const option = {
          tooltip: {
            trigger: 'item'
          },
          series: [{
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
          }]
        }

        myChart.setOption(option)
      })
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

  .stats {
    background: #f5f5f5;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 30px;
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
    box-shadow: 0 2px 12px rgba(0,0,0,0.1);
  }

  .chart {
    width: 100%;
    height: 300px;
  }

  .api-reports .api-item {
    background: white;
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }

  h2, h3 {
    color: #2c3e50;
    margin-bottom: 15px;
  }
</style>
