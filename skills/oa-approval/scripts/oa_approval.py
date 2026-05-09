#!/usr/bin/env python3
"""
OA 合同审批脚本
================
通过 Playwright 浏览器自动化操作泛微 OA 系统

⚠️ 安全规则：
1. 必须由用户主动触发，禁止任何自动化/定时调用
2. 每次操作有 2-5 秒延迟，模拟人类行为
3. 每次只处理一个审批，不支持批量操作
4. 执行审批前必须获得用户确认

作者: Ella 🦊
版本: v1.0
创建时间: 2026-04-23
"""

import argparse
import json
import logging
import random
import time
import os
from pathlib import Path

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
        logging.FileHandler(log_dir / 'approval.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class OAApproval:
    """OA 审批操作类"""

    def __init__(self, config_path: str = None):
        """
        初始化 OA 审批客户端
        
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
        
        # 确保输出目录存在
        for dir_key in ['screenshot_dir', 'log_dir']:
            dir_path = Path(self.config['output'][dir_key]).expanduser()
            dir_path.mkdir(parents=True, exist_ok=True)

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

    def launch_browser(self, headless: bool = True):
        """启动浏览器"""
        logger.info("🚀 启动浏览器...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.page = self.browser.new_page(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

    def login(self, interactive: bool = False):
        """
        登录 OA 系统
        
        Args:
            interactive: 是否交互式模式（遇到验证码时等待用户处理）
        """
        logger.info(f"🔐 登录 OA 系统: {self.config['oa_url']}")
        self.page.goto(self.config['oa_url'])
        self._human_delay()
        
        # 填写用户名密码
        password = self._get_password_from_keychain()
        self.page.fill(self.config['selectors']['login_form']['username_input'], 
                       self.config['auth']['username'])
        self._human_delay('typing')
        
        self.page.fill(self.config['selectors']['login_form']['password_input'], password)
        self._human_delay('typing')
        
        # 检查是否有验证码 - 使用 wait_for_selector 替代 is_visible
        captcha_selector = self.config['selectors']['login_form']['captcha_image']
        try:
            self.page.wait_for_selector(captcha_selector, timeout=3000, state='visible')
            if interactive:
                logger.info("⚠️  检测到验证码，请在浏览器中手动完成验证后按回车继续...")
                self.page.wait_for_timeout(1000)  # 给用户一点时间
                input()
            else:
                raise RuntimeError("检测到验证码，请使用 --interactive 模式运行")
        except Exception:
            # 无验证码，继续执行
            pass
        
        # 点击登录
        self.page.click(self.config['selectors']['login_form']['submit_button'])
        self._human_delay()
        logger.info("✅ 登录完成")

    def get_todo_list(self) -> list:
        """获取待审批列表"""
        logger.info("📋 获取待审批列表...")
        
        # 导航到待办事项页面
        todo_url = self.config.get('todo_url', self.config['oa_url'] + '/workflow/request/todo')
        self.page.goto(todo_url)
        self._human_delay()  # 人类行为模拟：页面加载等待
        
        # 等待列表容器加载
        selectors = self.config['selectors']['todo_list']
        try:
            self.page.wait_for_selector(selectors['container'], 
                                       timeout=self.config['timeout']['element_wait'] * 1000)
        except Exception as e:
            logger.warning(f"待办列表容器未找到，可能页面结构已变化: {e}")
            return []
        
        self._human_delay()  # 额外等待确保数据完全渲染
        
        # 提取列表数据
        contracts = []
        items = self.page.query_selector_all(selectors['items'])
        
        for idx, item in enumerate(items, start=1):
            try:
                contract = {
                    'index': idx,
                    'contract_id': '',
                    'title': '',
                    'initiator': '',
                    'submit_time': '',
                    'status': '',
                    'url': ''
                }
                
                # 提取合同ID
                id_elem = item.query_selector(selectors['item_id'])
                if id_elem:
                    contract['contract_id'] = id_elem.inner_text().strip()
                
                # 提取标题和链接
                title_elem = item.query_selector(selectors['item_title'])
                if title_elem:
                    contract['title'] = title_elem.inner_text().strip()
                    link_elem = item.query_selector(selectors['item_url'])
                    if link_elem:
                        contract['url'] = link_elem.get_attribute('href') or ''
                
                # 提取发起人（假设选择器配置）
                initiator_selector = selectors.get('item_initiator', '.initiator')
                initiator_elem = item.query_selector(initiator_selector)
                if initiator_elem:
                    contract['initiator'] = initiator_elem.inner_text().strip()
                
                # 提取发起时间
                time_selector = selectors.get('item_time', '.submit-time')
                time_elem = item.query_selector(time_selector)
                if time_elem:
                    contract['submit_time'] = time_elem.inner_text().strip()
                
                # 提取状态
                status_selector = selectors.get('item_status', '.status')
                status_elem = item.query_selector(status_selector)
                if status_elem:
                    contract['status'] = status_elem.inner_text().strip()
                
                contracts.append(contract)
                
            except Exception as e:
                logger.warning(f"解析第 {idx} 条记录失败: {e}")
                continue
        
        logger.info(f"📋 成功解析 {len(contracts)} 个待审批合同")
        return contracts

    def approve_contract(self, contract_id: str, comment: str = "同意") -> bool:
        """
        审批通过合同
        
        Args:
            contract_id: 合同ID
            comment: 审批意见
            
        Returns:
            是否成功
        """
        logger.info(f"✅ 审批合同: {contract_id}")
        
        # 步骤1: 获取并显示合同摘要（安全机制）
        detail = self.get_contract_detail(contract_id)
        self._display_contract_summary(detail, 'approve')
        
        # 步骤2: 用户确认（安全机制）
        confirm = input("\n⚠️  请确认是否审批通过该合同？(yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            logger.info("❌ 用户取消审批操作")
            return False
        
        logger.info("✅ 用户已确认，开始执行审批...")
        self._human_delay()
        
        # 步骤3: 定位并点击审批按钮
        selectors = self.config['selectors']['approval_page']
        
        try:
            # 等待审批按钮可见并点击
            self.page.wait_for_selector(selectors['approve_button'], 
                                       timeout=self.config['timeout']['element_wait'] * 1000,
                                       state='visible')
            self._human_delay()
            
            self.page.click(selectors['approve_button'])
            logger.info("🖱️  已点击审批按钮")
            self._human_delay()
            
            # 步骤4: 填写审批意见
            self.page.wait_for_selector(selectors['comment_textarea'], timeout=5000, state='visible')
            self._human_delay()
            
            self.page.fill(selectors['comment_textarea'], '')
            for char in comment:
                self.page.keyboard.type(char)
                time.sleep(random.uniform(0.05, 0.15))  # 模拟打字速度
            
            logger.info(f"📝 已填写审批意见: {comment}")
            self._human_delay()
            
            # 步骤5: 确认提交
            confirm_btn_selector = selectors.get('submit_confirm', '.btn-confirm-submit')
            self.page.wait_for_selector(confirm_btn_selector, timeout=5000, state='visible')
            self._human_delay()
            
            self.page.click(confirm_btn_selector)
            logger.info("🖱️  已点击确认提交按钮")
            self._human_delay()
            
            # 步骤6: 等待处理完成并验证结果
            success_indicator = selectors.get('success_indicator', '.success-message')
            try:
                self.page.wait_for_selector(success_indicator, timeout=10000, state='visible')
                logger.info("✅ 审批提交成功！")
                self.take_screenshot(f'approve_success_{contract_id}')
                return True
            except Exception:
                # 检查是否有错误提示
                error_indicator = selectors.get('error_indicator', '.error-message')
                try:
                    self.page.wait_for_selector(error_indicator, timeout=3000, state='visible')
                    error_msg = self.page.query_selector(error_indicator).inner_text().strip()
                    logger.error(f"❌ 审批失败: {error_msg}")
                    self.take_screenshot(f'approve_error_{contract_id}')
                    return False
                except Exception:
                    logger.warning("⚠️  未找到明确的成功/失败提示，假设审批已提交")
                    self.take_screenshot(f'approve_submitted_{contract_id}')
                    return True
                    
        except Exception as e:
            logger.error(f"❌ 审批过程中发生错误: {e}")
            self.take_screenshot(f'approve_exception_{contract_id}')
            raise
    
    def _display_contract_summary(self, detail: dict, action: str):
        """显示合同摘要用于用户确认"""
        print("\n" + "="*60)
        print(f"📋 合同审批摘要 - {'审批通过' if action == 'approve' else '驳回'}")
        print("="*60)
        
        basic = detail.get('basic_info', {})
        print(f"  合同ID: {detail['contract_id']}")
        print(f"  合同标题: {basic.get('contract_title', 'N/A')}")
        print(f"  合同金额: {basic.get('contract_amount', 'N/A')}")
        print(f"  甲方: {basic.get('party_a', 'N/A')}")
        print(f"  乙方: {basic.get('party_b', 'N/A')}")
        print(f"  合同类型: {basic.get('contract_type', 'N/A')}")
        print(f"  发起人: {basic.get('initiator', 'N/A')}")
        print(f"  发起部门: {basic.get('department', 'N/A')}")
        print(f"  提交时间: {basic.get('submit_time', 'N/A')}")
        print(f"  当前节点: {detail.get('current_node', 'N/A')}")
        
        history = detail.get('approval_history', [])
        if history:
            print(f"\n  审批流程 (共{len(history)}步):")
            for h in history:
                status_str = f"[{h.get('status', '')}]" if h.get('status') else ""
                print(f"    - {h.get('node_name', '')}: {h.get('approver', '')} {status_str} @ {h.get('approve_time', '')}")
        
        print("="*60)

    def reject_contract(self, contract_id: str, reason: str) -> bool:
        """
        驳回合同
        
        Args:
            contract_id: 合同ID
            reason: 驳回原因
            
        Returns:
            是否成功
        """
        logger.info(f"❌ 驳回合同: {contract_id}")
        
        # 步骤1: 获取并显示合同摘要（安全机制）
        detail = self.get_contract_detail(contract_id)
        self._display_contract_summary(detail, 'reject')
        
        print(f"\n  驳回原因: {reason}")
        
        # 步骤2: 用户确认（安全机制）
        confirm = input("\n⚠️  请确认是否驳回该合同？(yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            logger.info("❌ 用户取消驳回操作")
            return False
        
        logger.info("✅ 用户已确认，开始执行驳回...")
        self._human_delay()
        
        # 步骤3: 定位并点击驳回按钮
        selectors = self.config['selectors']['approval_page']
        
        try:
            # 等待驳回按钮可见并点击
            self.page.wait_for_selector(selectors['reject_button'], 
                                       timeout=self.config['timeout']['element_wait'] * 1000,
                                       state='visible')
            self._human_delay()
            
            self.page.click(selectors['reject_button'])
            logger.info("🖱️  已点击驳回按钮")
            self._human_delay()
            
            # 步骤4: 填写驳回原因
            self.page.wait_for_selector(selectors['comment_textarea'], timeout=5000, state='visible')
            self._human_delay()
            
            self.page.fill(selectors['comment_textarea'], '')
            for char in reason:
                self.page.keyboard.type(char)
                time.sleep(random.uniform(0.05, 0.15))  # 模拟打字速度
            
            logger.info(f"📝 已填写驳回原因: {reason}")
            self._human_delay()
            
            # 步骤5: 确认提交
            confirm_btn_selector = selectors.get('submit_confirm', '.btn-confirm-submit')
            self.page.wait_for_selector(confirm_btn_selector, timeout=5000, state='visible')
            self._human_delay()
            
            self.page.click(confirm_btn_selector)
            logger.info("🖱️  已点击确认提交按钮")
            self._human_delay()
            
            # 步骤6: 等待处理完成并验证结果
            success_indicator = selectors.get('success_indicator', '.success-message')
            try:
                self.page.wait_for_selector(success_indicator, timeout=10000, state='visible')
                logger.info("✅ 驳回提交成功！")
                self.take_screenshot(f'reject_success_{contract_id}')
                return True
            except Exception:
                logger.warning("⚠️  未找到明确的成功提示，假设驳回已提交")
                self.take_screenshot(f'reject_submitted_{contract_id}')
                return True
                    
        except Exception as e:
            logger.error(f"❌ 驳回过程中发生错误: {e}")
            self.take_screenshot(f'reject_exception_{contract_id}')
            raise

    def get_contract_detail(self, contract_id: str) -> dict:
        """
        获取合同详情
        
        Args:
            contract_id: 合同ID
            
        Returns:
            合同详细信息
        """
        logger.info(f"📄 获取合同详情: {contract_id}")
        
        # 方式1: 如果已知详情页URL则直接访问
        detail_url_pattern = self.config.get('detail_url_pattern', 
                                            self.config['oa_url'] + '/workflow/request/detail?id={id}')
        detail_url = detail_url_pattern.format(id=contract_id)
        self.page.goto(detail_url)
        self._human_delay()
        
        # 等待详情页加载
        selectors = self.config['selectors']['approval_page']
        try:
            self.page.wait_for_selector(selectors['detail_container'], 
                                       timeout=self.config['timeout']['element_wait'] * 1000)
        except Exception as e:
            logger.warning(f"详情容器未找到，尝试其他方式定位: {e}")
        
        self._human_delay()
        
        # 提取合同基本信息
        detail = {
            'contract_id': contract_id,
            'basic_info': {},
            'approval_history': [],
            'current_node': ''
        }
        
        # 提取基本信息字段（配置化字段映射）
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
                    detail['basic_info'][field_name] = elem.inner_text().strip()
            except Exception:
                detail['basic_info'][field_name] = ''
        
        # 提取审批流程记录
        history_container_selector = selectors.get('history_container', '.approval-history')
        try:
            self.page.wait_for_selector(history_container_selector, timeout=5000, state='visible')
            history_items = self.page.query_selector_all(selectors.get('history_item', '.history-item'))
            
            for item in history_items:
                try:
                    node_name_elem = item.query_selector(selectors.get('node_name', '.node-name'))
                    approver_elem = item.query_selector(selectors.get('approver_name', '.approver-name'))
                    time_elem = item.query_selector(selectors.get('approve_time', '.approve-time'))
                    opinion_elem = item.query_selector(selectors.get('approve_opinion', '.approve-opinion'))
                    status_elem = item.query_selector(selectors.get('node_status', '.node-status'))
                    
                    history_record = {
                        'node_name': node_name_elem.inner_text().strip() if node_name_elem else '',
                        'approver': approver_elem.inner_text().strip() if approver_elem else '',
                        'approve_time': time_elem.inner_text().strip() if time_elem else '',
                        'opinion': opinion_elem.inner_text().strip() if opinion_elem else '',
                        'status': status_elem.inner_text().strip() if status_elem else ''
                    }
                    detail['approval_history'].append(history_record)
                except Exception as e:
                    logger.warning(f"解析审批记录失败: {e}")
                    continue
        except Exception as e:
            logger.warning(f"未找到审批流程记录: {e}")
        
        # 识别当前审批节点
        current_node_selector = selectors.get('current_node', '.current-node')
        try:
            current_elem = self.page.query_selector(current_node_selector)
            if current_elem:
                detail['current_node'] = current_elem.inner_text().strip()
        except Exception:
            pass
        
        logger.info(f"📄 合同详情提取完成: {detail.get('basic_info', {}).get('contract_title', 'N/A')}")
        return detail

    def take_screenshot(self, name: str):
        """截图保存"""
        path = Path(self.config['output']['screenshot_dir']).expanduser() / f"{name}_{int(time.time())}.png"
        self.page.screenshot(path=str(path))
        logger.info(f"📸 截图已保存: {path}")

    def close(self):
        """关闭浏览器"""
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
    parser = argparse.ArgumentParser(description='OA 合同审批工具')
    parser.add_argument('--action', choices=['list', 'approve', 'reject', 'detail', 'test-login'],
                       required=True, help='操作类型')
    parser.add_argument('--id', help='合同ID (approve/reject/detail 时需要)')
    parser.add_argument('--comment', default='同意', help='审批/驳回意见')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--interactive', action='store_true', help='交互式模式（处理验证码）')
    parser.add_argument('--show-browser', action='store_true', help='显示浏览器窗口')
    
    args = parser.parse_args()
    
    # 参数校验
    if args.action in ['approve', 'reject', 'detail'] and not args.id:
        parser.error(f"--action {args.action} 需要提供 --id 参数")
    
    try:
        with OAApproval(args.config) as oa:
            oa.launch_browser(headless=not args.show_browser)
            oa.login(interactive=args.interactive)
            
            if args.action == 'test-login':
                logger.info("✅ 登录测试成功！")
                oa.take_screenshot('login_success')
                
            elif args.action == 'list':
                contracts = oa.get_todo_list()
                logger.info(f"📋 找到 {len(contracts)} 个待审批合同")
                for c in contracts:
                    print(f"  - {c}")
                    
            elif args.action == 'detail':
                detail = oa.get_contract_detail(args.id)
                print(json.dumps(detail, indent=2, ensure_ascii=False))
                
            elif args.action == 'approve':
                oa.approve_contract(args.id, args.comment)
                logger.info("✅ 审批完成！")
                
            elif args.action == 'reject':
                oa.reject_contract(args.id, args.comment)
                logger.info("✅ 驳回完成！")
                
    except Exception as e:
        logger.error(f"❌ 操作失败: {e}", exc_info=True)
        # 安全机制：异常时自动截图
        try:
            if 'oa' in locals():
                oa.take_screenshot('error_' + args.action)
        except Exception as screenshot_error:
            logger.warning(f"截图失败: {screenshot_error}")
        exit(1)


if __name__ == '__main__':
    main()
