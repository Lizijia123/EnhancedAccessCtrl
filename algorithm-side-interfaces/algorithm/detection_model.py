import os.path
from sklearn.preprocessing import  MinMaxScaler
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.impute import SimpleImputer
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report
from tqdm import tqdm  # ✅ 进度条库

import joblib
import lightgbm as lgb
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd

from algorithm.Dynamtic_Feature_Extraction import FeatureExtractor

class AE_CNN(nn.Module):
    def __init__(self, input_dim):
        super(AE_CNN, self).__init__()

        # **CNN 编码器**
        self.encoder = nn.Sequential(
            nn.Conv1d(in_channels=1, out_channels=16, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2),
            nn.Conv1d(16, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2)
        )

        # **FC 层连接 CNN 输出**
        self.fc_latent = nn.Linear(32 * (input_dim // 4), 64)

        # **解码器**
        self.fc_decoder = nn.Linear(64, 32 * (input_dim // 4))
        self.decoder = nn.Sequential(
            nn.ConvTranspose1d(32, 16, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.ReLU(),
            nn.ConvTranspose1d(16, 1, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.Tanh()
        )

    def forward(self, x):
        x = x.unsqueeze(1)  # 添加通道维度 (batch, 1, features)
        x = self.encoder(x)
        x = x.view(x.size(0), -1)  # 展平
        latent = self.fc_latent(x)
        x = self.fc_decoder(latent)
        x = x.view(x.size(0), 32, -1)  # 变回 CNN 形状
        reconstructed = self.decoder(x)
        return reconstructed.squeeze(1)  # 去掉通道维度 (batch, features)

class AutoEncoder(nn.Module):
    def __init__(self, input_dim, hidden_dim):
        super(AutoEncoder, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(hidden_dim // 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim),
            nn.Tanh()
        )

    def forward(self, x):
        latent = self.encoder(x)
        return self.decoder(latent)  # 只返回重构数据

class Generator(nn.Module):
    def __init__(self, input_dim, hidden_dim):
        super(Generator, self).__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU()
        )
        self.decoder = nn.Sequential(
            nn.Linear(hidden_dim // 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, input_dim),
            nn.Tanh()
        )

    def forward(self, x):
        latent = self.encoder(x)
        return self.decoder(latent), latent  # 返回重构数据 & 编码特征

class Discriminator(nn.Module):
    def __init__(self, input_dim, hidden_dim):
        super(Discriminator, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.model(x)

class VAE_CNN(nn.Module):
    def __init__(self, input_dim, latent_dim=64):
        super(VAE_CNN, self).__init__()

        # **CNN 编码器**
        self.encoder = nn.Sequential(
            nn.Conv1d(in_channels=1, out_channels=16, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2),
            nn.Conv1d(16, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2)
        )

        # **提取 CNN 输出的特征维度**
        self.flatten_dim = (input_dim // 4) * 32  # CNN 经过 2 次池化，变为 1/4 大小

        # **VAE 潜在空间**
        self.fc_mu = nn.Linear(self.flatten_dim, latent_dim)  # 均值
        self.fc_logvar = nn.Linear(self.flatten_dim, latent_dim)  # 方差

        # **解码器**
        self.fc_decoder = nn.Linear(latent_dim, self.flatten_dim)
        self.decoder = nn.Sequential(
            nn.ConvTranspose1d(32, 16, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.ReLU(),
            nn.ConvTranspose1d(16, 1, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.Tanh()
        )

    def reparameterize(self, mu, logvar):
        """ 变分推断的重参数技巧 """
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def forward(self, x):
        x = x.unsqueeze(1)  # (batch, 1, features)
        x = self.encoder(x)
        x = x.view(x.size(0), -1)  # 展平

        # **计算均值和方差**
        mu = self.fc_mu(x)
        logvar = self.fc_logvar(x)

        # **使用 reparameterization trick 采样**
        z = self.reparameterize(mu, logvar)

        # **解码**
        x = self.fc_decoder(z)
        x = x.view(x.size(0), 32, -1)  # 变回 CNN 形状
        reconstructed = self.decoder(x)

        return reconstructed.squeeze(1), mu, logvar  # 返回重构数据 & 潜在变量



class DetectionModel:
    def train_and_save_model(self, features):
        return "Model Report"

    def predict(self, data):
        return []


class AECNN(DetectionModel):
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

     
    def train_and_save_model(self, features):
        train_extractor = FeatureExtractor(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data", "Humhub_train.csv"), features=features)
        test_extractor = FeatureExtractor(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data", "Humhub_test.csv"), features=features)

        # 提取特征
        train_features_df, train_labels = train_extractor.get_features()
        test_features_df, test_labels = test_extractor.get_features()

        # 数据预处理
        scaler = MinMaxScaler(feature_range=(-1, 1))  # 归一化到 [-1, 1]
        train_features_scaled = scaler.fit_transform(train_features_df)
        test_features_scaled = scaler.transform(test_features_df)

        # 处理 NaN/Inf
        train_features_scaled = np.nan_to_num(train_features_scaled, nan=0.0, posinf=1.0, neginf=-1.0)
        test_features_scaled = np.nan_to_num(test_features_scaled, nan=0.0, posinf=1.0, neginf=-1.0)

        # 只使用 "正常" API 请求训练模型
        train_normal_idx = np.where(np.array(train_labels) == 0)[0]
        train_normal_features = torch.tensor(train_features_scaled[train_normal_idx], dtype=torch.float32)

        # 划分训练集（80%）和验证集（20%）
        train_feats, val_feats = train_test_split(train_normal_features, test_size=0.2, random_state=42)

        # 转换为 PyTorch Dataset
        batch_size = 64
        train_loader = torch.utils.data.DataLoader(train_feats, batch_size=batch_size, shuffle=True)
        val_loader = torch.utils.data.DataLoader(val_feats, batch_size=batch_size, shuffle=False)

        # # 设备选择
        # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


        # 初始化 AutoEncoder-CNN
        input_dim = train_normal_features.shape[1]
        ae_cnn = AE_CNN(input_dim).to(self.device)

        # 损失函数 & 优化器
        criterion = nn.MSELoss()
        optimizer = optim.Adam(ae_cnn.parameters(), lr=0.001)

        # 训练 AE-CNN（带验证集）
        best_ae_cnn = None
        best_val_loss = float("inf")
        patience = 5
        patience_counter = 0

        num_epochs = 100
        for epoch in range(num_epochs):
            ae_cnn.train()

            for batch in train_loader:
                batch = batch.to(self.device)

                # **前向传播**
                reconstructed = ae_cnn(batch)

                # **计算损失**
                loss = criterion(reconstructed, batch)

                # **反向传播**
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            # 计算验证损失
            ae_cnn.eval()
            val_loss = 0.0
            with torch.no_grad():
                for val_batch in val_loader:
                    val_batch = val_batch.to(self.device)
                    val_reconstructed = ae_cnn(val_batch)
                    val_loss += criterion(val_reconstructed, val_batch).item()

            val_loss /= len(val_loader)

            print(f"Epoch [{epoch + 1}/{num_epochs}] - Train Loss: {loss.item():.4f} - Val Loss: {val_loss:.4f}")

            # 更新最佳模型
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                best_ae_cnn = ae_cnn
                print("✅ 发现更好的模型，已更新变量！")
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print("⏹️ 早停触发，停止训练！")
                    break

        # 保存最佳模型
        torch.save(best_ae_cnn.state_dict(), os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'AE-CNN', 'best_ae_cnn.pth'))
        # 保存 scaler
        joblib.dump(scaler, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'AE-CNN', 'scaler.pkl'))

        # 加载模型
        loaded_ae_cnn = AE_CNN(input_dim).to(self.device)
        loaded_ae_cnn.load_state_dict(torch.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'AE-CNN', 'best_ae_cnn.pth'), weights_only=False))
        loaded_ae_cnn.eval()

        # 直接用 `loaded_ae_cnn` 计算异常分数
        test_features_tensor = torch.tensor(test_features_scaled, dtype=torch.float32).to(self.device)

        with torch.no_grad():
            reconstructed = loaded_ae_cnn(test_features_tensor)
            anomaly_scores = torch.mean((test_features_tensor - reconstructed) ** 2, dim=1).cpu().numpy()

        # 设定异常检测阈值（用训练数据的 95% 分位数）
        threshold = np.percentile(anomaly_scores, 95)
        # 保存阈值
        np.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'AE-CNN', 'threshold.npy'), threshold)

        preds = (anomaly_scores > threshold).astype(int)  # 1 = 异常, 0 = 正常

        # 评估模型
        from sklearn.metrics import accuracy_score, classification_report

        print(f"\nAE-CNN 测试集准确率: {accuracy_score(test_labels, preds):.4f}")
        report = classification_report(test_labels, preds, digits=4)
        return report

     
    def predict(self, data):
        # 加载 scaler
        scaler = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'AE-CNN', 'scaler.pkl')
        # 加载阈值
        threshold = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'AE-CNN', 'threshold.npy'))
        # 数据预处理
        new_data_scaled = scaler.transform(data)
        new_data_scaled = np.nan_to_num(new_data_scaled, nan=0.0, posinf=1.0, neginf=-1.0)
        new_data_tensor = torch.tensor(new_data_scaled, dtype=torch.float32).to(self.device)

        # 加载模型
        input_dim = new_data_scaled.shape[1]
        model = AE_CNN(input_dim).to(self.device)
        model.load_state_dict(torch.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'AE-CNN', 'best_ae_cnn.pth'), weights_only=False))
        model.eval()

        # 计算异常分数
        with torch.no_grad():
            reconstructed = model(new_data_tensor)
            anomaly_scores = torch.mean((new_data_tensor - reconstructed) ** 2, dim=1).cpu().numpy()

        # 预测结果
        preds = (anomaly_scores > threshold).astype(int)
        return preds


class AEMLP(DetectionModel):
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

     
    def train_and_save_model(self, features):
        train_extractor = FeatureExtractor(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data", "Humhub_train.csv"),
            features=features)
        test_extractor = FeatureExtractor(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data", "Humhub_test.csv"),
            features=features)

        # ✅ 提取特征
        train_features_df, train_labels = train_extractor.get_features()
        test_features_df, test_labels = test_extractor.get_features()

        # ✅ 数据预处理
        scaler = MinMaxScaler(feature_range=(-1, 1))  # 归一化到 [-1, 1]
        train_features_scaled = scaler.fit_transform(train_features_df)
        test_features_scaled = scaler.transform(test_features_df)

        # ✅ 处理 NaN/Inf
        train_features_scaled = np.nan_to_num(train_features_scaled, nan=0.0, posinf=1.0, neginf=-1.0)
        test_features_scaled = np.nan_to_num(test_features_scaled, nan=0.0, posinf=1.0, neginf=-1.0)

        # ✅ 只使用 "正常" API 请求训练模型
        train_normal_idx = np.where(np.array(train_labels) == 0)[0]
        train_normal_features = torch.tensor(train_features_scaled[train_normal_idx], dtype=torch.float32)

        # ✅ 划分训练集（80%）和验证集（20%）
        train_feats, val_feats = train_test_split(train_normal_features, test_size=0.2, random_state=42)

        # ✅ 转换为 PyTorch Dataset
        batch_size = 64
        train_loader = torch.utils.data.DataLoader(train_feats, batch_size=batch_size, shuffle=True)
        val_loader = torch.utils.data.DataLoader(val_feats, batch_size=batch_size, shuffle=False)

        # ✅ 初始化模型
        input_dim = train_normal_features.shape[1]
        hidden_dim = 128
        autoencoder = AutoEncoder(input_dim, hidden_dim).to(self.device)

        # ✅ 损失函数 & 优化器
        criterion = nn.MSELoss()
        optimizer = optim.Adam(autoencoder.parameters(), lr=0.001)
        best_autoencoder = None  # 记录最佳 AE
        best_val_loss = float("inf")  # 记录最低验证损失
        patience = 5  # 早停轮数
        patience_counter = 0  # 早停计数器

        num_epochs = 100
        for epoch in range(num_epochs):
            autoencoder.train()

            for batch in train_loader:
                batch = batch.to(self.device)

                # **前向传播**
                reconstructed = autoencoder(batch)

                # **计算损失**
                loss = criterion(reconstructed, batch)

                # **反向传播**
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            # ✅ 计算验证损失
            autoencoder.eval()
            val_loss = 0.0
            with torch.no_grad():
                for val_batch in val_loader:
                    val_batch = val_batch.to(self.device)
                    val_reconstructed = autoencoder(val_batch)
                    val_loss += criterion(val_reconstructed, val_batch).item()

            val_loss /= len(val_loader)  # 计算平均损失

            print(f"Epoch [{epoch + 1}/{num_epochs}] - Train Loss: {loss.item():.4f} - Val Loss: {val_loss:.4f}")

            # ✅ 更新最佳模型
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0  # 重置早停计数器
                best_autoencoder = autoencoder  # 直接更新变量
                print("✅ 发现更好的模型，已更新变量！")
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print("⏹️ 早停触发，停止训练！")
                    break  # 触发早停，终止训练
        # 使用 os.path.join 修改模型保存路径
        model_save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'AE_MLP',
                                       'best_autoencoder.pth')
        torch.save(best_autoencoder.state_dict(), model_save_path)
        # 使用 os.path.join 修改 scaler 保存路径
        scaler_save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'AE_MLP',
                                        'scaler.pkl')
        joblib.dump(scaler, scaler_save_path)
        # 保存阈值

        # 装载模型
        loaded_autoencoder = AutoEncoder(input_dim, hidden_dim).to(self.device)
        # 使用 os.path.join 修改模型加载路径
        loaded_model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'AE_MLP',
                                         'best_autoencoder.pth')
        loaded_autoencoder.load_state_dict(torch.load(loaded_model_path, weights_only=False))
        loaded_autoencoder.eval()

        # ✅ 直接用 `loaded_autoencoder` 计算异常分数
        test_features_tensor = torch.tensor(test_features_scaled, dtype=torch.float32).to(self.device)

        with torch.no_grad():
            reconstructed = loaded_autoencoder(test_features_tensor)
            anomaly_scores = torch.mean((test_features_tensor - reconstructed) ** 2, dim=1).cpu().numpy()

        # ✅ 设定异常检测阈值（用训练数据的 95% 分位数）
        threshold = np.percentile(anomaly_scores, 95)
        # 使用 os.path.join 修改阈值保存路径
        threshold_save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'AE_MLP',
                                           'threshold.npy')
        np.save(threshold_save_path, threshold)
        preds = (anomaly_scores > threshold).astype(int)  # 1 = 异常, 0 = 正常

        # ✅ 评估模型
        from sklearn.metrics import accuracy_score, classification_report

        print(f"\nAutoEncoder 测试集准确率: {accuracy_score(test_labels, preds):.4f}")
        return classification_report(test_labels, preds, digits=4)

     
    def predict(self, data):
        # 使用 os.path.join 修改 scaler 加载路径
        scaler_load_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'AE_MLP', 'scaler.pkl')
        scaler = joblib.load(scaler_load_path)
        # 加载模型
        input_dim = data.shape[1]
        hidden_dim = 128
        model = AutoEncoder(input_dim, hidden_dim).to(self.device)
        # 使用 os.path.join 修改模型加载路径
        model_load_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'AE_MLP',
                                       'best_autoencoder.pth')
        model.load_state_dict(torch.load(model_load_path, weights_only=False))
        model.eval()
        # 使用 os.path.join 修改阈值加载路径
        threshold_load_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'AE_MLP',
                                           'threshold.npy')
        threshold = np.load(threshold_load_path)

        new_data_scaled = scaler.transform(data)
        new_data_scaled = np.nan_to_num(new_data_scaled, nan=0.0, posinf=1.0, neginf=-1.0)
        new_data_tensor = torch.tensor(new_data_scaled, dtype=torch.float32).to(self.device)

        with torch.no_grad():
            reconstructed = model(new_data_tensor)
            anomaly_scores = torch.mean((new_data_tensor - reconstructed) ** 2, dim=1).cpu().numpy()

        preds = (anomaly_scores > threshold).astype(int)
        return preds


class Ganomaly(DetectionModel):
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

     
    def train_and_save_model(self, features):
        train_extractor = FeatureExtractor(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data", "Humhub_train.csv"),
            features=features)
        test_extractor = FeatureExtractor(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data", "Humhub_test.csv"),
            features=features)

        # ✅ 提取特征
        train_features_df, train_labels = train_extractor.get_features()
        test_features_df, test_labels = test_extractor.get_features()

        # ✅ 数据预处理
        scaler = StandardScaler()
        scaler = MinMaxScaler(feature_range=(-1, 1))  # ✅ 归一化到 [-1, 1]
        train_features_scaled = scaler.fit_transform(train_features_df)
        test_features_scaled = scaler.transform(test_features_df)
        train_features_scaled = np.nan_to_num(train_features_scaled, nan=0.0, posinf=1.0, neginf=-1.0)
        test_features_scaled = np.nan_to_num(test_features_scaled, nan=0.0, posinf=1.0, neginf=-1.0)

        # ✅ 只使用 "正常" API 请求训练模型
        train_normal_idx = np.where(np.array(train_labels) == 0)[0]
        train_normal_features = torch.tensor(train_features_scaled[train_normal_idx], dtype=torch.float32)

        # ✅ 转换为 PyTorch Tensor
        test_features_tensor = torch.tensor(test_features_scaled, dtype=torch.float32)

        # ✅ 初始化模型
        input_dim = train_normal_features.shape[1]
        hidden_dim = 128
        generator = Generator(input_dim, hidden_dim).to(self.device)
        discriminator = Discriminator(input_dim, hidden_dim).to(self.device)

        # ✅ 损失函数 & 优化器
        criterion = nn.MSELoss()
        optimizer_G = optim.Adam(generator.parameters(), lr=0.001)
        optimizer_D = optim.Adam(discriminator.parameters(), lr=0.001)

        # ---------------------------------------------------
        # **3. 训练 `GANomaly` 模型**
        # ---------------------------------------------------
        num_epochs = 100
        batch_size = 64

        # ✅ 划分训练集（80%）和验证集（20%）
        train_feats, val_feats = train_test_split(train_normal_features, test_size=0.2, random_state=42)

        # ✅ 转换为 PyTorch Dataset
        train_dataset = torch.utils.data.TensorDataset(train_feats)
        val_dataset = torch.utils.data.TensorDataset(val_feats)

        # ✅ 训练 & 验证 DataLoader
        batch_size = 64
        train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

        best_generator = None  # 记录最佳生成器
        best_discriminator = None  # 记录最佳判别器
        best_val_loss = float("inf")  # 记录最低的验证损失
        patience = 5  # 早停轮数
        patience_counter = 0  # 早停计数器

        for epoch in range(num_epochs):
            generator.train()
            discriminator.train()

            for batch in train_loader:
                batch = batch[0].to(self.device)

                # **生成器前向传播**
                reconstructed, latent = generator(batch)

                # **判别器训练**
                optimizer_D.zero_grad()
                real_preds = discriminator(batch)  # 真实数据
                fake_preds = discriminator(reconstructed.detach())  # 生成数据
                d_loss = -torch.mean(torch.log(real_preds + 1e-8) + torch.log(1 - fake_preds + 1e-8))
                d_loss.backward()
                optimizer_D.step()

                # **生成器训练**
                optimizer_G.zero_grad()
                g_loss = criterion(reconstructed, batch) + criterion(latent, generator.encoder(reconstructed))
                g_loss.backward()
                optimizer_G.step()

            # ✅ 计算验证损失
            generator.eval()
            val_loss = 0.0
            with torch.no_grad():
                for val_batch in val_loader:
                    val_batch = val_batch[0].to(self.device)
                    val_reconstructed, val_latent = generator(val_batch)
                    val_loss += criterion(val_reconstructed, val_batch).item()

            val_loss /= len(val_loader)  # 计算平均损失

            print(
                f"Epoch [{epoch + 1}/{num_epochs}] - D Loss: {d_loss.item():.4f} - G Loss: {g_loss.item():.4f} - Val Loss: {val_loss:.4f}")

            # ✅ 更新最佳模型变量
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0  # 重置早停计数器
                best_generator = generator  # 直接更新变量
                best_discriminator = discriminator
                print("✅ 发现更好的模型，已更新变量！")
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print("⏹️ 早停触发，停止训练！")
                    break  # 触发早停，终止训练

        # 保存最佳模型及必要参数
        model_save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'Ganomaly',
                                       'best_generator_model.pth')
        torch.save({
            'input_dim': input_dim,
            'hidden_dim': hidden_dim,
            'generator_state_dict': best_generator.state_dict(),
        }, model_save_path)
        scaler_save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'Ganomaly',
                                        'scaler.pkl')
        joblib.dump(scaler, scaler_save_path)

        # 直接用 `loaded_generator` 计算异常分数
        best_generator.eval()
        test_features_tensor = test_features_tensor.to(self.device)

        with torch.no_grad():
            reconstructed, latent = best_generator(test_features_tensor)
            anomaly_scores = torch.mean((test_features_tensor - reconstructed) ** 2, dim=1).cpu().numpy()

        # 设定异常检测阈值（用训练数据的 95% 分位数）
        threshold = np.percentile(anomaly_scores, 95)
        threshold_save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'Ganomaly',
                                           'threshold.npy')
        np.save(threshold_save_path, threshold)

        preds = (anomaly_scores > threshold).astype(int)  # 1 = 异常, 0 = 正常

        # 评估模型
        from sklearn.metrics import accuracy_score, classification_report

        print(f"\nGANomaly 测试集准确率: {accuracy_score(test_labels, preds):.4f}")
        return classification_report(test_labels, preds, digits=4)

     
    def predict(self, data):
        scaler_load_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'Ganomaly', 'scaler.pkl')
        scaler = joblib.load(scaler_load_path)
        # 加载阈值
        threshold_load_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'Ganomaly',
                                           'threshold.npy')
        threshold = np.load(threshold_load_path)
        # 数据预处理
        new_data_scaled = scaler.transform(data)
        new_data_scaled = np.nan_to_num(new_data_scaled, nan=0.0, posinf=1.0, neginf=-1.0)
        new_data_tensor = torch.tensor(new_data_scaled, dtype=torch.float32).to(self.device)

        # 加载模型
        checkpoint = torch.load(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'Ganomaly', 'best_generator_model.pth'), weights_only=False)
        input_dim = checkpoint['input_dim']
        hidden_dim = checkpoint['hidden_dim']
        generator_model = Generator(input_dim, hidden_dim).to(self.device)
        generator_model.load_state_dict(checkpoint['generator_state_dict'])
        generator_model.eval()

        # 计算异常分数
        with torch.no_grad():
            reconstructed, latent = generator_model(new_data_tensor)
            anomaly_scores = torch.mean((new_data_tensor - reconstructed) ** 2, dim=1).cpu().numpy()

        # 预测结果
        preds = (anomaly_scores > threshold).astype(int)
        return preds


class RandomForest(DetectionModel):
    @staticmethod
    def override(func):
        return func

     
    def train_and_save_model(self, features):
        train_extractor = FeatureExtractor(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data", "Humhub_train.csv"),
            features=features)
        test_extractor = FeatureExtractor(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data", "Humhub_test.csv"),
            features=features)

        # 提取特征
        train_features_df, train_labels = train_extractor.get_features()
        test_features_df, test_labels = test_extractor.get_features()

        # 拆分训练集 & 验证集
        train_features_df, val_features_df, train_labels, val_labels = train_test_split(
            train_features_df, train_labels, test_size=0.2, random_state=42
        )

        # ✅ 打印最终使用的特征
        print("最终选择的特征:")
        print(list(train_features_df.columns))
        print(f"最终特征数量: {len(train_features_df.columns)}")

        # 确保特征列一致
        val_features_df = val_features_df[train_features_df.columns]
        test_features_df = test_features_df[train_features_df.columns]

        # 标准化特征
        scaler = StandardScaler()
        train_features_scaled = scaler.fit_transform(train_features_df)
        val_features_scaled = scaler.transform(val_features_df)
        test_features_scaled = scaler.transform(test_features_df)

        # 转换标签
        label_encoder = LabelEncoder()
        train_labels_encoded = label_encoder.fit_transform(train_labels)
        val_labels_encoded = label_encoder.transform(val_labels)
        test_labels_encoded = label_encoder.transform(test_labels)

        # ✅ 训练 RandomForest
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(train_features_scaled, train_labels_encoded)

        # 评估 RandomForest
        test_preds = rf_model.predict(test_features_scaled)

        # 保存模型和必要数据
        model_save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'RandomForest',
                                       'rf_model.pkl')
        joblib.dump(rf_model, model_save_path)
        scaler_save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'RandomForest',
                                        'scaler.pkl')
        joblib.dump(scaler, scaler_save_path)
        encoder_save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'RandomForest',
                                         'label_encoder.pkl')
        joblib.dump(label_encoder, encoder_save_path)
        feature_save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'RandomForest',
                                         'feature_names.pkl')
        joblib.dump(list(train_features_df.columns), feature_save_path)

        print(f"\nRandomForest 测试集准确率: {accuracy_score(test_labels_encoded, test_preds):.4f}")
        print("RandomForest 分类报告:")
        return classification_report(test_labels_encoded, test_preds, digits=4)

     
    def predict(self, data):
        # 加载模型和必要数据
        loaded_rf_model = joblib.load(os.path.join(os.path.dirname(os.path.abspath(__file__)),'models', 'RandomForest', 'rf_model.pkl'))
        loaded_scaler = joblib.load(os.path.join(os.path.dirname(os.path.abspath(__file__)),'models', 'RandomForest','scaler.pkl'))
        loaded_label_encoder = joblib.load(os.path.join(os.path.dirname(os.path.abspath(__file__)),'models', 'RandomForest', 'label_encoder.pkl'))
        loaded_feature_names = joblib.load(os.path.join(os.path.dirname(os.path.abspath(__file__)),'models', 'RandomForest', 'feature_names.pkl'))

        new_data = data[loaded_feature_names]
        new_data_scaled = loaded_scaler.transform(new_data)
        new_preds = loaded_rf_model.predict(new_data_scaled)
        new_pred_labels = loaded_label_encoder.inverse_transform(new_preds)
        return new_pred_labels


class Stacking(DetectionModel):
     
    def train_and_save_model(self, features):
        train_extractor = FeatureExtractor(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data", "Humhub_train.csv"),
            features=features)
        test_extractor = FeatureExtractor(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data", "Humhub_test.csv"),
            features=features)

        # 提取特征
        train_features_df, train_labels = train_extractor.get_features()
        test_features_df, test_labels = test_extractor.get_features()

        # 拆分训练集 & 验证集
        train_features_df, val_features_df, train_labels, val_labels = train_test_split(
            train_features_df, train_labels, test_size=0.2, random_state=42
        )

        # ✅ 打印最终使用的特征
        print("最终选择的特征:")
        print(list(train_features_df.columns))
        print(f"最终特征数量: {len(train_features_df.columns)}")

        # 确保特征列一致
        val_features_df = val_features_df[train_features_df.columns]
        test_features_df = test_features_df[train_features_df.columns]

        # 处理缺失值
        imputer = SimpleImputer(strategy="mean")
        train_features_df = pd.DataFrame(imputer.fit_transform(train_features_df), columns=train_features_df.columns)
        val_features_df = pd.DataFrame(imputer.transform(val_features_df), columns=val_features_df.columns)
        test_features_df = pd.DataFrame(imputer.transform(test_features_df), columns=test_features_df.columns)

        # 标准化特征
        scaler = StandardScaler()
        train_features_scaled = scaler.fit_transform(train_features_df)
        val_features_scaled = scaler.transform(val_features_df)
        test_features_scaled = scaler.transform(test_features_df)

        # 转换标签
        label_encoder = LabelEncoder()
        train_labels_encoded = label_encoder.fit_transform(train_labels)
        val_labels_encoded = label_encoder.transform(val_labels)
        test_labels_encoded = label_encoder.transform(test_labels)

        # ✅ Stacking 集成模型
        base_models = [
            ('xgb', XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42)),  # XGBoost
            ('rf', RandomForestClassifier(n_estimators=100, random_state=42)),  # 随机森林
            ('dnn', MLPClassifier(hidden_layer_sizes=(128, 64), activation='relu', solver='adam', max_iter=500,
                                  random_state=42)),  # DNN
            ('dt', DecisionTreeClassifier(max_depth=10, random_state=42))  # 决策树
        ]

        # 第二层元学习器 (LightGBM)
        meta_model = lgb.LGBMClassifier(n_estimators=100, learning_rate=0.1, random_state=42)

        # ✅ 逐个训练 Base Models，并显示进度条
        print("\n训练 Base Models...")
        for name, model in tqdm(base_models, desc="Training Base Models"):
            model.fit(train_features_scaled, train_labels_encoded)

        # ✅ 构建 Stacking 分类器
        stacking_clf = StackingClassifier(
            estimators=base_models,  # 第一层模型
            final_estimator=meta_model,  # 第二层元模型
            passthrough=True,  # 让元模型同时使用原始特征 + 第一层模型的预测结果
            n_jobs=-1
        )

        # ✅ 训练 Stacking 模型 & 进度条
        print("\n训练 Stacking 集成模型...")
        with tqdm(total=1, desc="Training Stacking Model") as pbar:
            stacking_clf.fit(train_features_scaled, train_labels_encoded)
            pbar.update(1)  # 更新进度

        # ✅ 评估 Stacking 模型
        print("\n评估 Stacking 集成模型...")
        test_preds = stacking_clf.predict(test_features_scaled)
        print(f"\nStacking 集成学习 测试集准确率: {accuracy_score(test_labels_encoded, test_preds):.4f}")

        # 保存模型和必要数据
        joblib.dump(stacking_clf, os.path.join(os.path.dirname(os.path.abspath(__file__)),'models', 'Stacking','stacking_clf.pkl'))
        joblib.dump(scaler, os.path.join(os.path.dirname(os.path.abspath(__file__)),'models', 'Stacking','scaler.pkl'))
        joblib.dump(label_encoder, os.path.join(os.path.dirname(os.path.abspath(__file__)),'models', 'Stacking', 'label_encoder.pkl'))
        joblib.dump(imputer, os.path.join(os.path.dirname(os.path.abspath(__file__)),'models', 'Stacking', 'imputer.pkl'))
        joblib.dump(list(train_features_df.columns), os.path.join(os.path.dirname(os.path.abspath(__file__)),'models', 'Stacking', 'feature_names.pkl'))

        return classification_report(test_labels_encoded, test_preds, digits=4)

     
    def predict(self, data):
        # 加载模型和必要数据
        loaded_stacking_clf = joblib.load(os.path.join(os.path.dirname(os.path.abspath(__file__)),'models', 'Stacking','stacking_clf.pkl'))
        loaded_scaler = joblib.load(os.path.join(os.path.dirname(os.path.abspath(__file__)),'models', 'Stacking','scaler.pkl'))
        loaded_label_encoder = joblib.load(os.path.join(os.path.dirname(os.path.abspath(__file__)),'models', 'Stacking', 'label_encoder.pkl'))
        loaded_imputer = joblib.load(os.path.join(os.path.dirname(os.path.abspath(__file__)),'models', 'Stacking', 'imputer.pkl'))
        loaded_feature_names = joblib.load(os.path.join(os.path.dirname(os.path.abspath(__file__)),'models', 'Stacking', 'feature_names.pkl'))

        # 确保新数据包含所有特征列
        new_data = data[loaded_feature_names]
        # 处理缺失值
        new_data = pd.DataFrame(loaded_imputer.transform(new_data), columns=loaded_feature_names)
        # 标准化特征
        new_data_scaled = loaded_scaler.transform(new_data)
        # 进行预测
        new_preds = loaded_stacking_clf.predict(new_data_scaled)
        # 将编码后的预测结果转换回原始标签
        new_pred_labels = loaded_label_encoder.inverse_transform(new_preds)
        return new_pred_labels


class VAECNN(DetectionModel):
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

     
    def train_and_save_model(self, features):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        train_extractor = FeatureExtractor(
            os.path.join(base_dir, "sample_data", "Humhub_train.csv"),
            features=features)
        test_extractor = FeatureExtractor(
            os.path.join(base_dir, "sample_data", "Humhub_test.csv"),
            features=features)

        # ✅ 提取特征
        train_features_df, train_labels = train_extractor.get_features()
        test_features_df, test_labels = test_extractor.get_features()

        # ✅ 数据预处理
        scaler = MinMaxScaler(feature_range=(-1, 1))  # 归一化到 [-1, 1]
        train_features_scaled = scaler.fit_transform(train_features_df)
        test_features_scaled = scaler.transform(test_features_df)

        # ✅ 处理 NaN/Inf
        train_features_scaled = np.nan_to_num(train_features_scaled, nan=0.0, posinf=1.0, neginf=-1.0)
        test_features_scaled = np.nan_to_num(test_features_scaled, nan=0.0, posinf=1.0, neginf=-1.0)

        # ✅ 只使用 "正常" API 请求训练模型
        train_normal_idx = np.where(np.array(train_labels) == 0)[0]
        train_normal_features = torch.tensor(train_features_scaled[train_normal_idx], dtype=torch.float32)

        # ✅ 划分训练集（80%）和验证集（20%）
        train_feats, val_feats = train_test_split(train_normal_features, test_size=0.2, random_state=42)

        # ✅ 转换为 PyTorch Dataset
        batch_size = 64
        train_loader = torch.utils.data.DataLoader(train_feats, batch_size=batch_size, shuffle=True)
        val_loader = torch.utils.data.DataLoader(val_feats, batch_size=batch_size, shuffle=False)

        # ✅ 初始化 VAE-CNN
        input_dim = train_normal_features.shape[1]
        latent_dim = 64  # 潜在变量维度
        vae_cnn = VAE_CNN(input_dim, latent_dim).to(self.device)

        # ✅ 变分损失（ELBO）
        def vae_loss(reconstructed, x, mu, logvar):
            recon_loss = nn.MSELoss()(reconstructed, x)  # 重构损失
            kl_div = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())  # KL 散度
            return recon_loss + kl_div * 0.0001  # KL 散度加权（避免影响训练）

        # ✅ 优化器
        optimizer = optim.Adam(vae_cnn.parameters(), lr=0.001)

        # ✅ 训练 VAE-CNN（带验证集）
        best_vae_cnn = None
        best_val_loss = float("inf")
        patience = 5
        patience_counter = 0

        num_epochs = 100
        for epoch in range(num_epochs):
            vae_cnn.train()

            for batch in train_loader:
                batch = batch.to(self.device)

                # **前向传播**
                reconstructed, mu, logvar = vae_cnn(batch)

                # **计算损失**
                loss = vae_loss(reconstructed, batch, mu, logvar)

                # **反向传播**
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            # ✅ 计算验证损失
            vae_cnn.eval()
            val_loss = 0.0
            with torch.no_grad():
                for val_batch in val_loader:
                    val_batch = val_batch.to(self.device)
                    val_reconstructed, val_mu, val_logvar = vae_cnn(val_batch)
                    val_loss += vae_loss(val_reconstructed, val_batch, val_mu, val_logvar).item()

            val_loss /= len(val_loader)

            print(f"Epoch [{epoch + 1}/{num_epochs}] - Train Loss: {loss.item():.4f} - Val Loss: {val_loss:.4f}")

            # ✅ 更新最佳模型
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                best_vae_cnn = vae_cnn
                print("✅ 发现更好的模型，已更新变量！")
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print("⏹️ 早停触发，停止训练！")
                    break

        # ✅ 直接用 `best_vae_cnn` 计算异常分数
        best_vae_cnn.eval()
        test_features_tensor = torch.tensor(test_features_scaled, dtype=torch.float32).to(self.device)

        with torch.no_grad():
            reconstructed, _, _ = best_vae_cnn(test_features_tensor)
            anomaly_scores = torch.mean((test_features_tensor - reconstructed) ** 2, dim=1).cpu().numpy()

        # ✅ 设定异常检测阈值（用训练数据的 95% 分位数）
        threshold = np.percentile(anomaly_scores, 80)
        preds = (anomaly_scores > threshold).astype(int)  # 1 = 异常, 0 = 正常

        # ✅ 评估模型
        print(f"\nVAE-CNN 测试集准确率: {accuracy_score(test_labels, preds):.4f}")
        print("VAE-CNN 分类报告:")

        # 保存模型和必要数据
        model_dir = os.path.join(base_dir, "models", "VAE-CNN")
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        torch.save({
            'input_dim': input_dim,
            'latent_dim': latent_dim,
            'model_state_dict': best_vae_cnn.state_dict(),
            'scaler': scaler,
            'threshold': threshold
        }, os.path.join(model_dir, "best_vae_cnn_model.pth"))

        return classification_report(test_labels, preds, digits=4)

     
    def predict(self, data):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # 加载模型和必要数据
        checkpoint = torch.load(os.path.join(base_dir, "models", "VAE-CNN", "best_vae_cnn_model.pth"), weights_only=False)
        input_dim = checkpoint['input_dim']
        latent_dim = checkpoint['latent_dim']
        loaded_vae_cnn = VAE_CNN(input_dim, latent_dim).to(self.device)
        loaded_vae_cnn.load_state_dict(checkpoint['model_state_dict'])
        loaded_vae_cnn.eval()
        loaded_scaler = checkpoint['scaler']
        loaded_threshold = checkpoint['threshold']

        # 数据预处理
        new_data_scaled = loaded_scaler.transform(data)
        new_data_scaled = np.nan_to_num(new_data_scaled, nan=0.0, posinf=1.0, neginf=-1.0)
        new_data_tensor = torch.tensor(new_data_scaled, dtype=torch.float32).to(self.device)

        # 模型推理
        with torch.no_grad():
            reconstructed, _, _ = loaded_vae_cnn(new_data_tensor)
            anomaly_scores = torch.mean((new_data_tensor - reconstructed) ** 2, dim=1).cpu().numpy()

        # 生成预测结果
        preds = (anomaly_scores > loaded_threshold).astype(int)
        return preds


class XGBoost(DetectionModel):
     
    def train_and_save_model(self, features):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        train_extractor = FeatureExtractor(
            os.path.join(base_dir, "sample_data", "Humhub_train.csv"),
            features=features)
        test_extractor = FeatureExtractor(
            os.path.join(base_dir, "sample_data", "Humhub_test.csv"),
            features=features)

        # 提取特征
        train_features_df, train_labels = train_extractor.get_features()
        test_features_df, test_labels = test_extractor.get_features()

        # 拆分训练集 & 验证集
        train_features_df, val_features_df, train_labels, val_labels = train_test_split(
            train_features_df, train_labels, test_size=0.2, random_state=42
        )

        # ✅ 打印最终使用的特征
        print("最终选择的特征:")
        print(list(train_features_df.columns))
        print(f"最终特征数量: {len(train_features_df.columns)}")

        # 确保特征列一致
        val_features_df = val_features_df[train_features_df.columns]
        test_features_df = test_features_df[train_features_df.columns]

        # 标准化特征
        scaler = StandardScaler()
        train_features_scaled = scaler.fit_transform(train_features_df)
        val_features_scaled = scaler.transform(val_features_df)
        test_features_scaled = scaler.transform(test_features_df)

        # 转换标签
        label_encoder = LabelEncoder()
        train_labels_encoded = label_encoder.fit_transform(train_labels)
        val_labels_encoded = label_encoder.transform(val_labels)
        test_labels_encoded = label_encoder.transform(test_labels)

        # ✅ 训练 XGBoost
        xgb_model = XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42)
        xgb_model.fit(train_features_scaled, train_labels_encoded)

        # ✅ 评估 XGBoost
        test_preds = xgb_model.predict(test_features_scaled)
        print(f"\nXGBoost 测试集准确率: {accuracy_score(test_labels_encoded, test_preds):.4f}")

        # 保存模型和必要数据
        model_dir = os.path.join(base_dir, "models", "XGBoost")
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        joblib.dump(xgb_model, os.path.join(model_dir, "xgb_model.pkl"))
        joblib.dump(scaler, os.path.join(model_dir, "scaler.pkl"))
        joblib.dump(label_encoder, os.path.join(model_dir, "label_encoder.pkl"))
        joblib.dump(list(train_features_df.columns), os.path.join(model_dir, "feature_names.pkl"))

        return classification_report(test_labels_encoded, test_preds)

     
    def predict(self, data):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # 加载模型和必要数据
        loaded_xgb_model = joblib.load(os.path.join(base_dir, "models", "XGBoost", "xgb_model.pkl"))
        loaded_scaler = joblib.load(os.path.join(base_dir, "models", "XGBoost", "scaler.pkl"))
        loaded_label_encoder = joblib.load(os.path.join(base_dir, "models", "XGBoost", "label_encoder.pkl"))
        loaded_feature_names = joblib.load(os.path.join(base_dir, "models", "XGBoost", "feature_names.pkl"))

        # 确保新数据包含所有特征列
        new_data = data[loaded_feature_names]
        # 标准化特征
        new_data_scaled = loaded_scaler.transform(new_data)
        # 进行预测
        new_preds = loaded_xgb_model.predict(new_data_scaled)
        # 将编码后的预测结果转换回原始标签
        new_pred_labels = loaded_label_encoder.inverse_transform(new_preds)
        return new_pred_labels


DETECTION_MODELS = {
    'AE_CNN': AECNN(),
    'AE_MAP': AEMLP(),
    'Ganomaly': Ganomaly(),
    'RandomForest': RandomForest(),
    'Stacking': Stacking(),
    'VAE_CNN': VAECNN(),
    'XGBoost': XGBoost()
}

# data,_ = FeatureExtractor(".\Data\Humhub_new\Humhub_test.csv").get_features()
# for name, model in DETECTION_MODELS.items():
#     print(model.train_and_save_model(features=feature.APP_FEATURES))
#     print(model.predict(data))
