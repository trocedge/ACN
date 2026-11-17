use leptos::prelude::*;
use serde::Deserialize;
use std::collections::{HashMap, HashSet};

const STORAGE_KEY: &str = "acn:favorites";

#[derive(Clone, Debug, Deserialize, PartialEq, Eq)]
pub struct GithubUser {
    pub login: String,
    pub avatar_url: String,
    pub profile_url: String,
}

#[derive(Clone, Copy)]
pub struct FavoritesContext {
    pub user: RwSignal<Option<GithubUser>>,
    pub loaded: RwSignal<bool>,
    pub counts: RwSignal<HashMap<String, u64>>,
    pub starred: RwSignal<HashSet<String>>,
    pending: RwSignal<HashSet<String>>,
    pub error: RwSignal<Option<String>>,
}

impl FavoritesContext {
    pub fn new() -> Self {
        let starred = read_stored();
        let counts = starred
            .iter()
            .map(|key| (key.clone(), 1u64))
            .collect::<HashMap<_, _>>();
        Self {
            user: RwSignal::new(None),
            loaded: RwSignal::new(true),
            counts: RwSignal::new(counts),
            starred: RwSignal::new(starred),
            pending: RwSignal::new(HashSet::new()),
            error: RwSignal::new(None),
        }
    }

    pub fn load(self) {
        self.loaded.set(true);
    }

    pub fn count(self, conference_key: &str) -> u64 {
        if self
            .starred
            .with_untracked(|starred| starred.contains(conference_key))
        {
            1
        } else {
            0
        }
    }

    pub fn is_pending(self, _conference_key: &str) -> bool {
        false
    }

    pub fn toggle(self, conference_key: String) {
        let was_starred = self
            .starred
            .with_untracked(|starred| starred.contains(&conference_key));
        if was_starred {
            self.starred.update(|starred| {
                starred.remove(&conference_key);
            });
            self.counts
                .update(|counts| _ = counts.insert(conference_key.clone(), 0));
        } else {
            self.starred.update(|starred| {
                starred.insert(conference_key.clone());
            });
            self.counts
                .update(|counts| _ = counts.insert(conference_key.clone(), 1));
        }
        persist(&self.starred.get_untracked());
    }

    pub fn logout(self) {
        // 本地收藏无登录态，保留空实现以兼容尚未清理的引用。
    }
}

// 已移除 GitHub 登录后端；保留函数签名以兼容尚未清理的组件引用。
pub fn start_github_login() {}

pub(crate) fn api_url(path: &str) -> String {
    let base = option_env!("CCFDDL_API_BASE")
        .unwrap_or_default()
        .trim_end_matches('/');
    format!("{base}{path}")
}

fn read_stored() -> HashSet<String> {
    let stored = web_sys::window()
        .and_then(|window| window.local_storage().ok().flatten())
        .and_then(|storage| storage.get_item(STORAGE_KEY).ok().flatten())
        .unwrap_or_default();
    serde_json::from_str::<Vec<String>>(&stored)
        .unwrap_or_default()
        .into_iter()
        .collect()
}

fn persist(starred: &HashSet<String>) {
    let list: Vec<String> = starred.iter().cloned().collect();
    let Ok(json) = serde_json::to_string(&list) else {
        return;
    };
    if let Some(storage) = web_sys::window().and_then(|window| window.local_storage().ok().flatten())
    {
        let _ = storage.set_item(STORAGE_KEY, &json);
    }
}
