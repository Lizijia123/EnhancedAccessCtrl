# SFWAP
lzj毕设

工程-前端：EnhancedAccessCtrl-FrontEnd

工程-后端：SFWAPProject

工程-算法端：algorithm-side-interfaces

实验-数据收集&模型构建主要流程：algorithm-side（实验部分代码）






SFWAP(SmartFlow WebAccess Pro)是一个Web应用的访问控制管控平台原型，架构由前端、服务端（Django框架）与算法端（Flask）框架组成。

用户可以在SFWAP平台下载SFWAP-Detector安装包（对应于algorithm-side-interfaces代码），并根据指引将其安装部署在**目标Web应用**的服务端；同时配置使目标应用的Web流量都经由mitmproxy代理。SFWAP-Detector运行时会持续从mitmproxy收集并分析目标应用的应用层流量，识别其中是否存在越权安全风险，并持续形成目标应用的检测报告。

用户使用SFWAP的基本流程包括：

- 注册登录
- 下载安装SFWAP-Detector，并根据目标Web应用的实际情况，修改配置信息，启动运行SFWAP-Detector
- 在SFWAP平台创建“目标应用”：填写基本信息，包括：
  - 目标应用首页URL
  - 目标应用的登录凭据列表（最好保证覆盖各种角色的用户）
  - SFWAP Address：SFWAP-Detector的运行地址（部署的服务器地址:运行端口号）
  - 填写这些信息后，进行部署检测，成功后可以创建新的目标应用
- 在当前目标应用的检测任务页面，根据流程指引，配置相关信息，启动SFWAP检测：
  - Basic Config阶段：确认并完善基础配置信息（与上述的目标应用基本信息相同）
  - API Discovery阶段:
    - 首先进行自动API Discovery：SFWAP-Detector会对目标应用的前端页面进行探测式爬虫；收集爬虫期间的Web流量**S**，并利用API发现算法，从集合S中识别基本的API列表。自动API Discovery的过程比较耗时，用户需要等待。目前还没有取消自动API Discovery的功能
    - 用户查看API Discovery Results：查看从集合S中识别出的API列表
    - 用户进行Manual API Discovery：上述API列表可能无法覆盖目标应用的很多API，因此用户可以进行Manual API Discovery（此前必须至少完成一次自动API Discovery）：启动Manual API Discovery后，用户自行手动操作目标应用的前端页面，同时SFWAP-Detector收集流量数据并**加入到集合S**；终止Manual API Discovery时，SFWAP-Detector对扩增后的集合S进行API发现。此时用户可以再次查看API Discovery Results：如果其中依然不包含用户所需的API，则可以再次进行Manual API Discovery，直到API Discovery Results中包含所需的API
    - 用户Edit API List（此前必须至少完成一次自动API Discovery）：从集合S中识别出的API列表（对应于目标应用的discovered_API_list属性）中API的格式有误差，且部分API可能不是用户所需的；因此用户需要在discovered_API_list的基础上（或者对照discovered_API_list进行）编辑（只能修改或删除其中的API，不能新增：如果需要新增，需先进行Manual API Discovery以保证discovered_API_list覆盖了所需的新API），得到**user_API_list**（user_API_list会初始化为discovered_API_list）
    - 用户可以重复Edit API List：重复更新user_API_list：用户每次进行Edit API List时，SFWAP-Detector都会开始异步地进行安全异常检测模型的训练数据集扩增（从流量集合S中收集user_API_list中各个API的调用时可取参数集合，利用大模型生成正常/恶意的用户仿真API调用序列，进行API序列参数填充和交互校验；如果无法从S中收集某个API的可取参数集合，会加以记录）
    - 用户可以重复进行自动API Discovery，每次都会重新自动探测式爬虫，得到流量数据S1，同时与用户全部历史Manual API Discovery流量记录S2合并形成集合S，并将目标应用的discovered_API_list更新为从S识别的API列表。如果user_API_list为空，还会将discovered_API_list复制到user_API_list（否则不会复制）
  - Model Construction阶段：
    - 用户请求Start Model Construction（此前必须至少完成一次自动API Discovery）：请求时，如果SFWAP-Detector未完成训练数据扩增，用户需要等待。完成数据扩增后，SFWAP-Detector构建模型，并展示模型报告（性能数据），以及问题API列表（用户可以从user_API_list中删除或者修改这些API，并重新进行模型构建）
    - 用户Edit Feature List：编辑异常检测的机器学习算法采用的特征提取集合。任何目标应用的detect_feature_list都会初始化为一个basic feature list（通用特征全集，其中的feature的类型均为基本的DetectFeature，而非SeqOccurTimeFeature）。用户可以对其进行删减；也可以新增特征（新增的特征必须为SeqOccurTimeFeature类型，且每个特征有一个string_list属性）
    - 用户重新进行Start Model Construction。模型构建可以进行多次。如果更新了user_API_list或者更新了detect_feature_list，需要（最好）重新Start Model Construction以保证数据同步
  - Start Detection阶段：用户编辑Detection Config并启动检测（此前需要至少完成一次自动API Discovery，至少完成一次Model Construction）。用户可以暂停检测。在检测进行中时，不能进行Basic Config&API Discovery&Model Construction阶段的操作（需要先暂停检测）
- 用户在当前目标应用的报告页面查看检测报告





