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
        
        # 常见的国家名称
        country_names = [
            '挪威', '中国', '台湾', '香港', '日本', '韩国', '美国', '新加坡', '印度', '俄罗斯',
            '英国', '德国', '法国', '意大利', '加拿大', '澳大利亚', '荷兰', '瑞士', '瑞典', '芬兰',
            '丹麦', '比利时', '奥地利', '西班牙', '葡萄牙', '希腊', '土耳其', '阿联酋', '以色列', '沙特',
            '巴西', '阿根廷', '墨西哥', '南非', '埃及', '泰国', '马来西亚', '印尼', '菲律宾', '越南',
            '柬埔寨', '缅甸', '尼泊尔', '巴基斯坦', '孟加拉', '斯里兰卡', '哈萨克斯坦', '乌兹别克斯坦', '乌克兰', '白俄罗斯',
            '波兰', '捷克', '匈牙利', '罗马尼亚', '保加利亚', '塞尔维亚'
        ]

        # 首先预处理常见问题格式
        
        # 1. 处理"国内"粘连问题，为常见国家名称和"国内"之间添加空格便于后续处理
        for country in country_names:
            content = re.sub(f'({country})国内', f'\\1 国内', content)
        
        # 2. 清理形如 "2|搜精 3" 的数字前缀
        content = re.sub(r'(name: ["\']).?\|[^|]+\|', r'\1', content)
        content = re.sub(r'(ps: ["\']).?\|[^|]+\|', r'\1', content)
        
        # 3. 清理特定服务商标识和域名
        service_providers = [
            'CloudFlare', 'cloudflare', 'AWS', 'AZURE', 'GCP', 
            'Oracle', 'oracle', 'Azure', 'aws',
            '权威商', '狸床床', '搜精', 'V2CROSS', 'v2cross', 
            'ORACLE', 'LINODE', 'linode', 'DO', 'Vultr', 'vultr',
            'GIA', 'gia', 'IPLC', 'iplc', 'BGP', 'bgp', 'CN2', 'cn2'
        ]
        
        # 清理节点名称中的服务商标识
        for provider in service_providers:
            content = re.sub(f'(name: ["\'])[^"\']*{provider}[^"\']*(["\'])', r'\1节点\2', content)
            content = re.sub(f'(ps: ["\'])[^"\']*{provider}[^"\']*(["\'])', r'\1节点\2', content)
        
        # 4. 清理带有特殊符号的节点名称
        special_chars = r'[♦★☆◆●◎○▲△▼▽◇□■【】「」❤️💕💗💞💘❤]'
        content = re.sub(f'(name: ["\'])[^"\']*{special_chars}[^"\']*(["\'])', r'\1节点\2', content)
        content = re.sub(f'(ps: ["\'])[^"\']*{special_chars}[^"\']*(["\'])', r'\1节点\2', content)
        
        # 5. 处理隧道回国点
        content = re.sub(r'(name: ["\'])隧道回国点[^\'"]*(["\'])', r'\1回国节点\2', content)
        content = re.sub(r'(ps: ["\'])隧道回国点[^\'"]*(["\'])', r'\1回国节点\2', content)
        
        # 6. 处理带网址和IP的节点
        content = re.sub(r'(name: ["\'])[^\'"]*((?:\d{1,3}\.){3}\d{1,3})[^\'"]*(["\'])', r'\1节点\3', content)
        content = re.sub(r'(ps: ["\'])[^\'"]*((?:\d{1,3}\.){3}\d{1,3})[^\'"]*(["\'])', r'\1节点\3', content)
        content = re.sub(r'(name: ["\'])[^\'"]*((?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,})[^\'"]*(["\'])', r'\1节点\3', content)
        content = re.sub(r'(ps: ["\'])[^\'"]*((?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,})[^\'"]*(["\'])', r'\1节点\3', content)
        
        # 7. 处理带有速度标识的节点名称（例如：5.8MB/s）
        content = re.sub(r'(name: ["\'])[^"\']*\d+\.?\d*\s*[KMG]B\/s[^"\']*(["\'])', r'\1节点\2', content)
        content = re.sub(r'(ps: ["\'])[^"\']*\d+\.?\d*\s*[KMG]B\/s[^"\']*(["\'])', r'\1节点\2', content)
        
        # 最后清理任何剩余的"国内"文本
        content = re.sub(r'国内\s+', '', content)
        content = re.sub(r'\s+国内', '', content)
        content = re.sub(r'挪国内', '挪威', content)
        
        # 清理结果中可能出现的多个空格
        content = re.sub(r'(name: ["\']\s*)(节点)(\s*["\'])', r'\1节点\3', content)
        content = re.sub(r'(ps: ["\']\s*)(节点)(\s*["\'])', r'\1节点\3', content)
        
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