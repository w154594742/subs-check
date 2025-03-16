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
        
        # 替换常见的中文国家/地区名称
        replacements = {
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
            'Telegram': 'Telegram',
            'trojan': 'trojan',
            'vmess': 'vmess',
            'vless': 'vless',
            'hysteria2': 'hysteria2',
            'ss': 'ss'
        }
        
        for k, v in replacements.items():
            content = content.replace(f'\\u{k}', v)
        
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