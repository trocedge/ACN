use leptos::prelude::*;

use crate::SITE_BASE_PATH;
use crate::components::gitbutton::GitButton;

#[component]
pub fn Header(
    use_english: RwSignal<bool>,
    show_favorites_timeline: RwSignal<bool>,
    show_batch_subscription: RwSignal<bool>,
    show_email_reminders: RwSignal<bool>,
    table_view: bool,
) -> impl IntoView {
    view! {
        <section>
            <div class="header-main">
                <a href=format!("{SITE_BASE_PATH}/") class="title">
                    <span class="title-normal">"CCFDDL"</span>
                    <span class="title-normal">"\u{00a0}Open\u{00a0}"</span>
                    <span class="title-accent">"Deadlines"</span>
                </a>
                <div class="header-github">
                    <GitButton />
                </div>
            </div>
            <div class="el-row subtitle">
                "Worldwide Conference Deadline Countdowns."
            </div>
            <div class="el-row subtitle">
                "*Disclaimer: The data is agentically collected and for reference purposes only."
            </div>
        </section>
    }
}
