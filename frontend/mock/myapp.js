module.exports = [
  {
    url: '/api/target-app-list/',
    type: 'get',
    response: config => {
      return {
        'code': 200,
        'data': {
          'target_app_list': [
            {
              'id': 1,
              'APP_name': 'Updated Test App',
              'APP_url': 'http://49.234.6.241:5230/',
              'user_behavior_cycle': 1,
              'SFWAP_address': '49.234.6.241:5000',
              'description': 'This is an updated test application',
              'created_at': '2025-02-26 04:03:44',
              'updated_at': '2025-03-09 06:04:16',
              'is_draft': false,
              'last_API_discovery_at': '2025-03-09 14:15:42',
              'last_model_construction_at': '2025-03-09 13:29:53',
              'login_credentials': [
                {
                  'user_role': 'admin',
                  'username': 'adminuser',
                  'password': 'adminpass'
                },
                {
                  'user_role': 'ordinary_user',
                  'username': 'normaluser',
                  'password': 'normalpass'
                },
                {
                  'user_role': 'unlogged_in_user',
                  'username': 'unloggeduser',
                  'password': 'normalpass'
                }
              ],
              'detect_state': 'PAUSED',
              'model_report': '"              precision    recall  f1-score   support\n\n           0       0.67      1.00      0.80         2\n           1       0.00      0.00      0.00         1\n\n    accuracy                           0.67         3\n   macro avg       0.33      0.50      0.40         3\nweighted avg       0.44      0.67      0.53         3\n"',
              'enhanced_detection_enabled': true,
              'combined_data_duration': 30
            },
            {
              'id': 4,
              'APP_name': 'New Test App',
              'APP_url': 'http://testapp.com',
              'user_behavior_cycle': 1,
              'SFWAP_address': '49.234.6.241:5000',
              'description': 'This is a test application',
              'created_at': '2025-03-09 14:13:22',
              'updated_at': '2025-03-09 14:13:22',
              'is_draft': false,
              'last_API_discovery_at': null,
              'last_model_construction_at': null,
              'login_credentials': [
                {
                  'user_role': 'admin',
                  'username': 'adminuser',
                  'password': 'adminpass'
                },
                {
                  'user_role': 'user',
                  'username': 'normaluser',
                  'password': 'normalpass'
                }
              ],
              'detect_state': 'API_LIST_TO_DISCOVER',
              'model_report': null,
              'enhanced_detection_enabled': null,
              'combined_data_duration': null
            }
          ],
          'total': 2
        }
      }
    }
  },
  {
    url: '/api/target-app/',
    type: 'get',
    response: config => {
      const { id } = config.query
      return {
        'code': 200,
        'data': {
          'id': id,
          'APP_name': 'Updated Test App ' + id,
          'APP_url': 'http://49.234.6.241:5230/',
          'user_behavior_cycle': 1,
          'SFWAP_address': '49.234.6.241:5000',
          'description': 'This is an updated test application',
          'created_at': '2025-02-26 04:03:44',
          'updated_at': '2025-03-09 06:04:16',
          'is_draft': false,
          'last_API_discovery_at': '2025-03-09 06:05:34',
          'last_model_construction_at': '2025-03-09 13:29:53',
          'login_credentials': [
            {
              'user_role': 'admin',
              'username': 'adminuser',
              'password': 'adminpass'
            },
            {
              'user_role': 'ordinary_user',
              'username': 'normaluser',
              'password': 'normalpass'
            },
            {
              'user_role': 'unlogged_in_user',
              'username': 'unloggeduser',
              'password': 'normalpass'
            }
          ],
          'detect_state': 'PAUSED',
          'model_report': '"              precision    recall  f1-score   support\n\n           0       0.67      1.00      0.80         2\n           1       0.00      0.00      0.00         1\n\n    accuracy                           0.67         3\n   macro avg       0.33      0.50      0.40         3\nweighted avg       0.44      0.67      0.53         3\n"',
          'enhanced_detection_enabled': true,
          'combined_data_duration': 30
        }
      }
    }
  },
  {
    url: '/api/target-app/',
    type: 'put',
    response: config => {
      return {
        'code': 200,
        'message': 'Target application updated successfully'
      }
    }
  },
  {
    url: '/api/target-app/',
    type: 'post',
    response: config => {
      return {
        'code': 200,
        'message': 'Target application created successfully'
      }
    }
  },
  {
    url: '/api/detection/features/',
    type: 'get',
    response: config => {
      return {
        'code': 200,
        'data': {
          'detect_feature_list': [
            {
              'id': 1,
              'name': 'MeanUrlParamsCount',
              'description': 'MeanUrlParamsCount',
              'type': 'DetectFeature'
            },
            {
              'id': 2,
              'name': 'RepeatUrlVisitCount',
              'description': 'RepeatUrlVisitCount',
              'type': 'DetectFeature'
            },
            {
              'id': 3,
              'name': 'DeepPageVisitRate',
              'description': 'DeepPageVisitRate',
              'type': 'DetectFeature'
            },
            {
              'id': 4,
              'name': 'MeanUrlPathDepth',
              'description': 'MeanUrlPathDepth',
              'type': 'DetectFeature'
            },
            {
              'id': 5,
              'name': 'MeanUrlLength',
              'description': 'MeanUrlLength',
              'type': 'DetectFeature'
            },
            {
              'id': 6,
              'name': 'UniquePageVisitCount',
              'description': 'UniquePageVisitCount',
              'type': 'DetectFeature'
            },
            {
              'id': 7,
              'name': 'seq_occ_feat',
              'description': 'seq_occ_feature',
              'type': 'SeqOccurTimeFeature',
              'string_list': [
                'a',
                'b'
              ]
            }
          ],
          'total': 6
        }
      }
    }
  },
  {
    url: '/api/detection/features/',
    type: 'put',
    response: config => {
      return {
        'code': 200,
        'message': 'Detect features updated successfully'
      }
    }
  },
  {
    url: '/api/detection/config/',
    type: 'put',
    response: config => {
      return {
        'code': 200,
        'message': 'Detection configuration successful'
      }
    }
  },
  {
    url: '/api/api-discovery/start/',
    type: 'get',
    response: config => {
      return {
        'code': 200,
        'data': {
          'message': 'Manual API discovery started successfully'
        }
      }
    }
  },
  {
    url: '/api/api-discovery/finish/',
    type: 'get',
    response: config => {
      return {
        'code': 200,
        'data': {
          'message': 'Manual API discovery started successfully'
        }
      }
    }
  },
  {
    url: '/api/api-discovery/cancel/',
    type: 'get',
    response: config => {
      return {
        'code': 200,
        'data': {
          'message': 'Manual API discovery started successfully'
        }
      }
    }
  },
  {
    url: '/api/api-discovery/status/',
    type: 'get',
    response: config => {
      return {
        'code': 200,
        'data': {
          'api_discovery_status': 'AVAILABLE'
        }
      }
    }
  },
  {
    url: '/api/api-discovery/manual/status/',
    type: 'get',
    response: config => {
      return {
        'code': 200,
        'data': {
          'status': 'ON_GOING'
        }
      }
    }
  },
  {
    url: '/api/model-construct/data-collection-status/',
    type: 'get',
    response: config => {
      return {
        'code': 200,
        'data': {
          'status': 'COMPLETED'
        }
      }
    }
  },
  {
    url: '/api/model-construct',
    type: 'get',
    response: config => {
      return {
        'code': 200,
        'message': 'Model construction successful',
        'data': {
          'report': '              precision    recall  f1-score   support\n\n           0       0.50      1.00      0.67         2\n           1       0.00      0.00      0.00         2\n\n    accuracy                           0.50         4\n   macro avg       0.25      0.50      0.33         4\nweighted avg       0.25      0.50      0.33         4\n',
          'error_API_list': []
        }
      }
    }
  },
  {
    url: '/api/detection/pause/',
    type: 'get',
    response: config => {
      return {
        'code': 200,
        'message': 'Detection paused successfully'
      }
    }
  },
  {
    url: '/api/detection/start/',
    type: 'get',
    response: config => {
      return {
        'code': 200,
        'message': 'Detection started successfully'
      }
    }
  },
  {
    url: '/api/detection/record/combination/',
    type: 'get',
    response: config => {
      return {
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
    }
  },
  {
    url: '/api/api-lists/',
    type: 'get',
    response: config => {
      return {
        'code': 200,
        'data': {
          'discovered_API_list': [],
          'discovered_API_list_total': 0,
          'user_API_list': [
            {
              'id': 1591,
              'sample_url': 'http://47.97.114.24:5230/api/v1/resource/16',
              'sample_request_data': '{}',
              'request_method': 'DELETE',
              'function_description': 'Please fill in the function description',
              'permission_info': 'Please fill in the permission info',
              'path_segment_list': [
                {
                  'name': 'api',
                  'is_path_variable': false
                },
                {
                  'name': 'v1',
                  'is_path_variable': false
                },
                {
                  'name': 'resource',
                  'is_path_variable': false
                },
                {
                  'name': '<NUM>',
                  'is_path_variable': true
                }
              ],
              'request_param_list': [],
              'request_data_fields': []
            },
            {
              'id': 1592,
              'sample_url': 'http://47.97.114.24:5230/api/v1/memo/30',
              'sample_request_data': '{}',
              'request_method': 'DELETE',
              'function_description': 'Please fill in the function description',
              'permission_info': 'Please fill in the permission info',
              'path_segment_list': [
                {
                  'name': 'api',
                  'is_path_variable': false
                },
                {
                  'name': 'v1',
                  'is_path_variable': false
                },
                {
                  'name': 'memo',
                  'is_path_variable': false
                },
                {
                  'name': '<NUM>',
                  'is_path_variable': true
                }
              ],
              'request_param_list': [],
              'request_data_fields': []
            }
          ],
          'user_API_list_total': 2
        }
      }
    }
  }
]

