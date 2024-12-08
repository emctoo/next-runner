use std::{collections::HashMap, error::Error, future::pending};
use tracing::{info, Level};
use zbus::{connection, interface, zvariant};
use std::fs::File;

struct Runner {
    count: u64,
}

#[interface(name = "org.kde.krunner1")]
impl Runner {
    fn match_(&mut self, query: &str) -> Vec<(String, String, String, i32, f64, HashMap<String, zvariant::Value>)> {
        info!("Received query: {}", query);
        let mut results = Vec::new();

        if query.starts_with("run") {
            let mut props = HashMap::new();
            props.insert(
                "subtext".to_string(), 
                zvariant::Value::from("Execute command")
            );
            props.insert(
                "actions".to_string(),
                zvariant::Value::from(vec!["start".to_string()])
            );

            results.push((
                "run-command".to_string(),
                "Run Command".to_string(),
                "system-run".to_string(),
                100,
                1.0,
                props,
            ));
            info!("Added run command match");
        }

        info!("Returning {} matches", results.len());
        results
    }

    fn actions(&mut self) -> Vec<(String, String, String)> {
        info!("Actions requested");
        vec![(
            "start".to_string(),
            "Start".to_string(),
            "media-playback-start".to_string(),
        )]
    }

    fn run(&mut self, match_id: &str, action_id: &str) {
        info!("Run called with match_id: {}, action_id: {}", match_id, action_id);
        self.count += 1;
        info!("Execution count: {}", self.count);
    }

    fn teardown(&mut self) {
        info!("Teardown called");
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let file = File::create("/tmp/next-runner.log")?;
    
    tracing_subscriber::fmt()
        .with_writer(file)
        .with_target(false)
        .with_ansi(false)
        .with_level(true)
        .with_thread_ids(true)
        .with_line_number(true)
        .with_file(true)
        .with_max_level(Level::INFO)
        .init();

    info!("Starting KRunner plugin");
    
    let runner = Runner { count: 0 };
    let _conn = connection::Builder::session()?
        .name("xyz.simple-is-better.next")?
        .serve_at("/next", runner)?
        .build()
        .await?;

    info!("DBus service registered");
    pending::<()>().await;
    Ok(())
}
