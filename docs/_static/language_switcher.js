// Language Switcher for ToolUniverse Documentation
(function() {
    'use strict';
    
    // 检测当前语言
    function detectCurrentLanguage() {
        const path = window.location.pathname;
        if (path.includes('/zh-CN/') || path.includes('/zh_CN/')) {
            return 'zh_CN';
        }
        // 根路径或 /en/ 路径都视为英文
        return 'en';
    }
    
    // 切换语言
    function switchLanguage(newLang) {
        const currentPath = window.location.pathname;
        let newPath;
        
        // 提取当前文件路径(相对于语言目录)
        let relativeFile = 'index.html';
        
        if (currentPath.includes('/en/')) {
            const enIndex = currentPath.indexOf('/en/');
            relativeFile = currentPath.substring(enIndex + '/en/'.length);
        } else if (currentPath.includes('/zh-CN/')) {
            const zhIndex = currentPath.indexOf('/zh-CN/');
            relativeFile = currentPath.substring(zhIndex + '/zh-CN/'.length);
        } else if (currentPath.includes('/zh_CN/')) {
            const zhIndex = currentPath.indexOf('/zh_CN/');
            relativeFile = currentPath.substring(zhIndex + '/zh_CN/'.length);
        } else if (currentPath !== '/') {
            // 处理根路径的其他页面(如果英文文档在根目录)
            relativeFile = currentPath.substring(1); // 移除开头的 /
        }
        
        // 确保有文件名
        if (!relativeFile || relativeFile.endsWith('/')) {
            relativeFile += 'index.html';
        }
        
        // 获取基础URL(协议 + 主机 + 端口)
        const baseUrl = window.location.origin;
        
        if (newLang === 'zh_CN') {
            // 切换到中文
            if (currentPath.includes('/zh-CN/') || currentPath.includes('/zh_CN/')) {
                return; // 已经是中文
            }
            // 构建中文URL: http://host:port/zh-CN/file.html
            newPath = baseUrl + '/zh-CN/' + relativeFile;
        } else {
            // 切换到英文
            if (currentPath.includes('/en/')) {
                return; // 已经是英文
            }
            // 如果 DOC_EN_AS_ROOT=true,则使用根路径,否则使用 /en/ 路径
            // 这里我们统一使用 /en/ 路径以保持一致性
            newPath = baseUrl + '/en/' + relativeFile;
        }
        
        // 跳转到新语言
        window.location.href = newPath;
    }
    
    // 创建语言切换器
    function createLanguageSwitcher() {
        const currentLang = detectCurrentLanguage();
        
        const switcher = document.createElement('div');
        switcher.className = 'language-switcher';
        switcher.innerHTML = `
            <select id="lang-select" aria-label="Choose language">
                <option value="en" ${currentLang === 'en' ? 'selected' : ''}>🇬🇧 English</option>
                <option value="zh_CN" ${currentLang === 'zh_CN' ? 'selected' : ''}>🇨🇳 简体中文</option>
            </select>
        `;
        
        document.body.appendChild(switcher);
        
        // 添加事件监听
        const select = document.getElementById('lang-select');
        select.addEventListener('change', function() {
            switchLanguage(this.value);
        });
    }
    
    // 页面加载完成后创建切换器
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createLanguageSwitcher);
    } else {
        createLanguageSwitcher();
    }
})();
