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
        
        # ***** 处理所有节点名称并确保唯一性 *****
        lines = content.split('\n')
        
        # 跟踪已使用的节点名称
        used_names = {}
        name_counter = {}
        
        # 第一遍：收集所有名称并计数
        for line in lines:
            # 匹配name和ps字段的值
            name_match = re.search(r'\s*name:\s*["\'](.+?)["\']', line)
            ps_match = re.search(r'\s*ps:\s*["\'](.+?)["\']', line)
            
            if name_match:
                name = name_match.group(1)
                name_counter[name] = name_counter.get(name, 0) + 1
            
            if ps_match:
                ps = ps_match.group(1)
                name_counter[ps] = name_counter.get(ps, 0) + 1
        
        # 第二遍：根据计数修改重复的名称
        for i in range(len(lines)):
            line = lines[i]
            
            # 处理name字段
            name_match = re.search(r'\s*name:\s*["\'](.+?)["\']', line)
            if name_match:
                name = name_match.group(1)
                quote_type = "'" if "'" in line else "\""
                
                # 先进行通用替换，对特殊名称或长名称进行简化
                if "权威商" in name or "狸床床" in name or "CloudFlare" in name or "cloudflare" in name or len(name) > 15:
                    simplified_name = "节点"
                else:
                    simplified_name = name
                
                # 然后处理重复性
                if simplified_name in used_names:
                    used_names[simplified_name] += 1
                    new_name = f"{simplified_name}_{used_names[simplified_name]}"
                else:
                    used_names[simplified_name] = 0
                    new_name = simplified_name
                
                # 替换名称
                lines[i] = re.sub(r'name:\s*["\'].*?["\']', f'name: {quote_type}{new_name}{quote_type}', line)
            
            # 处理ps字段
            ps_match = re.search(r'\s*ps:\s*["\'](.+?)["\']', line)
            if ps_match:
                ps = ps_match.group(1)
                quote_type = "'" if "'" in line else "\""
                
                # 先进行通用替换，对特殊名称或长名称进行简化
                if "权威商" in ps or "狸床床" in ps or "CloudFlare" in ps or "cloudflare" in ps or len(ps) > 15:
                    simplified_ps = "节点"
                else:
                    simplified_ps = ps
                
                # 然后处理重复性
                if simplified_ps in used_names:
                    used_names[simplified_ps] += 1
                    new_ps = f"{simplified_ps}_{used_names[simplified_ps]}"
                else:
                    used_names[simplified_ps] = 0
                    new_ps = simplified_ps
                
                # 替换名称
                lines[i] = re.sub(r'ps:\s*["\'].*?["\']', f'ps: {quote_type}{new_ps}{quote_type}', line)
        
        content = '\n'.join(lines)
        
        # 清理剩余的特殊字符和国内标识
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