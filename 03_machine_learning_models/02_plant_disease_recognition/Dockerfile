# 使用AWS Lambda Python 3.11基础镜像
FROM public.ecr.aws/lambda/python:3.11

# 设置工作目录
WORKDIR ${LAMBDA_TASK_ROOT}

# 安装系统依赖
RUN yum update -y && \
    yum install -y \
    gcc \
    gcc-c++ \
    make \
    cmake \
    git \
    && yum clean all

# 升级pip并设置环境变量
RUN pip install --upgrade pip setuptools wheel

# 复制requirements.txt并安装Python依赖
COPY requirements.txt .

# 安装兼容的依赖包（按顺序安装以避免版本冲突）
RUN pip install --no-cache-dir "numpy<2.0.0" "numpy>=1.21.0"

# 安装torch和torchvision（使用CPU版本，与numpy兼容）
RUN pip install --no-cache-dir torch==2.0.0 torchvision==0.15.0+cpu --index-url https://download.pytorch.org/whl/cpu

# 安装其他依赖
RUN pip install --no-cache-dir Pillow==9.5.0 timm==0.9.12 boto3==1.26.137

# 复制模型文件和配置文件
COPY model.pth /opt/ml/model.pth
COPY class_map.json /opt/ml/class_map.json

# 复制Lambda函数代码
COPY lambda_function.py .

# 设置环境变量
ENV PYTHONPATH="${LAMBDA_TASK_ROOT}"
ENV PYTHONUNBUFFERED=1

# 设置Lambda处理程序
CMD ["lambda_function.lambda_handler"]
