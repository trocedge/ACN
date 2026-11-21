use crate::components::competition_table::CompetitionTable;
use crate::components::favorites::FavoritesContext;
use crate::components::header::Header;
use leptos::prelude::*;

use thaw::*;

/// Default Home Page
#[component]
pub fn Home() -> impl IntoView {
    let favorites = FavoritesContext::new();
    provide_context(favorites);
    favorites.load();

    view! {
        <ConfigProvider theme=crate::components::conference_controls::conference_theme()>
            <div class="home">
                <Header />
                <CompetitionTable />
            </div>
        </ConfigProvider>
    }
}
