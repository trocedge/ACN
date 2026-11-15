use leptos::prelude::*;

// Modules
mod components;
mod pages;

/// Path prefix the site is served from: empty for a root domain, `/ACN` for a
/// GitHub Pages project site. Baked in at build time through `CCFDDL_BASE_PATH`.
pub const SITE_BASE_PATH: &str = match option_env!("CCFDDL_BASE_PATH") {
    Some(path) => path,
    None => "",
};

/// Absolute URL of the site root, including the base path when the site is
/// hosted under a repository sub-path.
pub fn site_base_url() -> Option<String> {
    let origin = web_sys::window()?.location().origin().ok()?;
    Some(format!("{origin}{SITE_BASE_PATH}"))
}

// Top-Level pages
use crate::pages::home::Home;

#[component]
pub fn App() -> impl IntoView {
    view! { <Home /> }
}

pub use components::directory_controls::DirectoryControls;
