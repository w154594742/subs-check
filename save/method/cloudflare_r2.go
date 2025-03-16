package method

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"log/slog"

	"github.com/w154594742/subs-check/config"
)

const (
	maxRetries    = 3
	retryInterval = 2 * time.Second
)

// KVPayload 定义上传到R2的数据结构
type KVPayload struct {
	Filename string `json:"filename"`
	Value    string `json:"value"`
}

// R2Uploader 处理R2存储上传的结构体
type R2Uploader struct {
	client    *http.Client
	workerURL string
	token     string
}

// NewR2Uploader 创建新的R2上传器
func NewR2Uploader() *R2Uploader {
	return &R2Uploader{
		client:    &http.Client{Timeout: 30 * time.Second},
		workerURL: config.GlobalConfig.WorkerURL,
		token:     config.GlobalConfig.WorkerToken,
	}
}

// UploadToR2Storage 上传数据到R2存储的入口函数
func UploadToR2Storage(yamlData []byte, filename string) error {
	uploader := NewR2Uploader()
	return uploader.Upload(yamlData, filename)
}

// valiR2Config 验证R2配置
func ValiR2Config() error {
	if config.GlobalConfig.WorkerURL == "" {
		return fmt.Errorf("worker url未配置")
	}
	if config.GlobalConfig.WorkerToken == "" {
		return fmt.Errorf("worker token未配置")
	}
	return nil
}

// Upload 执行上传操作
func (r *R2Uploader) Upload(yamlData []byte, filename string) error {
	// 验证输入
	if err := r.validateInput(yamlData, filename); err != nil {
		return err
	}

	// 准备请求数据
	payload := KVPayload{
		Filename: filename,
		Value:    string(yamlData),
	}

	jsonData, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("JSON编码失败: %w", err)
	}

	// 执行带重试的上传
	return r.uploadWithRetry(jsonData, filename)
}

// validateInput 验证输入参数
func (r *R2Uploader) validateInput(yamlData []byte, filename string) error {
	if len(yamlData) == 0 {
		return fmt.Errorf("yaml数据为空")
	}
	if filename == "" {
		return fmt.Errorf("filename不能为空")
	}
	if r.workerURL == "" || r.token == "" {
		return fmt.Errorf("Worker配置不完整")
	}
	return nil
}

// uploadWithRetry 带重试机制的上传
func (r *R2Uploader) uploadWithRetry(jsonData []byte, filename string) error {
	var lastErr error

	for attempt := 0; attempt < maxRetries; attempt++ {
		if err := r.doUpload(jsonData); err != nil {
			lastErr = err
			slog.Error(fmt.Sprintf("R2上传失败(尝试 %d/%d) %v", attempt+1, maxRetries, err))
			time.Sleep(retryInterval)
			continue
		}
		slog.Info("R2上传成功", "filename", filename)
		return nil
	}

	return fmt.Errorf("上传失败，已重试%d次: %w", maxRetries, lastErr)
}

// doUpload 执行单次上传
func (r *R2Uploader) doUpload(jsonData []byte) error {
	// 创建请求
	req, err := r.createRequest(jsonData)
	if err != nil {
		return err
	}

	// 发送请求
	resp, err := r.client.Do(req)
	if err != nil {
		return fmt.Errorf("发送请求失败: %w", err)
	}
	defer resp.Body.Close()

	// 检查响应
	return r.checkResponse(resp)
}

// createRequest 创建HTTP请求
func (r *R2Uploader) createRequest(jsonData []byte) (*http.Request, error) {
	url := fmt.Sprintf("%s/storage?token=%s", r.workerURL, r.token)
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("创建请求失败: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	return req, nil
}

// checkResponse 检查响应结果
func (r *R2Uploader) checkResponse(resp *http.Response) error {
	if resp.StatusCode != http.StatusOK {
		body, err := io.ReadAll(resp.Body)
		if err != nil {
			return fmt.Errorf("读取响应失败(状态码: %d): %w", resp.StatusCode, err)
		}
		return fmt.Errorf("上传失败(状态码: %d): %s", resp.StatusCode, string(body))
	}
	return nil
}
