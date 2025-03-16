#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys
import json

def fix_unicode_escapes(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 处理形如 \\U0001F1FA\\U0001F1F8 的Unicode转义序列（国旗）
        content = re.sub(r'\\\\U0001F1[A-F0-9][A-F0-9]\\\\U0001F1[A-F0-9][A-F0-9]', '国家', content)
        content = re.sub(r'\\U0001F1[A-F0-9][A-F0-9]\\U0001F1[A-F0-9][A-F0-9]', '国家', content)
        
        # 处理形如 "\\U0001F1EC\\U0001F1E7" 的JSON格式Unicode转义序列
        def replace_json_unicode(match):
            try:
                # 尝试解析JSON字符串
                text = json.loads(match.group(0))
                return "国家"
            except:
                return match.group(0)
        
        content = re.sub(r'"\\\\U0001F1[A-F0-9][A-F0-9]\\\\U0001F1[A-F0-9][A-F0-9]"', replace_json_unicode, content)
        
        # 处理形如 \u4e2d\u56fd 的Unicode转义序列
        def replace_unicode(match):
            try:
                # 获取4位十六进制数
                hex_val = match.group(1)
                # 转换为Unicode字符
                return chr(int(hex_val, 16))
            except:
                return match.group(0)
        
        # 替换 \u4e2d 格式的Unicode
        content = re.sub(r'\\u([0-9a-fA-F]{4})', replace_unicode, content)
        
        # 修复国家名称后面跟着"国内"的问题
        content = re.sub(r'([^\s]+)\s国内', r'\1', content)
        
        # 处理特殊格式的节点名称
        # 1. 处理隧道回国点
        content = re.sub(r'(name: ["\'])隧道回国点[^\'"]*(["\'])', r'\1回国节点\2', content)
        content = re.sub(r'(ps: ["\'])隧道回国点[^\'"]*(["\'])', r'\1回国节点\2', content)
        
        # 2. 处理域名和IP地址
        content = re.sub(r'(name: ["\'])[^\'"]*(V2CROSS\.COM|v2cross\.com)[^\'"]*(["\'])', r'\1节点\3', content)
        content = re.sub(r'(ps: ["\'])[^\'"]*(V2CROSS\.COM|v2cross\.com)[^\'"]*(["\'])', r'\1节点\3', content)
        
        # 3. 处理带有特殊符号的节点名称
        content = re.sub(r'(name: ["\'])[^\'"]*(♦|★|☆|◆|●|◎|○|▲|△|▼|▽|◇|□|■|【|】|「|」)[^\'"]*(["\'])', r'\1节点\3', content)
        content = re.sub(r'(ps: ["\'])[^\'"]*(♦|★|☆|◆|●|◎|○|▲|△|▼|▽|◇|□|■|【|】|「|」)[^\'"]*(["\'])', r'\1节点\3', content)
        
        # 替换常见的中文国家/地区名称
        country_names = {
            '挪威': '挪威',
            '中国': '中国',
            '台湾': '台湾',
            '香港': '香港',
            '日本': '日本',
            '韩国': '韩国',
            '美国': '美国',
            '新加坡': '新加坡',
            '印度': '印度',
            '俄罗斯': '俄罗斯',
            '英国': '英国',
            '德国': '德国',
            '法国': '法国',
            '意大利': '意大利',
            '加拿大': '加拿大',
            '澳大利亚': '澳大利亚',
            '荷兰': '荷兰',
            '瑞士': '瑞士',
            '瑞典': '瑞典',
            '芬兰': '芬兰',
            '丹麦': '丹麦',
            '比利时': '比利时',
            '奥地利': '奥地利',
            '西班牙': '西班牙',
            '葡萄牙': '葡萄牙',
            '希腊': '希腊',
            '土耳其': '土耳其',
            '阿联酋': '阿联酋',
            '以色列': '以色列',
            '沙特': '沙特',
            '巴西': '巴西',
            '阿根廷': '阿根廷',
            '墨西哥': '墨西哥',
            '南非': '南非',
            '埃及': '埃及',
            '泰国': '泰国',
            '马来西亚': '马来西亚',
            '印尼': '印尼',
            '菲律宾': '菲律宾',
            '越南': '越南',
            '柬埔寨': '柬埔寨',
            '缅甸': '缅甸',
            '尼泊尔': '尼泊尔',
            '巴基斯坦': '巴基斯坦',
            '孟加拉': '孟加拉',
            '斯里兰卡': '斯里兰卡',
            '哈萨克斯坦': '哈萨克斯坦',
            '乌兹别克斯坦': '乌兹别克斯坦',
            '乌克兰': '乌克兰',
            '白俄罗斯': '白俄罗斯',
            '波兰': '波兰',
            '捷克': '捷克',
            '匈牙利': '匈牙利',
            '罗马尼亚': '罗马尼亚',
            '保加利亚': '保加利亚',
            '塞尔维亚': '塞尔维亚',
            'Telegram': 'Telegram',
            'trojan': 'trojan',
            'vmess': 'vmess',
            'vless': 'vless',
            'hysteria2': 'hysteria2',
            'ss': 'ss'
        }
        
        # 替换国家名称
        for country, replacement in country_names.items():
            # 替换形如 "name: "挪威 1.1MB/s"" 的格式
            content = re.sub(f'(name: ")[^"]*({country})[^"]*(")', f'\\1\\2\\3', content)
            # 替换形如 "name: '挪威 1.1MB/s'" 的格式
            content = re.sub(f"(name: ')[^']*({country})[^']*(')", f'\\1\\2\\3', content)
            # 替换形如 "ps: "挪威 1.1MB/s"" 的格式
            content = re.sub(f'(ps: ")[^"]*({country})[^"]*(")', f'\\1\\2\\3', content)
            # 替换形如 "ps: '挪威 1.1MB/s'" 的格式
            content = re.sub(f"(ps: ')[^']*({country})[^']*(')", f'\\1\\2\\3', content)
        
        # 最后清理任何剩余的"国内"文本
        content = re.sub(r'国内\s+', '', content)
        content = re.sub(r'\s+国内', '', content)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python fix_unicode.py <文件路径>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    success = fix_unicode_escapes(file_path)
    
    if success:
        print(f"成功处理文件: {file_path}")
    else:
        print(f"处理文件失败: {file_path}")
        sys.exit(1) 