package proxies

import (
	"fmt"
)

func DeduplicateProxies(proxies []map[string]any) []map[string]any {
	seen := make(map[string]map[string]any)

	for _, proxy := range proxies {
		server, _ := proxy["server"].(string)
		port, _ := proxy["port"].(int)
		if server == "" {
			continue
		}

		key := fmt.Sprintf("%s:%v", server, port)
		seen[key] = proxy
	}

	result := make([]map[string]any, 0, len(seen))
	for _, proxy := range seen {
		result = append(result, proxy)
	}

	// 重命名节点，确保节点名称唯一

	nameMap := make(map[string]int)
	
	for i, proxy := range result {
		name, ok := proxy["name"].(string)
		if !ok || name == "" {
			name = fmt.Sprintf("节点_%d", i)
			result[i]["name"] = name
		}
		
		if count, exists := nameMap[name]; exists {
			newName := fmt.Sprintf("%s_%d", name, count+1)
			result[i]["name"] = newName
			nameMap[name] = count + 1
		} else {
			nameMap[name] = 0
		}
	}

	return result
}
