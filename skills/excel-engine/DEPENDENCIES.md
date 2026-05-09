# 依赖说明

## Python 包依赖

| 包名 | 版本 | 用途 | 安装命令 |
|------|------|------|----------|
| pandas | >= 1.5.0 | 数据处理、CSV读写、高性能数据操作 | `pip install pandas` |
| openpyxl | >= 3.0.0 | Excel文件读写、格式处理、公式操作 | `pip install openpyxl` |
| numpy | >= 1.21.0 | 数值计算、类型转换 | `pip install numpy` |
| pyyaml | >= 6.0 | 配置文件解析 | `pip install pyyaml` |

## 快速安装

### 全部安装
```bash
pip install pandas openpyxl numpy pyyaml
```

### 验证安装
```python
import pandas
import openpyxl
import numpy
import yaml
print("所有依赖已正确安装!")
```

## 版本兼容性

| 组件 | 推荐版本 | 最低版本 | 备注 |
|------|----------|----------|------|
| Python | 3.10+ | 3.8+ | 建议使用 3.10 或更高版本 |
| pandas | 2.0+ | 1.5.0 | 大文件处理性能更好 |
| openpyxl | 3.1+ | 3.0.0 | 透视表支持更好 |

## 可选依赖

| 包名 | 用途 | 说明 |
|------|------|------|
| xlrd | 读取旧版 .xls 文件 | pandas 2.0+ 默认不包含 |
| xlsxwriter | 高性能写入 | 比 openpyxl 快，但不支持读取 |
| pyexcelerate | 超高速写入 | 适合 100万+ 行数据 |

## 性能优化建议

### 大文件处理

对于超过 10万行 的数据文件：

1. **使用 pandas 读取优化**
   ```python
   # 指定 dtype，避免类型推断开销
   dtypes = {'column1': str, 'column2': 'float32'}
   df = pd.read_csv('large.csv', dtype=dtypes, low_memory=False)
   ```

2. **分块处理**
   ```python
   chunksize = 10000
   for chunk in pd.read_csv('huge.csv', chunksize=chunksize):
       process_chunk(chunk)
   ```

3. **openpyxl 只读模式**
   ```python
   wb = openpyxl.load_workbook(
       'large.xlsx',
       read_only=True,  # 只读模式，内存友好
       data_only=True   # 只读取值，不解析公式
   )
   ```

## 常见问题

### Q: ImportError: No module named 'openpyxl'
A: 运行 `pip install openpyxl`

### Q: pandas 读取 Excel 报错
A: 确保安装了 openpyxl 引擎，pandas 需要它来读写 .xlsx 文件

### Q: 内存不足 (OOM)
A: 
1. 使用分块读取
2. 指定 dtype 减少内存占用
3. 删除不需要的列后再处理
4. 考虑使用 Dask 或 Vaex 处理超大数据

### Q: 中文乱码
A: 
```python
# UTF-8 with BOM (Windows 导出的 CSV 常用)
df = pd.read_csv('data.csv', encoding='utf-8-sig')

# GBK / GB2312 (中文 Windows 默认)
df = pd.read_csv('data.csv', encoding='gbk')
```

## 环境检查脚本

```python
#!/usr/bin/env python3
"""检查 Excel Engine 依赖环境"""

import sys

def check_dependencies():
    print("=" * 50)
    print("Excel Engine 依赖检查")
    print("=" * 50)
    
    packages = [
        ('pandas', '1.5.0'),
        ('openpyxl', '3.0.0'),
        ('numpy', '1.21.0'),
        ('yaml', '6.0'),
    ]
    
    all_ok = True
    
    for pkg_name, min_version in packages:
        try:
            if pkg_name == 'yaml':
                import yaml
                version = getattr(yaml, '__version__', 'unknown')
            else:
                module = __import__(pkg_name)
                version = getattr(module, '__version__', 'unknown')
            
            print(f"✓ {pkg_name:12} v{version}")
        except ImportError:
            print(f"✗ {pkg_name:12} 未安装")
            all_ok = False
    
    print("=" * 50)
    print(f"Python 版本: {sys.version.split()[0]}")
    print(f"整体状态: {'通过' if all_ok else '需要安装依赖'}")
    print("=" * 50)
    
    return all_ok

if __name__ == '__main__':
    sys.exit(0 if check_dependencies() else 1)
```
