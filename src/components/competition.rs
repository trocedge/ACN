//! 竞赛白名单数据模型与拉取。
//!
//! 数据源由 scripts/build_data.py 从 competition/whitelist.yml 生成，
//! 字段校验见 scripts/validate_competition.py，可选字段未核实时不出现在 JSON 中。

use serde::Deserialize;
use wasm_bindgen_futures::spawn_local;

use leptos::prelude::{RwSignal, Set};

/// 白名单单项竞赛。deadline 等可选字段由 CI 保证「未核实则不存在」。
#[derive(Debug, Clone, Deserialize, PartialEq)]
pub struct CompetitionItem {
    pub seq: u32,
    pub title: String,
    pub sub: String,
    pub category: String,
    pub site: Option<String>,
    pub deadline: Option<String>,
    #[serde(default)]
    pub timezone: Option<String>,
    #[serde(default)]
    pub source_url: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct CompetitionData {
    pub total: u32,
    pub items: Vec<CompetitionItem>,
}

#[derive(Debug, Clone, Deserialize, PartialEq)]
pub struct CompetitionType {
    pub name: String,
    #[serde(default)]
    pub name_en: String,
    pub sub: String,
}

/// 收藏键。与旧会议收藏（会议 id）命名空间不同，互不干扰。
pub fn competition_key(item: &CompetitionItem) -> String {
    format!("competition:c{:02}", item.seq)
}

/// 详情页地址，由 scripts/generate_competition_pages.py 生成。
pub fn competition_detail_path(item: &CompetitionItem) -> String {
    format!("{}/competition/c{:02}/", crate::SITE_BASE_PATH, item.seq)
}

/// 解析北京时间截止时间。返回 None 表示数据异常，按「待公布」处理。
pub fn parse_deadline(item: &CompetitionItem) -> Option<chrono::DateTime<chrono::Utc>> {
    let deadline = item.deadline.as_deref()?;
    let naive = chrono::NaiveDateTime::parse_from_str(deadline, "%Y-%m-%dT%H:%M:%S").ok()?;
    // timezone 仅支持 Asia/Shanghai（CI 强制），固定 UTC+08:00
    let offset = chrono::FixedOffset::east_opt(8 * 3600)?;
    let local = naive.and_local_timezone(offset).single()?;
    Some(local.with_timezone(&chrono::Utc))
}

/// 排序分组：0 进行中(近→远) / 1 已截止(近→远) / 2 未公布(seq)。
fn sort_group(item: &CompetitionItem, now: chrono::DateTime<chrono::Utc>) -> u8 {
    match parse_deadline(item) {
        Some(deadline) if deadline > now => 0,
        Some(_) => 1,
        None => 2,
    }
}

/// 首页默认排序：进行中的截止日期由近到远，已截止其次，未公布按官方序号。
pub fn sort_competitions(
    items: &mut [CompetitionItem],
    now: chrono::DateTime<chrono::Utc>,
) {
    items.sort_by(|a, b| {
        sort_group(a, now)
            .cmp(&sort_group(b, now))
            .then_with(|| {
                let key = |item: &CompetitionItem| parse_deadline(item);
                match (key(a), key(b)) {
                    (Some(x), Some(y)) => x.cmp(&y),
                    _ => std::cmp::Ordering::Equal,
                }
            })
            .then_with(|| a.seq.cmp(&b.seq))
    });
}

async fn fetch_json<T: serde::de::DeserializeOwned>(path: &str) -> Result<T, String> {
    let url = format!("{}{path}", crate::site_base_url().unwrap_or_default());
    // 先常规请求，失败后带时间戳绕过缓存重试一次
    let plain = gloo_net::http::Request::get(&url).send().await;
    let fetch = |bust: bool| {
        let target = if bust {
            format!("{url}{}", if url.contains('?') { '&' } else { '?' })
        } else {
            url.clone()
        };
        gloo_net::http::Request::get(&target)
    };
    let response = match plain {
        Ok(response) if response.ok() => response,
        _ => fetch(true)
            .send()
            .await
            .map_err(|error| format!("网络请求失败: {error}"))?,
    };
    if !response.ok() {
        return Err(format!("数据加载失败: HTTP {}", response.status()));
    }
    response.json::<T>().await.map_err(|e| e.to_string())
}

pub async fn fetch_competition_data() -> Result<CompetitionData, String> {
    fetch_json("/competition/whitelist.json").await
}

pub async fn fetch_competition_types() -> Result<Vec<CompetitionType>, String> {
    fetch_json("/competition/types.json").await
}

/// 一次性拉取白名单与分类，结果写入信号。失败时写错误信息。
pub fn load_competition_data(
    data: RwSignal<Option<CompetitionData>>,
    types: RwSignal<Vec<CompetitionType>>,
    loading: RwSignal<bool>,
    error: RwSignal<Option<String>>,
) {
    spawn_local(async move {
        loading.set(true);
        error.set(None);
        let types_result = fetch_competition_types().await;
        match fetch_competition_data().await {
            Ok(result) => {
                if let Ok(loaded) = types_result {
                    types.set(loaded);
                }
                data.set(Some(result));
            }
            Err(message) => error.set(Some(message)),
        }
        loading.set(false);
    });
}
