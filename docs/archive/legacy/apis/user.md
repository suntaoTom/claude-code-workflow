# User 接口

> ⚠️ 本文件由 `tools/gen_api_md.py` 从 OpenAPI 自动生成, **不要手改**。
> 接口变更 → 替换 `docs/apis/openapi/*.json` → 重新执行脚本。

- **协议源**: `docs/apis/openapi/openapi.json`
- **接口数量**: 3
- **PRD 引用方式**: `@api docs/apis/user.md#<operation-id>`

## 接口列表

| Operation | Method | Path | 摘要 |
|-----------|--------|------|------|
| [searchusers](#searchusers) | GET | `/api/users/search` | 按筛选条件搜索用户 |
| [getuserbyid](#getuserbyid) | GET | `/api/users/{id}` | 按 id 查询用户详情 |
| [exportusers](#exportusers) | POST | `/api/users/export` | 导出符合筛选条件的用户为 Excel |

---

## searchusers

- **接口**: `GET /api/users/search`
- **摘要**: 按筛选条件搜索用户

**请求参数**:

| 位置 | 名称 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| query | `phone` | string |  | 手机号 (模糊匹配) |
| query | `status` | enum[enabled, disabled] |  | 状态筛选 |
| query | `page` | integer |  |  |
| query | `pageSize` | integer |  |  |

**响应**: [UserListResponse](#schema-userlistresponse)

### H5 旧实现

_(待补: H5 页面/路由 + 调用时机)_

### Flutter 迁移备注

_(待补: 错误码映射 / 鉴权要求 / 缓存策略 / 与其他接口的调用顺序)_

## getuserbyid

- **接口**: `GET /api/users/{id}`
- **摘要**: 按 id 查询用户详情

**请求参数**:

| 位置 | 名称 | 类型 | 必填 | 描述 |
|------|------|------|------|------|
| path | `id` | string | ✓ |  |

**响应**: [User](#schema-user)

### H5 旧实现

_(待补: H5 页面/路由 + 调用时机)_

### Flutter 迁移备注

_(待补: 错误码映射 / 鉴权要求 / 缓存策略 / 与其他接口的调用顺序)_

## exportusers

- **接口**: `POST /api/users/export`
- **摘要**: 导出符合筛选条件的用户为 Excel

**请求体**:

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `phone` | string |  |  |
| `status` | enum[enabled, disabled] |  |  |

**响应**: `string(binary)`

### H5 旧实现

_(待补: H5 页面/路由 + 调用时机)_

### Flutter 迁移备注

_(待补: 错误码映射 / 鉴权要求 / 缓存策略 / 与其他接口的调用顺序)_

---

## 数据结构 (Schemas)

### schema-user

`User`

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `id` | string | ✓ | 用户唯一 id |
| `phone` | string | ✓ | 11 位手机号 |
| `nickname` | string |  | 昵称 |
| `status` | enum[enabled, disabled] | ✓ | 账号状态 |
| `createdAt` | string(date-time) |  |  |

### schema-userlistresponse

`UserListResponse`

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `list` | array<[User](#schema-user)> | ✓ |  |
| `total` | integer | ✓ |  |
| `page` | integer |  |  |
| `pageSize` | integer |  |  |
