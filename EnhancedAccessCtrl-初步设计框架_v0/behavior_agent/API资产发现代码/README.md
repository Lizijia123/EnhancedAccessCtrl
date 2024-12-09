# API资产发现工具
本工具是一种从复杂网络流量中发现API资产的API发现工具，通过API流量模板提取来实现API资产发现。以及通过Method以及API端点进行流量归类。

## 文件说明

### api-discovery.py
该Python脚本实现了以下功能：
- **数据预处理模块**：对API流量数据进行清洗和格式化，以便于后续处理。
- **分析和处理API流量数据模块**：使用Drain3模型对提取的数据进行聚类，根据URL模板将流量数据分组，并输出每个聚类的详细信息。通过Method以及API端点进行流量归类和输出。

### api-discovery.ini
这是一个配置文件，用于设置`Drain3`模型的参数。主要配置项包括：
- **Masking**：定义了模型在处理数据时应用的掩码技术，目的是提高API流量模板提取的准确度。

## 使用说明

1. **安装依赖**：确保您的Python环境中安装了所有必要的库。
2. **配置参数**：根据您的需求编辑`api-discovery.ini`文件中的参数。
3. **运行脚本**：在命令行中运行`api-discovery.py`以启动API流量发现过程。

## 测试说明

1. **测试数据集**：本项目提供默认的测试数据集api_data_set.xlsx，您可以运行api-discovery.py并以该数据集进行测试，然后得到测试结果。
2. **验证数据集**：由于测试数据集来自于开源项目train-ticket，因此本项目采用train-ticket现有的[API文档](https://github.com/FudanSELab/train-ticket/wiki/Service-Guide-and-API-Reference)进行覆盖率和准确率验证。
3. **验证说明**：验证过程主要通过对比模型输出的API模板是否有相应的API进行对应，并且对应结果是否正确。

### 依赖库
请确保您已安装以下依赖库：
- Python 3.x
- 以及其他可能在`api-discovery.py`中使用的第三方库。
