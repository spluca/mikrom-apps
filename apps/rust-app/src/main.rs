use axum::{routing::get, response::Json, Router};
use serde::Serialize;
use std::net::SocketAddr;
use chrono::Utc;

#[derive(Serialize)]
struct StatusResponse {
    message: String,
    timestamp: String,
    host: String,
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/", get(handler))
        .route("/health", get(health_check));

    let port = std::env::var("PORT").unwrap_or_else(|_| "8080".to_string());
    let addr: SocketAddr = format!("0.0.0.0:{}", port).parse().unwrap();

    println!("Starting Rust (Axum) server on {}", addr);
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

async fn handler() -> Json<StatusResponse> {
    let hostname = gethostname::gethostname()
        .to_string_lossy()
        .into_owned();

    Json(StatusResponse {
        message: "Hello from Rust (Axum) — Packaged for Firecracker via Cloud Native Buildpacks"
            .to_string(),
        timestamp: Utc::now().to_rfc3339(),
        host: hostname,
    })
}

async fn health_check() -> &'static str {
    "OK"
}
