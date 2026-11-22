use leptos::prelude::*;

use crate::SITE_BASE_PATH;
use crate::components::gitbutton::GitButton;

#[component]
pub fn Header() -> impl IntoView {
    view! {
        <section>
            <div class="header-main">
                <a href=format!("{SITE_BASE_PATH}/") class="title">
                    <span class="title-normal">"ACN"</span>
                    <span class="title-normal">"\u{00a0}学科竞赛"</span>
                    <span class="title-accent">"资讯"</span>
                </a>
                <div class="header-github">
                    <GitButton />
                </div>
            </div>
            <div class="el-row subtitle">
                "大学生竞赛白名单 · 报名时间 · 官方入口"
            </div>
            <div class="el-row subtitle">
                "*数据以官方公告为准，仅供参考"
            </div>
        </section>
    }
}
