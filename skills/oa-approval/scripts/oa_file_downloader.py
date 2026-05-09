#!/usr/bin/env python3
"""
OA 合同文件自动下载脚本
======================
通过 Playwright 浏览器自动化从泛微 OA 系统下载合同附件

功能特性:
- 多种查询方式：合同编号、审批流程ID、标题关键词、批量下载
- 智能文件处理：自动重命名、格式识别、完整性校验
- 元信息提取：合同基本信息自动提取
- 异常处理：登录重试、下载重试、权限提示

作者: Ella 🦊
版本: v1.0
创建时间: 2026-04-24
"""

import argparse
import json
import logging
import random
import time
import os
import re
import hashlib
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse
import mimetypes

try:
    from playwright.sync_api import sync_playwright, Page, Browser
except ImportError:
    print("❌ 请先安装 playwright: pip install playwright && playwright install chromium")
    exit(1)

# 确保日志目录存在
log_dir = Path.home() / '.openclaw' / 'output' / 'oa-logs'
log_dir.mkdir(parents=True, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'downloader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class OAFileDownloader:
    """OA 合同文件下载器类"""

    def __init__(self, config_path: str = None):
        """
        初始化 OA 下载器客户端
        
        Args:
            config_path: 配置文件路径，默认使用 config/oa-config.json
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'oa-config.json'
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.playwright = None
        self.browser: Browser = None
        self.page: Page = None
        self.download_context = None
        
        # 下载配置（默认值）
        self.download_config = self.config.get('download', {
            'save_dir': '~/Downloads/OA_Contracts/',
            'auto_rename': True,
            'naming_pattern': '{contract_code}_{filename}_{timestamp}',
            'retry_count': 3,
            'retry_delay': 5,
            'max_file_size': 100
        })
        
        # 确保输出目录存在
        for dir_key in ['screenshot_dir', 'log_dir']:
            dir_path = Path(self.config['output'][dir_key]).expanduser()
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # 确保下载目录存在
        save_dir = Path(self.download_config['save_dir']).expanduser()
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # 下载报告
        self.download_report = {
            'start_time': datetime.now().isoformat(),
            'total_files': 0,
            'success_files': 0,
            'failed_files': 0,
            'files': [],
            'errors': []
        }
        
        # 合同元信息集合
        self.contracts_metadata = []

    def _human_delay(self, action_type: str = 'operation'):
        """
        模拟人类操作延迟
        
        Args:
            action_type: 'operation' (操作) 或 'typing' (打字)
        """
        if action_type == 'typing':
            delay = random.uniform(
                self.config['human_simulation']['typing_delay_min'],
                self.config['human_simulation']['typing_delay_max']
            )
        else:
            delay = random.uniform(
                self.config['human_simulation']['operation_delay_min'],
                self.config['human_simulation']['operation_delay_max']
            )
        time.sleep(delay)

    def _get_password_from_keychain(self) -> str:
        """从 macOS Keychain 获取密码"""
        import subprocess
        result = subprocess.run([
            'security', 'find-generic-password',
            '-s', self.config['auth']['keychain_service'],
            '-w'
        ], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError("无法从 Keychain 获取密码，请先配置")
        return result.stdout.strip()

    def _calculate_md5(self, file_path: Path) -> str:
        """计算文件 MD5 哈希值"""
        md5_hash = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名中的非法字符"""
        # 替换非法字符
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # 去除首尾空格和点
        sanitized = sanitized.strip('. ')
        # 限制长度
        if len(sanitized) > 200:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:190] + '...' + ext
        return sanitized

    def _generate_filename(self, contract_code: str, original_filename: str, 
                          naming_pattern: str = None) -> str:
        """
        根据命名模式生成文件名
        
        Args:
            contract_code: 合同编号
            original_filename: 原始文件名
            naming_pattern: 命名模式模板
            
        Returns:
            生成的文件名
        """
        if naming_pattern is None:
            naming_pattern = self.download_config['naming_pattern']
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(original_filename)
        
        replacements = {
            'contract_code': contract_code or 'UNKNOWN',
            'filename': name,
            'timestamp': timestamp,
            'date': datetime.now().strftime('%Y%m%d'),
            'time': datetime.now().strftime('%H%M%S')
        }
        
        try:
            new_name = naming_pattern.format(**replacements) + ext
        except Exception:
            # 如果模板格式化失败，使用默认模式
            new_name = f"{contract_code or 'UNKNOWN'}_{name}_{timestamp}{ext}"
        
        return self._sanitize_filename(new_name)

    def launch_browser(self, headless: bool = True):
        """启动浏览器并配置下载行为"""
        logger.info("🚀 启动浏览器...")
        self.playwright = sync_playwright().start()
        
        # 配置浏览器下载行为
        download_path = str(Path(self.download_config['save_dir']).expanduser())
        self.browser = self.playwright.chromium.launch(
            headless=headless,
            downloads_path=download_path
        )
        
        # 创建浏览器上下文并配置下载
        self.download_context = self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            accept_downloads=True
        )
        
        self.page = self.download_context.new_page()

    def login(self, interactive: bool = False, max_retries: int = 3) -> bool:
        """
        登录 OA 系统（带重试机制）
        
        Args:
            interactive: 是否交互式模式
            max_retries: 最大重试次数
            
        Returns:
            是否登录成功
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"🔐 登录 OA 系统 (尝试 {attempt + 1}/{max_retries}): {self.config['oa_url']}")
                self.page.goto(self.config['oa_url'])
                self._human_delay()
                
                # 填写用户名密码
                password = self._get_password_from_keychain()
                self.page.fill(self.config['selectors']['login_form']['username_input'], 
                               self.config['auth']['username'])
                self._human_delay('typing')
                
                self.page.fill(self.config['selectors']['login_form']['password_input'], password)
                self._human_delay('typing')
                
                # 检查是否有验证码
                captcha_selector = self.config['selectors']['login_form']['captcha_image']
                try:
                    self.page.wait_for_selector(captcha_selector, timeout=3000, state='visible')
                    if interactive:
                        logger.info("⚠️  检测到验证码，请在浏览器中手动完成验证后按回车继续...")
                        self.page.wait_for_timeout(1000)
                        input()
                    else:
                        raise RuntimeError("检测到验证码，请使用 --interactive 模式运行")
                except Exception:
                    pass
                
                # 点击登录
                self.page.click(self.config['selectors']['login_form']['submit_button'])
                self._human_delay()
                
                # 验证登录成功（检查是否跳转到主页）
                if 'login' not in self.page.url.lower():
                    logger.info("✅ 登录完成")
                    return True
                else:
                    logger.warning(f"⚠️  登录可能未成功，当前页面: {self.page.url}")
                    
            except Exception as e:
                logger.error(f"❌ 登录尝试 {attempt + 1} 失败: {e}")
                if attempt < max_retries - 1:
                    retry_delay = self.download_config['retry_delay'] * (attempt + 1)
                    logger.info(f"⏳ 等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
        
        raise RuntimeError(f"登录失败，已重试 {max_retries} 次")

    def search_contract_by_code(self, contract_code: str) -> dict:
        """
        按合同编号搜索合同
        
        Args:
            contract_code: 合同编号
            
        Returns:
            合同信息字典
        """
        logger.info(f"🔍 按合同编号搜索: {contract_code}")
        
        # 导航到合同台账页面
        contract_list_url = self.config.get('contract_list_url', 
                                           self.config['oa_url'] + '/workflow/contract/list')
        self.page.goto(contract_list_url)
        self._human_delay()
        
        # 查找搜索框并输入合同编号
        search_selectors = self.config.get('selectors', {}).get('search_form', {
            'search_input': '#searchInput',
            'search_button': '#searchBtn',
            'contract_code_field': '#contractCode'
        })
        
        try:
            # 在搜索框输入合同编号
            search_input = search_selectors.get('contract_code_field', search_selectors.get('search_input'))
            self.page.wait_for_selector(search_input, timeout=5000, state='visible')
            self.page.fill(search_input, contract_code)
            self._human_delay('typing')
            
            # 点击搜索按钮
            self.page.click(search_selectors['search_button'])
            self._human_delay()
            
            # 解析搜索结果
            return self._parse_search_results(contract_code)
            
        except Exception as e:
            logger.error(f"❌ 搜索合同失败: {e}")
            raise

    def _parse_search_results(self, search_key: str = '') -> dict:
        """解析搜索结果页面"""
        result_selectors = self.config.get('selectors', {}).get('search_results', {
            'container': '.result-list',
            'items': '.result-item',
            'item_title': '.item-title',
            'item_contract_code': '.contract-code',
            'item_link': '.item-link',
            'item_status': '.item-status'
        })
        
        try:
            self.page.wait_for_selector(result_selectors['container'], timeout=5000, state='visible')
            items = self.page.query_selector_all(result_selectors['items'])
            
            if not items:
                logger.warning(f"⚠️  未找到搜索结果: {search_key}")
                return None
            
            # 返回第一个匹配结果
            first_item = items[0]
            contract_info = {
                'contract_code': '',
                'title': '',
                'url': '',
                'status': '',
                'request_id': ''
            }
            
            code_elem = first_item.query_selector(result_selectors['item_contract_code'])
            if code_elem:
                contract_info['contract_code'] = code_elem.inner_text().strip()
            
            title_elem = first_item.query_selector(result_selectors['item_title'])
            if title_elem:
                contract_info['title'] = title_elem.inner_text().strip()
            
            link_elem = first_item.query_selector(result_selectors['item_link'])
            if link_elem:
                contract_info['url'] = link_elem.get_attribute('href') or ''
                # 从URL中提取request_id
                url_match = re.search(r'(?:id|requestId)=(\d+)', contract_info['url'])
                if url_match:
                    contract_info['request_id'] = url_match.group(1)
            
            status_elem = first_item.query_selector(result_selectors['item_status'])
            if status_elem:
                contract_info['status'] = status_elem.inner_text().strip()
            
            logger.info(f"✅ 找到合同: {contract_info['title']}")
            return contract_info
            
        except Exception as e:
            logger.error(f"❌ 解析搜索结果失败: {e}")
            return None

    def get_contract_by_request_id(self, request_id: str) -> dict:
        """
        按审批流程ID获取合同
        
        Args:
            request_id: 审批流程ID
            
        Returns:
            合同信息字典
        """
        logger.info(f"🔍 按审批流程ID获取合同: {request_id}")
        
        detail_url_pattern = self.config.get('detail_url_pattern', 
                                            self.config['oa_url'] + '/workflow/request/detail?id={id}')
        detail_url = detail_url_pattern.format(id=request_id)
        self.page.goto(detail_url)
        self._human_delay()
        
        return {
            'request_id': request_id,
            'url': detail_url,
            'title': '',
            'contract_code': ''
        }

    def search_contract_by_keyword(self, keyword: str) -> list:
        """
        按标题关键词搜索合同
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            合同信息列表
        """
        logger.info(f"🔍 按关键词搜索: {keyword}")
        
        contract_list_url = self.config.get('contract_list_url', 
                                           self.config['oa_url'] + '/workflow/contract/list')
        self.page.goto(contract_list_url)
        self._human_delay()
        
        search_selectors = self.config.get('selectors', {}).get('search_form', {
            'search_input': '#searchInput',
            'search_button': '#searchBtn'
        })
        
        try:
            self.page.wait_for_selector(search_selectors['search_input'], timeout=5000, state='visible')
            self.page.fill(search_selectors['search_input'], keyword)
            self._human_delay('typing')
            
            self.page.click(search_selectors['search_button'])
            self._human_delay()
            
            # 解析多个搜索结果
            result_selectors = self.config.get('selectors', {}).get('search_results', {
                'container': '.result-list',
                'items': '.result-item',
                'item_title': '.item-title',
                'item_contract_code': '.contract-code',
                'item_link': '.item-link',
                'item_status': '.item-status'
            })
            
            self.page.wait_for_selector(result_selectors['container'], timeout=5000, state='visible')
            items = self.page.query_selector_all(result_selectors['items'])
            
            contracts = []
            for item in items:
                contract_info = {
                    'contract_code': '',
                    'title': '',
                    'url': '',
                    'status': ''
                }
                
                code_elem = item.query_selector(result_selectors['item_contract_code'])
                if code_elem:
                    contract_info['contract_code'] = code_elem.inner_text().strip()
                
                title_elem = item.query_selector(result_selectors['item_title'])
                if title_elem:
                    contract_info['title'] = title_elem.inner_text().strip()
                
                link_elem = item.query_selector(result_selectors['item_link'])
                if link_elem:
                    contract_info['url'] = link_elem.get_attribute('href') or ''
                    url_match = re.search(r'(?:id|requestId)=(\d+)', contract_info['url'])
                    if url_match:
                        contract_info['request_id'] = url_match.group(1)
                
                status_elem = item.query_selector(result_selectors['item_status'])
                if status_elem:
                    contract_info['status'] = status_elem.inner_text().strip()
                
                contracts.append(contract_info)
            
            logger.info(f"✅ 找到 {len(contracts)} 个匹配合同")
            return contracts
            
        except Exception as e:
            logger.error(f"❌ 关键词搜索失败: {e}")
            return []

    def extract_contract_metadata(self, contract_info: dict) -> dict:
        """
        提取合同元信息
        
        Args:
            contract_info: 合同基本信息
            
        Returns:
            完整的合同元信息
        """
        logger.info(f"📄 提取合同元信息...")
        
        # 导航到详情页
        if contract_info.get('url'):
            self.page.goto(contract_info['url'])
        self._human_delay()
        
        metadata = {
            **contract_info,
            'extracted_at': datetime.now().isoformat(),
            'contract_title': '',
            'contract_amount': '',
            'party_a': '',
            'party_b': '',
            'contract_type': '',
            'effective_date': '',
            'expiry_date': '',
            'initiator': '',
            'department': '',
            'submit_time': '',
            'approval_status': ''
        }
        
        # 提取基本信息字段
        basic_fields = self.config.get('detail_fields', {
            'contract_title': '.contract-title',
            'contract_amount': '.contract-amount',
            'party_a': '.party-a',
            'party_b': '.party-b',
            'contract_type': '.contract-type',
            'effective_date': '.effective-date',
            'expiry_date': '.expiry-date',
            'initiator': '.initiator-name',
            'department': '.initiator-dept',
            'submit_time': '.submit-datetime'
        })
        
        for field_name, selector in basic_fields.items():
            try:
                elem = self.page.query_selector(selector)
                if elem:
                    metadata[field_name] = elem.inner_text().strip()
            except Exception:
                metadata[field_name] = ''
        
        # 提取审批状态
        try:
            status_selector = self.config.get('selectors', {}).get('approval_page', {}).get('current_node', '.current-node')
            status_elem = self.page.query_selector(status_selector)
            if status_elem:
                metadata['approval_status'] = status_elem.inner_text().strip()
        except Exception:
            pass
        
        logger.info(f"📄 元信息提取完成: {metadata.get('contract_title', 'N/A')}")
        return metadata

    def find_and_download_attachments(self, contract_info: dict, output_dir: Path = None, 
                                     metadata_only: bool = False) -> list:
        """
        查找并下载合同附件
        
        Args:
            contract_info: 合同信息
            output_dir: 输出目录
            metadata_only: 仅提取元信息不下载
            
        Returns:
            下载的文件信息列表
        """
        logger.info(f"🔍 查找合同附件...")
        
        if output_dir is None:
            output_dir = Path(self.download_config['save_dir']).expanduser()
        
        # 导航到详情页
        if contract_info.get('url'):
            self.page.goto(contract_info['url'])
        self._human_delay()
        
        # 查找附件区域
        attachment_selectors = self.config.get('selectors', {}).get('attachments', {
            'container': '.attachment-list, .file-list, #attachmentArea',
            'items': '.attachment-item, .file-item',
            'item_name': '.file-name, .attachment-name',
            'item_size': '.file-size, .attachment-size',
            'download_link': '.download-link, a[href*=download]'
        })
        
        downloaded_files = []
        
        try:
            # 等待附件容器加载
            container_found = False
            for container_sel in attachment_selectors['container'].split(','):
                try:
                    self.page.wait_for_selector(container_sel.strip(), timeout=3000, state='visible')
                    container_found = True
                    break
                except Exception:
                    continue
            
            if not container_found:
                logger.warning("⚠️  未找到附件区域")
                return downloaded_files
            
            self._human_delay()
            
            # 查找所有附件项
            attachments = []
            for item_sel in attachment_selectors['items'].split(','):
                items = self.page.query_selector_all(item_sel.strip())
                if items:
                    attachments = items
                    break
            
            logger.info(f"📎 找到 {len(attachments)} 个附件")
            
            for idx, attachment in enumerate(attachments):
                try:
                    # 提取文件名
                    file_name = ''
                    for name_sel in attachment_selectors['item_name'].split(','):
                        name_elem = attachment.query_selector(name_sel.strip())
                        if name_elem:
                            file_name = name_elem.inner_text().strip()
                            break
                    
                    # 提取文件大小
                    file_size = ''
                    for size_sel in attachment_selectors['item_size'].split(','):
                        size_elem = attachment.query_selector(size_sel.strip())
                        if size_elem:
                            file_size = size_elem.inner_text().strip()
                            break
                    
                    # 查找下载链接
                    download_elem = None
                    for link_sel in attachment_selectors['download_link'].split(','):
                        download_elem = attachment.query_selector(link_sel.strip())
                        if download_elem:
                            break
                    
                    if not download_elem:
                        # 尝试查找附件本身的链接
                        download_elem = attachment.query_selector('a')
                    
                    if not download_elem and not file_name:
                        logger.warning(f"⚠️  第 {idx + 1} 个附件无法识别，跳过")
                        continue
                    
                    file_info = {
                        'original_name': file_name or f'attachment_{idx + 1}',
                        'file_size': file_size,
                        'contract_code': contract_info.get('contract_code', ''),
                        'contract_title': contract_info.get('title', ''),
                        'downloaded': False,
                        'saved_path': '',
                        'md5': '',
                        'error': ''
                    }
                    
                    if metadata_only:
                        downloaded_files.append(file_info)
                        logger.info(f"📋 [元信息模式] {file_info['original_name']}")
                        continue
                    
                    # 执行下载
                    if download_elem:
                        download_result = self._download_file_with_retry(
                            download_elem, file_info, output_dir, contract_info
                        )
                        downloaded_files.append(download_result)
                    else:
                        file_info['error'] = '未找到下载链接'
                        downloaded_files.append(file_info)
                        logger.warning(f"⚠️  {file_info['original_name']}: 未找到下载链接")
                    
                except Exception as e:
                    logger.error(f"❌ 处理第 {idx + 1} 个附件失败: {e}")
                    continue
            
            return downloaded_files
            
        except Exception as e:
            logger.error(f"❌ 查找附件失败: {e}")
            raise

    def _download_file_with_retry(self, download_elem, file_info: dict, output_dir: Path,
                                 contract_info: dict) -> dict:
        """
        带重试机制的文件下载
        
        Args:
            download_elem: 下载链接元素
            file_info: 文件信息字典
            output_dir: 输出目录
            contract_info: 合同信息
            
        Returns:
            更新后的文件信息
        """
        max_retries = self.download_config['retry_count']
        retry_delay = self.download_config['retry_delay']
        
        for attempt in range(max_retries):
            try:
                logger.info(f"⬇️  下载文件: {file_info['original_name']} (尝试 {attempt + 1}/{max_retries})")
                
                # 启动下载
                with self.page.expect_download(timeout=30000) as download_info:
                    download_elem.click()
                
                download = download_info.value
                
                # 获取原始文件名
                original_name = download.suggested_filename or file_info['original_name']
                
                # 生成新文件名
                if self.download_config['auto_rename']:
                    new_filename = self._generate_filename(
                        contract_info.get('contract_code', ''),
                        original_name
                    )
                else:
                    new_filename = self._sanitize_filename(original_name)
                
                save_path = output_dir / new_filename
                
                # 保存文件
                download.save_as(str(save_path))
                
                # 验证文件
                if not save_path.exists():
                    raise RuntimeError("文件未保存成功")
                
                # 计算MD5
                file_md5 = self._calculate_md5(save_path)
                file_size = save_path.stat().st_size
                
                # 检查文件大小限制
                max_size_mb = self.download_config['max_file_size']
                file_size_mb = file_size / (1024 * 1024)
                if file_size_mb > max_size_mb:
                    logger.warning(f"⚠️  文件超过大小限制: {file_size_mb:.1f} MB > {max_size_mb} MB")
                
                file_info.update({
                    'downloaded': True,
                    'saved_path': str(save_path),
                    'file_size_bytes': file_size,
                    'md5': file_md5,
                    'final_name': new_filename,
                    'attempts': attempt + 1
                })
                
                self.download_report['success_files'] += 1
                logger.info(f"✅ 下载成功: {new_filename} ({file_size_mb:.2f} MB)")
                return file_info
                
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"⚠️  下载尝试 {attempt + 1} 失败: {error_msg}")
                
                if attempt < max_retries - 1:
                    logger.info(f"⏳ 等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                else:
                    file_info['error'] = error_msg
                    self.download_report['errors'].append({
                        'file': file_info['original_name'],
                        'error': error_msg,
                        'attempts': max_retries
                    })
        
        self.download_report['failed_files'] += 1
        return file_info

    def download_contract(self, identifier: str, id_type: str = 'contract_code',
                         output_dir: str = None, metadata_only: bool = False) -> dict:
        """
        下载单个合同的所有附件
        
        Args:
            identifier: 合同标识（合同编号或审批ID）
            id_type: 'contract_code' 或 'request_id'
            output_dir: 输出目录
            metadata_only: 仅提取元信息不下载
            
        Returns:
            下载结果字典
        """
        if output_dir:
            output_path = Path(output_dir).expanduser()
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            output_path = Path(self.download_config['save_dir']).expanduser()
        
        # 获取合同信息
        if id_type == 'contract_code':
            contract_info = self.search_contract_by_code(identifier)
            if not contract_info:
                raise RuntimeError(f"未找到合同编号为 {identifier} 的合同")
        elif id_type == 'request_id':
            contract_info = self.get_contract_by_request_id(identifier)
        else:
            raise ValueError(f"不支持的ID类型: {id_type}")
        
        # 提取元信息
        metadata = self.extract_contract_metadata(contract_info)
        self.contracts_metadata.append(metadata)
        
        # 下载附件
        downloaded_files = self.find_and_download_attachments(
            contract_info, output_path, metadata_only
        )
        
        self.download_report['total_files'] += len(downloaded_files)
        
        result = {
            'contract_info': contract_info,
            'metadata': metadata,
            'files': downloaded_files,
            'output_dir': str(output_path)
        }
        
        return result

    def batch_download(self, batch_file: str, output_dir: str = None,
                      metadata_only: bool = False) -> list:
        """
        批量下载合同
        
        Args:
            batch_file: 包含合同编号列表的文件
            output_dir: 输出目录
            metadata_only: 仅提取元信息
            
        Returns:
            所有下载结果列表
        """
        logger.info(f"📦 开始批量下载，读取文件: {batch_file}")
        
        with open(batch_file, 'r', encoding='utf-8') as f:
            contract_codes = [line.strip() for line in f if line.strip()]
        
        logger.info(f"📋 共 {len(contract_codes)} 个合同需要处理")
        
        results = []
        for idx, code in enumerate(contract_codes, 1):
            try:
                logger.info(f"\n--- 处理第 {idx}/{len(contract_codes)} 个合同: {code} ---")
                result = self.download_contract(code, 'contract_code', output_dir, metadata_only)
                results.append(result)
                self._human_delay()  # 合同之间的延迟
            except Exception as e:
                logger.error(f"❌ 下载合同 {code} 失败: {e}")
                results.append({
                    'contract_code': code,
                    'error': str(e),
                    'files': []
                })
                continue
        
        return results

    def save_report(self, output_dir: str = None):
        """
        保存下载报告和元信息到JSON文件
        
        Args:
            output_dir: 输出目录
        """
        if output_dir:
            output_path = Path(output_dir).expanduser()
        else:
            output_path = Path(self.download_config['save_dir']).expanduser()
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 更新报告时间
        self.download_report['end_time'] = datetime.now().isoformat()
        
        # 保存下载报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f'download_report_{timestamp}.json'
        report_path = output_path / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.download_report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 下载报告已保存: {report_path}")
        
        # 保存合同元信息
        if self.contracts_metadata:
            metadata_filename = f'contract_metadata_{timestamp}.json'
            metadata_path = output_path / metadata_filename
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.contracts_metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📄 合同元信息已保存: {metadata_path}")

    def take_screenshot(self, name: str):
        """截图保存"""
        path = Path(self.config['output']['screenshot_dir']).expanduser() / f"{name}_{int(time.time())}.png"
        self.page.screenshot(path=str(path))
        logger.info(f"📸 截图已保存: {path}")

    def close(self):
        """关闭浏览器"""
        if self.download_context:
            self.download_context.close()
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("👋 浏览器已关闭")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main():
    parser = argparse.ArgumentParser(description='OA 合同文件下载工具')
    
    # 查询方式（互斥）
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--contract-code', help='按合同编号下载')
    group.add_argument('--request-id', help='按审批流程ID下载')
    group.add_argument('--keyword', help='按标题关键词搜索并下载（首个匹配）')
    group.add_argument('--batch', help='批量下载（从文件读取合同编号列表，每行一个）')
    
    # 其他选项
    parser.add_argument('--output-dir', help='指定保存目录')
    parser.add_argument('--metadata-only', action='store_true', help='仅提取元信息不下载文件')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--interactive', action='store_true', help='交互式模式（处理验证码）')
    parser.add_argument('--show-browser', action='store_true', help='显示浏览器窗口')
    parser.add_argument('--no-report', action='store_true', help='不生成下载报告文件')
    
    args = parser.parse_args()
    
    try:
        with OAFileDownloader(args.config) as oa:
            oa.launch_browser(headless=not args.show_browser)
            oa.login(interactive=args.interactive)
            
            results = []
            
            if args.contract_code:
                logger.info(f"📥 按合同编号下载: {args.contract_code}")
                result = oa.download_contract(
                    args.contract_code, 'contract_code',
                    args.output_dir, args.metadata_only
                )
                results.append(result)
                
            elif args.request_id:
                logger.info(f"📥 按审批ID下载: {args.request_id}")
                result = oa.download_contract(
                    args.request_id, 'request_id',
                    args.output_dir, args.metadata_only
                )
                results.append(result)
                
            elif args.keyword:
                logger.info(f"📥 按关键词搜索下载: {args.keyword}")
                contracts = oa.search_contract_by_keyword(args.keyword)
                if contracts:
                    # 下载第一个匹配的
                    first_contract = contracts[0]
                    logger.info(f"🎯 选择第一个匹配: {first_contract['title']}")
                    result = oa.download_contract(
                        first_contract.get('contract_code') or first_contract.get('request_id', ''),
                        'contract_code' if first_contract.get('contract_code') else 'request_id',
                        args.output_dir, args.metadata_only
                    )
                    results.append(result)
                else:
                    logger.warning("⚠️  未找到匹配的合同")
                    
            elif args.batch:
                results = oa.batch_download(args.batch, args.output_dir, args.metadata_only)
            
            # 保存报告
            if not args.no_report:
                oa.save_report(args.output_dir)
            
            # 输出结果摘要
            print("\n" + "="*60)
            print("📊 下载任务完成")
            print("="*60)
            total_success = sum(len([f for f in r.get('files', []) if f.get('downloaded')]) for r in results)
            total_files = sum(len(r.get('files', [])) for r in results)
            print(f"  处理合同数: {len(results)}")
            print(f"  总附件数: {total_files}")
            print(f"  下载成功: {total_success}")
            print(f"  下载失败: {total_files - total_success}")
            print("="*60)
            
            logger.info("✅ 下载任务完成！")
                
    except Exception as e:
        logger.error(f"❌ 操作失败: {e}", exc_info=True)
        try:
            if 'oa' in locals():
                oa.take_screenshot('error_download')
        except Exception as screenshot_error:
            logger.warning(f"截图失败: {screenshot_error}")
        exit(1)


if __name__ == '__main__':
    main()
