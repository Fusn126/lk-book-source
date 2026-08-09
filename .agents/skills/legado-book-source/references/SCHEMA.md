# 常用字段结构

本表用于建模和审查，不替代具体 Legado 版本的实际编辑器字段。未知字段应保留而不是擅自删除。

## 顶层字段

| 字段 | 常见类型 | 作用与要求 |
|---|---|---|
| `bookSourceName` | string | 显示名称；必须非空 |
| `bookSourceGroup` | string | 分组，可选 |
| `bookSourceType` | number | `0` 文本、`1` 音频、`2` 图片、`3` 文件 |
| `bookSourceUrl` | string | 源标识与相对地址基准；通常为 `http(s)` URL |
| `bookSourceComment` | string | 使用说明、登录要求、作者与许可信息 |
| `enabled` | boolean | 是否启用 |
| `enabledExplore` | boolean | 是否启用发现 |
| `enabledCookieJar` | boolean | 是否使用 Cookie 容器 |
| `header` | string/object | 通用请求头；可为 JSON 文本或返回 JSON 的 JS 规则 |
| `searchUrl` | string | 搜索 URL 规则，可使用 `key`、`page` |
| `exploreUrl` | string | 发现配置；可为分类 JSON 或 JS 生成的 JSON |
| `loginUrl` | string | Web 登录页、登录 URL 规则或执行登录的 JS |
| `loginUi` | string | 登录表单 JSON；字段名应与登录 JS 读取名称一致 |
| `loginCheckJs` | string | 登录状态检测逻辑 |
| `bookUrlPattern` | string | 用于识别详情 URL 的模式 |
| `jsLib` | string | 多处复用的 JavaScript 函数；不要放仅调用一次的大段逻辑 |
| `variableComment` | string | 源变量/书籍变量的用户说明 |
| `ruleSearch` | object | 搜索结果列表及字段规则 |
| `ruleExplore` | object | 发现结果列表及字段规则 |
| `ruleBookInfo` | object | 详情字段规则与初始化逻辑 |
| `ruleToc` | object | 目录列表及章节字段规则 |
| `ruleContent` | object | 正文、下一页、替换与媒体规则 |
| `lastUpdateTime` | number | 毫秒时间戳；生成时使用当前时间 |
| `customOrder`, `weight`, `respondTime` | number | 排序、权重或兼容字段；从模板/已有源保留合理默认值 |

## `ruleSearch` / `ruleExplore`

| 字段 | 作用 |
|---|---|
| `bookList` | 先切分结果列表，是其他字段的上下文 |
| `name` | 书名；建议必填 |
| `bookUrl` | 详情地址或唯一详情标识；建议必填 |
| `author` | 作者 |
| `kind` | 分类/状态标签 |
| `coverUrl` | 封面地址 |
| `intro` | 简介 |
| `wordCount` | 字数或规模 |
| `lastChapter` | 最新章节 |
| `updateTime` | 更新时间 |
| `checkKeyWord` | 调试用已知关键词 |

发现规则可为空：当发现 URL 直接进入详情或其数据结构与搜索规则共用时，应说明复用方式；不要为了消除警告伪造选择器。

## `ruleBookInfo`

| 字段 | 作用 |
|---|---|
| `init` | 详情规则执行前初始化/改写响应或保存变量 |
| `name`, `author`, `kind` | 基本元数据 |
| `coverUrl`, `intro` | 封面与简介 |
| `wordCount`, `lastChapter`, `updateTime` | 状态信息 |
| `tocUrl` | 目录请求地址；目录与详情同页时可省略 |
| `canReName` | 是否允许详情名称覆盖列表名称 |
| `downloadUrls` | 文件类书源的下载地址 |

## `ruleToc`

| 字段 | 作用与检查点 |
|---|---|
| `chapterList` | 目录列表；必须返回按阅读顺序排列的项目 |
| `chapterName` | 章节名；在当前目录项上下文中抽取 |
| `chapterUrl` | 章节地址或 ID；必须和名称一一对应 |
| `updateTime` | 章节更新时间 |
| `isVolume` | 卷标判断；卷标不应被当作正文章节 |
| `isVip` | 付费状态标记；不得用于绕过付费限制 |
| `isPay` | 已购买状态，仅反映用户授权状态 |
| `nextTocUrl` | 目录下一页 |

## `ruleContent`

| 字段 | 作用与检查点 |
|---|---|
| `content` | 文本正文或媒体地址；必须非空 |
| `nextContentUrl` | 正文下一页；检查终止条件与去重 |
| `webJs` | WebView 场景脚本，仅在普通请求无法获得授权内容时使用 |
| `sourceRegex` | 源文本替换/清理规则 |
| `replaceRegex` | 阅读显示前替换；避免误删正文 |
| `imageStyle`, `imageDecode` | 图片书源样式与解码 |
| `payAction` | 购买动作，只能操作用户明确授权的账户与内容 |

## 最小可用骨架

最小文本书源通常需要：

- 顶层：`bookSourceName`、`bookSourceType`、`bookSourceUrl`、`searchUrl`。
- 搜索：`bookList`、`name`、`bookUrl`。
- 详情：至少能得到 `name` 或沿用列表信息，并确定目录响应。
- 目录：`chapterList`、`chapterName`、`chapterUrl`。
- 正文：`content`。

字段可为空不代表流程可缺失。每个阶段都必须用真实响应验证数据上下文。
