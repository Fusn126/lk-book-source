# 规则语法速查

这里只记录书源编写时的决策方法和常见形式。具体解析差异以用户的 Legado 版本与规则教程为准。

## 1. 先选择最简单的解析器

| 响应 | 首选 | 何时升级 |
|---|---|---|
| HTML/XML | 默认/CSS 规则 | 需要复杂层级时用 XPath；需要转换时加短 JS |
| JSON | JSONPath | 字段结构动态、要合并数组或生成 URL 时加 JS |
| 稳定纯文本 | 正则 | 不要用正则解析通用 HTML |
| 动态页面 | 找 XHR/API | 仅当内容确实只能通过 WebView 获得时使用 WebView |

列表规则先定位集合，字段规则再相对当前元素提取。能在声明式规则中完成的，不要改写成整段 JavaScript。

## 2. URL 规则

常用变量：

- `{{key}}`：搜索词。
- `{{page}}` 或 JS 变量 `page`：页码；确认站点从 0 还是 1 开始。
- `baseUrl`：当前阶段的基础地址/结果地址，具体语义依上下文。
- `book`、`source`：书籍和书源对象；只访问已知存在的属性。

常见形态：

```text
/search?q={{key}}&page={{page}}
```

复杂请求可由前置 JS 生成 `URL + ',' + JSON.stringify(option)`；`option` 常含 `method`、`body`、`headers`。例如：

```javascript
@js:
var url = baseUrl + "/api/search";
var option = {
  method: "POST",
  body: JSON.stringify({q: "{{key}}", page: page}),
  headers: {"Content-Type": "application/json"}
};
java.put("url", String(url + "," + JSON.stringify(option)));
```

不同版本对 `@js:`、`<js>...</js>` 和返回值的处理可能不同；修复已有源时保持其已工作的风格，新建源则在目标版本中实测。

## 3. 默认/CSS 规则

真实样例中的典型形式：

```text
div.col-lg-3
.card-title@a@text
.card-title@a@href
.product-gallery@img@src
```

原则：

- `bookList` 先选每一本书的共同容器。
- 字段规则尽量相对于当前容器。
- `@text`、`@html`、`@href`、`@src` 分清；正文保留段落结构时通常取 HTML。
- 索引规则（如 `.1`、`.-1`）易受页面改版影响，只在没有稳定标识时使用并记录假设。

## 4. JSONPath

真实样例中的典型字段：

```text
items
$.title
$..novelId
authors..name
```

先确认当前 `result` 是整个响应、数组元素还是经前置 JS 处理后的对象。混用绝对与相对路径前，要验证每条字段是否仍在同一上下文中。

## 5. 组合、替换与备选

常见用途：

- `{{ ... }}`：嵌入规则或表达式并拼接文本。
- `##正则##替换`：清理/替换结果；JSON 中反斜杠需再次转义。
- `||`：备选规则，仅在两个结构确实互斥时使用。
- `&&`：组合多个结果；验证结果顺序与空值行为。

不要用宽泛替换删除脚本、广告时误删正文。每个正则应在保存的响应样本上测试。

## 6. JavaScript

可用场景：

- POST/PUT 请求、动态请求头或 URL。
- API 响应重组、卷标插入、多语言切换。
- 登录 token 读写、源变量/书籍变量。
- 声明式规则无法表达的短转换。

约束：

1. 明确输入：`result` 当前是什么类型和内容。
2. 明确输出：最后一个表达式或显式保存的变量必须是下一阶段期望的字符串/对象/数组。
3. 不吞异常；至少给出可区分的失败提示。
4. 复用逻辑才放 `jsLib`，并保持函数无隐藏网络副作用。
5. 不硬编码真实 Cookie、Authorization、账号、密码、签名密钥。
6. JS 放进 JSON 字符串后，重新检查引号、换行和反斜杠转义。

## 7. 登录与状态

- Web 登录：`loginUrl` 指向登录页，使用 Cookie 容器读取站点会话。
- 自定义登录：`loginUi` 定义字段，登录 JS 从运行时读取并将授权头保存到书源登录状态。
- 每个需要登录的阶段都应识别“未登录/会话过期”响应，不能把它解析成空列表或正文。
- 报告中只说明 token 是否存在/过期，禁止输出实际 token、Cookie 或密码。

## 8. 发现配置

简单发现可写分类 JSON；动态分类可用 JS 生成 JSON 数组。每项通常包含：

```json
{"title":"最新","url":"/list/{{page}}","style":{"layout_flexGrow":1,"layout_flexBasisPercent":0.25}}
```

标题项可使用空 URL；可点击项必须验证分页。动态发现中的网络请求会增加打开速度和失败点，应缓存/减少不必要请求。

## 9. 转义检查

书源是“JSON 包着规则，规则可能再包 JavaScript/正则/JSON”。逐层检查：

1. 外层 JSON 能解析。
2. `header`、`loginUi`、静态 `exploreUrl` 若声称是 JSON，其字符串内容也能解析。
3. JavaScript 字符串中的 `\n`、引号、模板字符串保持预期。
4. 正则中的反斜杠在 JSON 层已正确加倍。
5. 生成请求选项时，嵌套 JSON 只序列化一次，不把对象误传成 `[object Object]`。
