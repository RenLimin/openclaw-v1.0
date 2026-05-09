#!/usr/bin/env python3
"""
邮件管理脚本
============
通过 IMAP/SMTP 协议管理企业邮箱，支持检查、分类、搜索、发送等功能

⚠️ 安全规则：
1. 必须由用户主动触发，禁止任何自动化/定时调用
2. 每封邮件分析间隔 1-3 秒，模拟人类阅读行为
3. 单次最多检查 50 封邮件，防止频繁调用
4. 敏感内容本地处理，不上传到第三方模型
5. 发送/回复邮件前必须获得用户明确确认

作者: Iris 🐦‍⬛
版本: v1.0
创建时间: 2026-04-23
"""

import argparse
import email
import imaplib
import json
import logging
import os
import random
import re
import smtplib
import time
from datetime import datetime
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ 请先安装 beautifulsoup4: pip install beautifulsoup4")
    exit(1)

# 确保日志目录存在（模块级初始化）
log_dir = Path.home() / '.openclaw' / 'output' / 'email-logs'
log_dir.mkdir(parents=True, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'email_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EmailManager:
    """邮件管理类"""

    def __init__(self, config_path: str = None):
        """
        初始化邮件管理器
        
        Args:
            config_path: 配置文件路径
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'email-config.json'
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.imap_conn = None
        self.smtp_conn = None
        
        # 确保输出目录存在
        for dir_key in ['report_dir', 'attachment_dir']:
            dir_path = Path(self.config['output'][dir_key]).expanduser()
            dir_path.mkdir(parents=True, exist_ok=True)

    def _human_delay(self, delay_type: str = 'email'):
        """
        模拟人类阅读/操作延迟
        
        Args:
            delay_type: 'email' (邮件分析) 或 'batch' (批处理间隔)
        """
        if delay_type == 'email':
            delay = random.uniform(
                self.config['processing']['email_analysis_delay_min'],
                self.config['processing']['email_analysis_delay_max']
            )
        else:  # batch
            delay = self.config['processing']['batch_delay_seconds']
        time.sleep(delay)

    def _get_password_from_keychain(self, service_name: str) -> str:
        """从 macOS Keychain 获取密码"""
        import subprocess
        result = subprocess.run([
            'security', 'find-generic-password',
            '-s', service_name,
            '-w'
        ], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"无法从 Keychain 获取密码: {service_name}，请先配置")
        return result.stdout.strip()

    def connect_imap(self):
        """连接 IMAP 服务器"""
        logger.info(f"📡 连接 IMAP 服务器: {self.config['imap']['server']}")
        password = self._get_password_from_keychain(self.config['imap']['keychain_service'])
        self.imap_conn = imaplib.IMAP4_SSL(
            self.config['imap']['server'],
            self.config['imap']['port']
        )
        self.imap_conn.login(self.config['imap']['username'], password)
        logger.info("✅ IMAP 连接成功")

    def connect_smtp(self):
        """连接 SMTP 服务器"""
        logger.info(f"📡 连接 SMTP 服务器: {self.config['smtp']['server']}")
        password = self._get_password_from_keychain(self.config['smtp']['keychain_service'])
        self.smtp_conn = smtplib.SMTP_SSL(
            self.config['smtp']['server'],
            self.config['smtp']['port']
        )
        self.smtp_conn.login(self.config['smtp']['username'], password)
        logger.info("✅ SMTP 连接成功")

    def _decode_email_header(self, header: str) -> str:
        """解码邮件标题/发件人等头信息"""
        if not header:
            return ""
        decoded_parts = decode_header(header)
        result = []
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                if encoding:
                    try:
                        result.append(part.decode(encoding))
                    except:
                        result.append(part.decode('utf-8', errors='ignore'))
                else:
                    result.append(part.decode('utf-8', errors='ignore'))
            else:
                result.append(str(part))
        return ''.join(result)

    def _parse_email_body(self, msg: email.message.Message) -> str:
        """解析邮件正文"""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        payload = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        body += payload
                    except:
                        pass
                elif content_type == "text/html" and "attachment" not in content_disposition:
                    try:
                        payload = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        soup = BeautifulSoup(payload, 'html.parser')
                        body += soup.get_text(separator='\n', strip=True)
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(msg.get_payload())
        
        return body.strip()

    def _classify_email(self, subject: str, from_addr: str, to_addr: str = "", body: str = "") -> Dict[str, str]:
        """
        根据规则分类邮件
        
        Args:
            subject: 邮件主题
            from_addr: 发件人地址
            to_addr: 收件人地址
            body: 邮件正文
            
        Returns:
            {level, name, reason}
        """
        self._human_delay('email')  # 模拟人类阅读判断时间
        
        subject_lower = subject.lower() if subject else ""
        from_lower = from_addr.lower() if from_addr else ""
        username = self.config['imap']['username'].lower()
        
        # P0: 发件人含 oa@* + 主题含「审批/待审批/请审批」
        oa_pattern = r'oa@|workflow@'
        approval_pattern = r'审批|待审批|请审批|待审核|审批提醒'
        
        if re.search(oa_pattern, from_lower) and re.search(approval_pattern, subject_lower):
            return {
                "level": "P0",
                "name": "审批提醒",
                "reason": "发件人含 OA 系统地址且主题含审批关键词"
            }
        
        # P1: 直接发送给本人（收件人 == username）
        if to_addr and username in to_addr.lower():
            return {
                "level": "P1",
                "name": "工作邮件",
                "reason": "邮件直接发送给本人"
            }
        
        # P3: 系统通知、广告等特征检测
        notification_pattern = r'订阅|推广|优惠|新闻|公告|通知|noreply|no-reply|system'
        if re.search(notification_pattern, subject_lower) or re.search(r'noreply|no-reply|system|notify', from_lower):
            return {
                "level": "P3",
                "name": "通知广告",
                "reason": "系统通知或营销类邮件特征"
            }
        
        # P2: 普通外部邮件（默认）
        return {
            "level": "P2",
            "name": "普通邮件",
            "reason": "普通外部或内部邮件"
        }

    def get_email_list(self, folder: str = "INBOX", limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取邮件列表
        
        Args:
            folder: 邮件文件夹
            limit: 获取邮件数量
            
        Returns:
            邮件列表（按时间倒序）
        """
        limit = min(limit, self.config['processing']['max_limit'])
        logger.info(f"📥 获取 {folder} 文件夹的最新 {limit} 封邮件")
        
        self.imap_conn.select(folder)
        
        # 搜索所有邮件
        status, messages = self.imap_conn.search(None, "ALL")
        email_ids = messages[0].split()[-limit:]  # 取最新的 N 封
        
        emails = []
        for i, email_id in enumerate(reversed(email_ids)):
            try:
                status, msg_data = self.imap_conn.fetch(email_id, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])
                
                subject = self._decode_email_header(msg["Subject"])
                from_addr = self._decode_email_header(msg["From"])
                to_addr = self._decode_email_header(msg.get("To", ""))
                date = msg["Date"]
                
                # 解析正文摘要
                body = self._parse_email_body(msg)
                body_summary = body[:100].strip().replace('\n', ' ') if body else ""
                if len(body) > 100:
                    body_summary += "..."
                
                # 分类
                classification = self._classify_email(subject, from_addr, to_addr, body)
                
                emails.append({
                    "id": email_id.decode(),
                    "subject": subject or "(无主题)",
                    "from": from_addr or "(未知发件人)",
                    "to": to_addr,
                    "date": date,
                    "body_summary": body_summary,
                    "classification": classification
                })
            except Exception as e:
                logger.warning(f"⚠️  解析邮件 ID {email_id} 失败: {e}")
                continue
            
            # 每 10 封邮件延迟一下
            if (i + 1) % 10 == 0 and i < len(email_ids) - 1:
                self._human_delay('batch')
                logger.info(f"  已处理 {i + 1}/{len(email_ids)} 封邮件")
        
        # 按时间倒序返回（已通过 reversed(email_ids) 保证）
        return emails

    def search_emails(self, keyword: str = "", from_addr: str = "", 
                     subject_only: bool = True) -> List[Dict[str, Any]]:
        """
        搜索邮件
        
        Args:
            keyword: 搜索关键词
            from_addr: 发件人过滤
            subject_only: 仅搜索主题
            
        Returns:
            匹配的邮件列表
        """
        logger.info(f"🔍 搜索邮件: keyword='{keyword}', from='{from_addr}'")
        # TODO: 实现邮件搜索逻辑
        return []

    def export_attachments(self, email_id: str, output_dir: str = None) -> List[str]:
        """
        导出邮件附件
        
        Args:
            email_id: 邮件 ID
            output_dir: 输出目录
            
        Returns:
            导出的文件路径列表
        """
        logger.info(f"📎 导出邮件附件: {email_id}")
        # TODO: 实现附件导出逻辑
        # 注意：检查文件类型和大小，禁止可执行文件
        return []

    def send_email(self, to: str, subject: str, body: str, 
                  attachments: List[str] = None, confirm: bool = True) -> bool:
        """
        发送邮件
        
        Args:
            to: 收件人
            subject: 主题
            body: 正文
            attachments: 附件路径列表
            confirm: 是否需要用户确认
            
        Returns:
            是否成功
        """
        if confirm:
            print(f"\n⚠️  请确认发送邮件：")
            print(f"   收件人: {to}")
            print(f"   主题: {subject}")
            print(f"   正文长度: {len(body)} 字符")
            if attachments:
                print(f"   附件: {len(attachments)} 个")
            if input("\n确认发送? (yes/no): ").lower() != 'yes':
                logger.info("❌ 用户取消发送")
                return False
        
        logger.info(f"✉️  发送邮件到: {to}")
        # TODO: 实现发送逻辑
        return True

    def generate_report(self, emails: List[Dict[str, Any]], format: str = "markdown") -> str:
        """
        生成邮件检查报告
        
        Args:
            emails: 邮件列表
            format: 输出格式
            
        Returns:
            报告内容
        """
        logger.info("📝 生成检查报告...")
        
        # 按分类分组
        classified = {
            "P0": [],
            "P1": [],
            "P2": [],
            "P3": []
        }
        
        for email_item in emails:
            level = email_item["classification"]["level"]
            if level in classified:
                classified[level].append(email_item)
        
        # 生成报告
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        report_lines = [
            f"# 📧 邮件检查报告（{now}）",
            "",
            "## 📊 统计汇总",
            "",
            f"- 总计检查: **{len(emails)}** 封",
            f"- 🔴 P0 审批提醒: **{len(classified['P0'])}** 封",
            f"- 🟡 P1 工作邮件: **{len(classified['P1'])}** 封",
            f"- 🟢 P2 普通邮件: **{len(classified['P2'])}** 封",
            f"- ⚪ P3 通知广告: **{len(classified['P3'])}** 封",
            ""
        ]
        
        # P0 审批提醒
        if classified['P0']:
            report_lines.extend([
                "## 🔴 P0 审批提醒",
                ""
            ])
            for i, email_item in enumerate(classified['P0'], 1):
                report_lines.extend([
                    f"{i}. **{email_item['subject']}**",
                    f"   - 发件人: {email_item['from']}",
                    f"   - 时间: {email_item['date']}",
                    f"   - 原因: {email_item['classification']['reason']}",
                    ""
                ])
        
        # P1 工作邮件
        if classified['P1']:
            report_lines.extend([
                "## 🟡 P1 工作邮件",
                ""
            ])
            for i, email_item in enumerate(classified['P1'], 1):
                report_lines.extend([
                    f"{i}. **{email_item['subject']}**",
                    f"   - 发件人: {email_item['from']}",
                    f"   - 时间: {email_item['date']}",
                    f"   - 摘要: {email_item.get('body_summary', '无')}",
                    ""
                ])
        
        # P2 普通邮件
        if classified['P2']:
            report_lines.extend([
                "## 🟢 P2 普通邮件",
                ""
            ])
            for i, email_item in enumerate(classified['P2'], 1):
                report_lines.extend([
                    f"{i}. {email_item['subject']}",
                    f"   - 发件人: {email_item['from']}",
                    ""
                ])
        
        # P3 通知广告
        if classified['P3']:
            report_lines.extend([
                "## ⚪ P3 通知广告",
                ""
            ])
            for i, email_item in enumerate(classified['P3'], 1):
                report_lines.append(f"{i}. {email_item['subject']} ({email_item['from']})")
            report_lines.append("")
        
        report = "\n".join(report_lines)
        
        # 输出到 stdout
        print(report)
        
        return report

    def close(self):
        """关闭连接"""
        if self.imap_conn:
            try:
                self.imap_conn.close()
                self.imap_conn.logout()
            except:
                pass
        if self.smtp_conn:
            try:
                self.smtp_conn.quit()
            except:
                pass
        logger.info("👋 连接已关闭")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main():
    parser = argparse.ArgumentParser(description='邮件管理工具')
    parser.add_argument('--action', 
                       choices=['check', 'classify', 'search', 'send', 
                               'export-attachments', 'test-connection', 'test-classification'],
                       required=True, help='操作类型')
    parser.add_argument('--folder', default='INBOX', help='邮件文件夹')
    parser.add_argument('--limit', type=int, default=20, help='获取邮件数量')
    parser.add_argument('--keyword', help='搜索关键词')
    parser.add_argument('--from', dest='from_addr', help='发件人过滤')
    parser.add_argument('--to', help='收件人邮箱 (send 时需要)')
    parser.add_argument('--subject', help='邮件主题 (send 时需要)')
    parser.add_argument('--body', help='邮件正文 (send 时需要)')
    parser.add_argument('--attach', action='append', help='附件路径 (可多次指定)')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--sample', help='测试分类的样本邮件主题')
    parser.add_argument('--no-confirm', action='store_true', help='跳过发送确认（不推荐）')
    
    args = parser.parse_args()
    
    # 测试模式
    if args.action == 'test-connection':
        logger.info("🧪 测试 IMAP 连接...")
        try:
            with EmailManager(args.config) as em:
                em.connect_imap()
            print("✅ 连接测试成功！")
        except Exception as e:
            logger.error(f"❌ 连接测试失败: {e}")
            exit(1)
        return
    
    if args.action == 'test-classification':
        logger.info(f"🧪 测试分类规则: {args.sample}")
        em = EmailManager(args.config)
        result = em._classify_email(args.sample or "", "")
        print(f"分类结果: {result}")
        return
    
    try:
        with EmailManager(args.config) as em:
            em.connect_imap()
            
            if args.action in ['check', 'classify']:
                emails = em.get_email_list(args.folder, args.limit)
                report = em.generate_report(emails, 'markdown')
                
                if args.output:
                    output_path = Path(args.output).expanduser()
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(report)
                    logger.info(f"💾 报告已保存到: {output_path}")
                else:
                    print(report)
            
            elif args.action == 'search':
                emails = em.search_emails(args.keyword, args.from_addr)
                logger.info(f"找到 {len(emails)} 封匹配邮件")
                for e in emails:
                    print(f"  - {e['subject']} ({e['from']})")
            
            elif args.action == 'send':
                if not all([args.to, args.subject, args.body]):
                    parser.error("--action send 需要提供 --to, --subject, --body 参数")
                em.connect_smtp()
                em.send_email(
                    args.to, args.subject, args.body,
                    args.attach, confirm=not args.no_confirm
                )
            
            elif args.action == 'export-attachments':
                # TODO: 支持指定邮件 ID 或批量导出
                logger.info("📎 附件导出功能开发中...")
            
    except Exception as e:
        logger.error(f"❌ 操作失败: {e}", exc_info=True)
        exit(1)


if __name__ == '__main__':
    main()
