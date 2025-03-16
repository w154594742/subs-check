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
                return "\"国家\""
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
        
        # ***** 直接处理所有节点名称 *****
        # 使用正则表达式查找YAML文件中的所有name字段和ps字段
        lines = content.split('\n')
        for i in range(len(lines)):
            line = lines[i]
            
            # 处理name字段
            if re.match(r'\s*name:\s*["\']', line):
                # 使用通用替换方法，将所有name字段的值替换为"节点"
                if "权威商" in line or "狸床床" in line or "CloudFlare" in line or "cloudflare" in line:
                    quote_type = "'" if "'" in line else "\""
                    lines[i] = re.sub(r'name:\s*["\'].*?["\']', f'name: {quote_type}节点{quote_type}', line)
                # 如果是普通节点名称，也进行简化
                elif len(line) > 15:  # 避免替换那些可能已经是简单名称的节点
                    quote_type = "'" if "'" in line else "\""
                    lines[i] = re.sub(r'name:\s*["\'].*?["\']', f'name: {quote_type}节点{quote_type}', line)
            
            # 处理ps字段
            if re.match(r'\s*ps:\s*["\']', line):
                # 使用通用替换方法，将所有ps字段的值替换为"节点"
                if "权威商" in line or "狸床床" in line or "CloudFlare" in line or "cloudflare" in line:
                    quote_type = "'" if "'" in line else "\""
                    lines[i] = re.sub(r'ps:\s*["\'].*?["\']', f'ps: {quote_type}节点{quote_type}', line)
                # 如果是普通节点名称，也进行简化
                elif len(line) > 15:  # 避免替换那些可能已经是简单名称的节点
                    quote_type = "'" if "'" in line else "\""
                    lines[i] = re.sub(r'ps:\s*["\'].*?["\']', f'ps: {quote_type}节点{quote_type}', line)
        
        content = '\n'.join(lines)
        
        # 8. 最后清理剩余的特殊字符和国内标识
        content = re.sub(r'国内\s+', '', content)
        content = re.sub(r'\s+国内', '', content)
        content = re.sub(r'挪国内', '挪威', content)
        
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