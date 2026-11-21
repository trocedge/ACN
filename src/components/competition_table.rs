//! 首页竞赛列表：搜索、分类筛选、收藏、截止倒计时。

use crate::components::competition::*;
use crate::components::countdown::use_interval;
use crate::components::favorites::FavoritesContext;
use chrono::{Duration, Utc};
use leptos::prelude::*;
use thaw::{Icon, Tag};

const PLAIN_TAG: &str = "plain-tag";

#[component]
pub fn CompetitionTable() -> impl IntoView {
    let favorites = expect_context::<FavoritesContext>();

    let items = RwSignal::new(None::<CompetitionData>);
    let types = RwSignal::new(Vec::<CompetitionType>::new());
    let loading = RwSignal::new(true);
    let load_error = RwSignal::new(None::<String>);
    let load_attempt = RwSignal::new(0u32);

    Effect::new(move |_| {
        _ = load_attempt.get();
        load_competition_data(items, types, loading, load_error);
    });

    // 倒计时按天显示，每分钟刷新一次足够
    let now = RwSignal::new(Utc::now());
    use_interval(60_000, move || now.set(Utc::now()));

    let search = RwSignal::new(String::new());
    let selected_subs = RwSignal::new(std::collections::HashSet::<String>::new());
    let favorites_only = RwSignal::new(false);

    let filtered = Memo::new(move |_| {
        let keyword = search.get().trim().to_lowercase();
        let subs = selected_subs.get();
        let only_liked = favorites_only.get();
        let starred = favorites.starred.get();
        let mut list = items
            .get()
            .map(|data| data.items)
            .unwrap_or_default()
            .into_iter()
            .filter(|item| {
                if !keyword.is_empty() {
                    let haystack = format!("{} {} {}", item.title, item.category, item.seq);
                    if !haystack.to_lowercase().contains(&keyword) {
                        return false;
                    }
                }
                if !subs.is_empty() && !subs.contains(&item.sub) {
                    return false;
                }
                if only_liked && !starred.contains(&competition_key(item)) {
                    return false;
                }
                true
            })
            .collect::<Vec<_>>();
        sort_competitions(&mut list, now.get());
        list
    });

    let total_count = Memo::new(move |_| items.get().map(|data| data.items.len()).unwrap_or(0));

    view! {
        <section class="competition-main">
            <div class="competition-toolbar">
                <input
                    class="competition-search"
                    type="search"
                    placeholder="搜索竞赛名称 / 分类 / 序号"
                    prop:value=move || search.get()
                    on:input=move |event| search.set(event_target_value(&event))
                />
                <button
                    type="button"
                    class="competition-fav-toggle"
                    class:is-active=move || favorites_only.get()
                    on:click=move |_| favorites_only.update(|value| *value = !*value)
                >
                    "★ 只看收藏"
                </button>
            </div>
            <div class="competition-filters">
                <button
                    type="button"
                    class="competition-filter-tag"
                    class:is-active=move || selected_subs.get().is_empty()
                    on:click=move |_| selected_subs.set(std::collections::HashSet::new())
                >
                    "全部"
                </button>
                {move || {
                    types
                        .get()
                        .into_iter()
                        .map(|kind| {
                            let sub = kind.sub.clone();
                            let label = kind.name.clone();
                            let active_sub = sub.clone();
                            let toggle_sub = sub.clone();
                            view! {
                                <button
                                    type="button"
                                    class="competition-filter-tag"
                                    class:is-active=move || {
                                        selected_subs.get().contains(&active_sub)
                                    }
                                    on:click=move |_| selected_subs.update(|subs| {
                                        if subs.contains(&toggle_sub) {
                                            subs.remove(&toggle_sub);
                                        } else {
                                            subs.insert(toggle_sub.clone());
                                        }
                                    })
                                >
                                    {label}
                                </button>
                            }
                        })
                        .collect_view()
                }}
            </div>

            {move || {
                if loading.get() {
                    view! { <div class="competition-status">"正在加载竞赛数据…"</div> }
                        .into_any()
                } else if let Some(message) = load_error.get() {
                    view! {
                        <div class="competition-status competition-status-error">
                            <p>{format!("竞赛数据加载失败：{message}")}</p>
                            <button
                                type="button"
                                class="competition-retry"
                                on:click=move |_| load_attempt.update(|n| *n += 1)
                            >
                                "重试"
                            </button>
                        </div>
                    }
                    .into_any()
                } else {
                    view! {
                        <div class="competition-meta">
                            {move || {
                                let shown = filtered.get().len();
                                format!("共 {shown} / {} 项", total_count.get())
                            }}
                            <a
                                class="competition-directory-link"
                                href=format!("{}/competition/", crate::SITE_BASE_PATH)
                            >
                                "查看白名单竞赛大全 →"
                            </a>
                        </div>
                        <div class="competition-list">
                            {move || {
                                let list = filtered.get();
                                if list.is_empty() {
                                    vec![
                                        view! {
                                            <div class="competition-status">
                                                "没有匹配的竞赛，换个关键词或分类试试"
                                            </div>
                                        }
                                        .into_any(),
                                    ]
                                } else {
                                    list.into_iter()
                                        .map(|item| {
                                            let key = competition_key(&item);
                                            let is_liked = Signal::derive(move || {
                                                favorites
                                                    .starred
                                                    .get()
                                                    .contains(&key)
                                            });
                                            view! {
                                                <CompetitionCard item now is_liked />
                                            }
                                        })
                                        .collect::<Vec<_>>()
                                        .into_iter()
                                        .map(|card| card.into_any())
                                        .collect()
                                }
                            }}
                        </div>
                    }
                    .into_any()
                }
            }}
        </section>
    }
}

#[component]
fn CompetitionCard(
    item: CompetitionItem,
    now: RwSignal<chrono::DateTime<Utc>>,
    is_liked: Signal<bool>,
) -> impl IntoView {
    let favorites = expect_context::<FavoritesContext>();
    let detail_url = competition_detail_path(&item);
    let deadline = parse_deadline(&item);
    let site = item.site.clone();

    let deadline_view = move || {
        match deadline {
            Some(time) => {
                let date_label = time
                    .with_timezone(&chrono::FixedOffset::east_opt(8).unwrap())
                    .format("%Y-%m-%d %H:%M")
                    .to_string();
                let remaining = time - now.get();
                if remaining > Duration::zero() {
                    let days = remaining.num_days();
                    view! {
                        <span class="comp-deadline-date">{date_label}</span>
                        <span class="comp-countdown comp-countdown-open">
                            {format!("剩 {days} 天")}
                        </span>
                    }
                    .into_any()
                } else {
                    view! {
                        <span class="comp-deadline-date">{date_label}</span>
                        <span class="comp-countdown comp-countdown-closed">"已截止"</span>
                    }
                    .into_any()
                }
            }
            None => view! {
                <span class="comp-deadline-date comp-deadline-tbd">"报名待公布"</span>
            }
            .into_any(),
        }
    };

    let toggle_key = competition_key(&item);
    view! {
        <div class="comp-card">
            <div class="conference-card-heading">
                <a class="conf-title comp-title" href=detail_url>
                    {item.title.clone()}
                </a>
                {site
                    .as_ref()
                    .map(|url| {
                        let href = url.clone();
                        view! {
                            <a
                                class="conference-card-website"
                                href=href
                                target="_blank"
                                rel="noopener"
                                aria-label="访问竞赛官网"
                                title="访问竞赛官网"
                            >
                                <Icon icon=icondata::FiExternalLink />
                            </a>
                        }
                    })}
                <button
                    type="button"
                    class=move || {
                        if is_liked.get() {
                            "conference-like-toggle is-liked"
                        } else {
                            "conference-like-toggle"
                        }
                    }
                    aria-label=move || if is_liked.get() { "取消收藏" } else { "收藏" }
                    on:click=move |_| favorites.toggle(toggle_key.clone())
                >
                    <Icon icon=icondata::BsStar />
                </button>
            </div>
            <div class="comp-card-row">
                <span class="comp-seq">#{format!("{:02}", item.seq)}</span>
                <Tag class=PLAIN_TAG>{item.category.clone()}</Tag>
                <span class="comp-deadline">{deadline_view}</span>
            </div>
        </div>
    }
}
